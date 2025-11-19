
from flask import Flask, render_template, request, jsonify, session
import google.generativeai as genai
import re
import os
import json
import time
import threading
from google.api_core import exceptions as api_exceptions
import tempfile


try:
    from PyPDF2 import PdfReader
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False
    print("PyPDF2 não instalado. Suporte a PDF desabilitado.")

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "chave_de_dev_trocar_no_futuro")




api_key = ""
genai.configure(api_key=api_key)
modelo = genai.GenerativeModel("gemini-2.0-flash")



CACHE_FILE = "receitas_cache.json"
PDF_FOLDER = "pdfs_upload"
if not os.path.exists(PDF_FOLDER):
    os.makedirs(PDF_FOLDER)

pdf_content = "" 


def carregar_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: return {}
    return {}

cache = carregar_cache()


contexto_base = (
    "Você é um assistente especializado em padarias, panificação e confeitaria. "
    "Você deve responder apenas sobre receitas de pães, bolos, massas, salgados e confeitaria artesanal. "
    "Nunca fale sobre outros temas como tecnologia, política, curiosidades, clima, ou qualquer outro assunto. "
    "Você pode aceitar elogios simples sobre suas receitas, mas nunca inicie ou prolongue conversas fora do tema principal. "
    "Se o usuário elogiar você diga apenas 'Obrigado! Fico feliz que tenha gostado da receita.'\n\n"
    "Se o usuário fizer uma pergunta fora desses temas, diga exatamente: "
    "'Desculpe, só falo sobre panificação e confeitaria.'\n\n"
    "Ao responder, siga estas regras:\n"
    "1. Sempre que o usuário pedir uma receita, envie apenas o modo de preparo e o nome da receita. "
    " Não liste os ingredientes, a menos que o usuário peça explicitamente (ex: 'quais são os ingredientes?' ou 'me mande os ingredientes').\n"
    "2. Se o usuário pedir os ingredientes depois, envie uma lista completa com as quantidades da receita anterior.\n"
    "3. Se o usuário pedir uma receita ajustada para uma quantidade específica (ex: 'para 5 kg de pão de queijo'), "
    " refaça a lista de ingredientes proporcionalmente, mantendo o modo de preparo igual.\n"
    "4. Sempre que o usuário citar medidas em kg, multiplique as quantidades base proporcionalmente.\n"
    "5. Dê apenas receitas e instruções objetivas, sem floreios.\n"
    "6. Explique o modo de preparo de forma simples e técnica.\n"
    "7. Não elogie, nem comente sobre o sabor, aparência ou textura dos alimentos.\n"
    "8. Não use emojis nem linguagem informal.\n"
    "9. Se o assunto não for panificação ou confeitaria, responda exatamente: 'Desculpe, só falo sobre panificação e confeitaria.'\n"
    "10. Se o usuário pedir para calcular fermento com base na temperatura e quantidade de farinha, "
    " use a seguinte regra prática: abaixo de 20°C use 3,5% de fermento seco; entre 21°C e 25°C use 2%; "
    " entre 26°C e 30°C use 1%; acima de 30°C use 0,5%. Retorne o resultado em gramas.\n"
)


def calcular_fermento(kg, temp):
    try:
        kg = float(kg.replace(",", "."))
        temp = float(temp.replace(",", "."))
        if kg <= 0 or temp < 0: return None
        p = 0.035 if temp < 20 else 0.02 if temp <= 25 else 0.01 if temp <= 30 else 0.005
        return round(kg * 1000 * p, 1)
    except: return None


def extrair_texto_pdf(caminho_pdf):
    """Extrai texto de um arquivo PDF usando PyPDF2."""
    try:
        texto = ""
        with open(caminho_pdf, 'rb') as f:
            leitor = PdfReader(f)
            for pagina in leitor.pages:
                texto += pagina.extract_text() + "\n"
        return texto.strip()
    except Exception as e:
        print(f"Erro ao extrair PDF: {e}")
        return ""


def carregar_pdfs_pasta():
    """Carrega automaticamente todos os PDFs da pasta pdfs_upload no startup."""
    global pdf_content
    if not os.path.exists(PDF_FOLDER):
        return
    
    for arquivo in os.listdir(PDF_FOLDER):
        if arquivo.endswith('.pdf'):
            caminho = os.path.join(PDF_FOLDER, arquivo)
            try:
                texto = extrair_texto_pdf(caminho)
                pdf_content += f"\n\n[PDF: {arquivo}]\n{texto}"
                print(f"✓ PDF carregado: {arquivo}")
            except Exception as e:
                print(f"✗ Erro ao carregar {arquivo}: {e}")


carregar_pdfs_pasta()


def limpar_cache_periodico():
    while True:
        time.sleep(3600)
        global cache
        cache = carregar_cache()
