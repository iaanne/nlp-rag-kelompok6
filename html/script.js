const WEBHOOK = "http://localhost:9000/webhook/rag-chat";
const chat = document.getElementById("chat");
const queryInput = document.getElementById("query");
const sendBtn = document.getElementById("send");

function addMsg(text, cls) {
  const div = document.createElement("div");
  div.className = `msg ${cls}`;
  div.textContent = text;
  chat.appendChild(div);
  chat.scrollTop = chat.scrollHeight;
}

async function sendQuery() {
  const q = queryInput.value.trim();
  if (!q) return;
  queryInput.value = "";
  addMsg(q, "user");
  addMsg("...", "system");
  sendBtn.disabled = true;

  try {
    const res = await fetch(WEBHOOK, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: q }),
    });
    chat.lastElementChild.remove();
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    addMsg(data.output ?? JSON.stringify(data), "bot");
  } catch (e) {
    chat.lastElementChild.remove();
    addMsg(`Error: ${e.message}`, "system");
  } finally {
    sendBtn.disabled = false;
    queryInput.focus();
  }
}

queryInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") sendQuery();
});
