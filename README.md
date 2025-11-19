# PadariaBot

Este projeto é um chatbot criado para ajudar em uma padaria, respondendo perguntas sobre receitas, massas e fermentação. Ele utiliza um PDF com receitas reais e uma API de IA para complementar respostas quando necessário.

---

## O que o projeto faz

* Recebe perguntas do usuário.
* Usa primeiro o conteúdo do PDF como fonte principal.
* Quando necessário, consulta a IA para completar a resposta.
* Sempre segue regras para falar apenas de panificação e confeitaria.

---

## Como funciona

### **Front-end**

* É a parte visual que o usuário interage.
* Envia as mensagens para o servidor.
* Mostra as respostas que chegam em formato JSON.

### **Back-end (Flask)**

Responsável por:

* Ler e carregar o PDF ao iniciar o sistema.
* Extrair o texto das receitas.
* Montar o contexto e enviar para a IA.
* Processar a resposta e devolver ao front-end.

### **IA**

* Recebe a pergunta + conteúdo do PDF.
* Gera uma resposta focada em panificação.
* Segue regras rígidas para não sair do tema.

---

## Principais recursos

* Leitura automática do PDF.
* Chat funcional acessado pelo navegador.
* API tratada com tentativas e prevenção de erro 429.
* Cálculo automático de fermento usando temperatura.
* Respostas totalmente focadas no tema padaria.

---

## Estrutura do projeto

* **Front-end**: interface simples do chat.
* **Back-end**: servidor Flask com rotas para chat e upload de PDF.
* **Integração com IA**: usa a API do Gemini.
* **PDF**: base de conhecimento com receitas.

---

## Objetivo

Criar um assistente prático e direto para padarias, usando o PDF como fonte principal e mantendo sempre o foco em panificação e confeitaria.

---