threading.Thread(target=limpar_cache_periodico, daemon=True).start()


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload_pdf", methods=["POST"])
def upload_pdf():
    """Rota para fazer upload de PDFs."""
    global pdf_content
    try:
        if 'pdf' not in request.files:
            return jsonify({"erro": "Nenhum arquivo fornecido"}), 400
        
        file = request.files['pdf']
        if not file.filename.endswith('.pdf'):
            return jsonify({"erro": "Apenas PDFs são aceitos"}), 400
        
        
        caminho_temp = os.path.join(PDF_FOLDER, file.filename)
        file.save(caminho_temp)
        
        
        if PDF_SUPPORT:
            novo_texto = extrair_texto_pdf(caminho_temp)
            pdf_content += "\n\n[PDF: " + file.filename + "]\n" + novo_texto
            return jsonify({"status": "ok", "mensagem": f"PDF '{file.filename}' carregado com sucesso!"})
        else:
            return jsonify({"erro": "PyPDF2 não instalado. Instale com: pip install PyPDF2"}), 500
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route("/chat", methods=["POST"])
def chat():
    global cache
    try:
        print("\n[CHAT] === NOVA REQUISIÇÃO ===")
        dados = request.get_json()
        if not dados or 'mensagem' not in dados:
            print("[CHAT] ✗ Mensagem não enviada")
            return jsonify({"erro": "Mensagem não enviada."}), 400
        mensagem = dados['mensagem'].strip()
        print(f"[CHAT] Mensagem: {mensagem[:50]}...")
        if not mensagem: return jsonify({"resposta": "Digite algo."})

        
        if 'historico' not in session: session['historico'] = []
        if 'ultima_receita' not in session: session['ultima_receita'] = ""
        historico = session['historico']
        ultima_receita = session['ultima_receita']

        
        if "fermento" in mensagem.lower() and "temperatura" in mensagem.lower():
            farinha = re.search(r"(\d+(?:[.,]\d+)?)\s*kg", mensagem, re.I)
            temp = re.search(r"(\d+(?:[.,]\d+)?)\s*(?:°|graus|c)", mensagem, re.I)
            if farinha and temp:
                f_kg = farinha.group(1)
                t_c = temp.group(1)
                fermento = calcular_fermento(f_kg, t_c)
                if fermento is not None:
                    return jsonify({"resposta": f"Para {f_kg} kg de farinha a {t_c}°C, use {fermento} g de fermento seco."})
                else:
                    return jsonify({"resposta": "Valores inválidos."})
            else:
                return jsonify({"resposta": "Informe farinha (kg) e temperatura (°C)."})

        
        if re.search(r"\bingrediente\b", mensagem.lower()):
            if ultima_receita:
                mensagem = f"Liste apenas os ingredientes da receita: {ultima_receita}"
            else:
                return jsonify({"resposta": "Não sei de qual receita."})

        
        chave = f"{mensagem}|{ultima_receita}"
        if chave in cache:
            return jsonify({"resposta": cache[chave]})

        
        historico.append(mensagem)
        if len(historico) > 3: historico.pop(0)

        
        contexto = contexto_base + "\n\nHistórico:\n" + "\n".join(historico[-3:])
        
       
        if pdf_content:
            contexto += f"\n\n[CONTEÚDO DE PDFs CARREGADOS]\n{pdf_content[:5000]}"  

        
        tentativa = 0
        tempo_inicio = time.time()
        while tentativa < 3:
            try:
                print(f"[GEMINI] Tentativa {tentativa + 1}/3 - Enviando para API...")
                resp = modelo.generate_content(f"{contexto}\nUsuário: {mensagem}")
                texto = resp.text.strip()
                tempo_decorrido = time.time() - tempo_inicio
                print(f"[GEMINI] ✓ Resposta recebida em {tempo_decorrido:.2f}s")
                break
            except Exception as e:
                tentativa += 1
                tempo_decorrido = time.time() - tempo_inicio
                print(f"[GEMINI] ✗ Erro na tentativa {tentativa}: {str(e)}")
                print(f"[GEMINI] Tempo decorrido: {tempo_decorrido:.2f}s")
                if tentativa < 3:
                    espera = 5 ** tentativa
                    print(f"[GEMINI] Aguardando {espera}s antes de tentar novamente...")
                    time.sleep(espera)
        else:
            tempo_total = time.time() - tempo_inicio
            print(f"[GEMINI] ✗ FALHOU após 3 tentativas. Tempo total: {tempo_total:.2f}s")
            return jsonify({"resposta": "Limite da API atingido. Tente novamente em alguns momentos."}), 503

        
        cache[chave] = texto
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
        match = re.search(r"(?i)(receita de|para fazer)\s+([a-zà-ú\s]+)", mensagem)
        if match:
            session['ultima_receita'] = match.group(2).strip().lower()
        session['historico'] = historico

        return jsonify({"resposta": texto})

    except Exception as e:
        import traceback
        print(f"\n[CHAT] ✗ ERRO NÃO TRATADO:")
        print(f"[CHAT] {type(e).__name__}: {str(e)}")
        traceback.print_exc()
        return jsonify({"erro": f"Erro interno: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True)