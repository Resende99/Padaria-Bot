PadariaBot

Este projeto é um chatbot desenvolvido para auxiliar atividades de uma padaria, respondendo perguntas relacionadas a receitas, massas e fermentação. Ele utiliza um PDF com receitas reais como base principal e, quando necessário, consulta uma API de IA para complementar respostas.


O que o projeto faz
	•	Recebe perguntas do usuário pelo chat.
	•	Consulta primeiro o conteúdo do PDF carregado.
	•	Usa a API de IA apenas quando precisa completar ou melhorar a resposta.
	•	Mantém o foco exclusivamente em panificação e confeitaria.



Como funciona

Front-end
	•	Interface onde o usuário envia perguntas.
	•	Envia mensagens para o servidor Flask.
	•	Exibe as respostas recebidas em JSON como mensagens no chat.

Back-end (Flask)

Responsável por:
	•	Carregar o PDF das receitas durante a inicialização.
	•	Extrair e armazenar o conteúdo para consulta.
	•	Montar o contexto enviado à IA.
	•	Processar e devolver a resposta ao front-end.

Integração com IA
	•	Recebe a pergunta do usuário + o conteúdo do PDF.
	•	Produz respostas focadas no tema da padaria.
	•	Atua apenas como complemento do material do PDF.

⸻

Principais recursos
	•	Leitura automática do PDF.
	•	Chat funcional no navegador.
	•	Sistema de cálculo automático de fermento com base na temperatura.
	•	Respostas sempre relacionadas ao tema.

⸻

Estrutura do projeto
	•	Front-end: interface simples em HTML, CSS e JS.
	•	Back-end: servidor Flask com rotas para interação do chat e upload de PDF.
	•	API de IA: utilizada para apoiar respostas quando o PDF não é suficiente.
	•	PDF: arquivo que serve como fonte principal de informação.


Deploy no Render

O projeto também foi configurado para rodar online pelo Render. Depois de enviado ao GitHub:
	•	O repositório é conectado ao Render.
	•	O serviço faz o build automaticamente.
	•	O Flask roda como aplicação web acessível por URL.

Isso permite que o chatbot funcione na nuvem e possa ser acessado sem precisar executar o código localmente.



Objetivo do projeto

Criar um assistente simples, direto e funcional para uso em padarias, centralizando informações de receitas e práticas de fermentação, garantindo praticidade e rapidez nas respostas.

⸻

Se quiser, posso ajustar mais partes, deixar mais curto, mais formal, mais técnico ou mais de “aluno apresentando trabalho”.


Objetivo do projeto

Criar um assistente simples, direto e funcional para uso em padarias, centralizando informações de receitas e práticas de fermentação, garantindo praticidade e rapidez nas respostas.


O Padaria-Bot esta disponivel online atraves do Render:

https://padaria-bot.onrender.com
