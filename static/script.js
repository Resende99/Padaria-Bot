const chatBox = document.getElementById("chat-box");
const userInput = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");

window.addEventListener("load", async () => {
  const typing = document.createElement("div");
  typing.classList.add("typing");
  typing.textContent = "PadariaBot está digitando...";
  chatBox.appendChild(typing);
  chatBox.scrollTop = chatBox.scrollHeight;

  await new Promise(r => setTimeout(r, 1200));
  typing.remove();

  appendMessage("Olá! Sou o PadariaBot. Pode me pedir receitas ou dicas sobre fermentação", "bot-message");
});

sendBtn.addEventListener("click", sendMessage);
userInput.addEventListener("keypress", (e) => {
  if (e.key === "Enter") sendMessage();
});

function appendMessage(content, className) {
  const msg = document.createElement("div");
  msg.classList.add("message", className);
  msg.textContent = content;
  chatBox.appendChild(msg);
  chatBox.scrollTop = chatBox.scrollHeight;
}

async function sendMessage() {
  const text = userInput.value.trim();
  if (text === "") return;

  appendMessage(text, "user-message");
  userInput.value = "";

  const typingMsg = document.createElement("div");
  typingMsg.classList.add("typing");
  typingMsg.textContent = "PadariaBot está digitando...";
  chatBox.appendChild(typingMsg);
  chatBox.scrollTop = chatBox.scrollHeight;

  userInput.disabled = true;
  sendBtn.disabled = true;

  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 20000);

  try {
    const response = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ mensagem: text }),
      signal: controller.signal,
    });

    const data = await response.json();
    typingMsg.remove();

    if (data.erro) {
      appendMessage(data.erro, "error-message");
    } else {
      appendMessage(data.resposta, "bot-message");
    }
  } catch (error) {
    typingMsg.remove();
    appendMessage(error.name === 'AbortError' ? "Tempo esgotado." : "Erro de conexão.", "error-message");
  } finally {
    clearTimeout(timeout);
    userInput.disabled = false;
    sendBtn.disabled = false;
    userInput.focus();
  }
}