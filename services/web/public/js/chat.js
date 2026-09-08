/* =============================================================================
   Conversador PoP-SE — lógica do chat
   ========================================================================== */

const USER_ID_KEY = "conversador_popse_user_id";
const ASSISTANT_NAME = "Calisto";

const els = {
  form: document.querySelector("[data-form]"),
  input: document.querySelector("[data-input]"),
  send: document.querySelector("[data-send]"),
  messages: document.querySelector("[data-messages]"),
  typing: document.querySelector("[data-typing]"),
  avatar: document.querySelector("[data-avatar]"),
  statusText: document.querySelector("[data-status-text]"),
  floatStatus: document.querySelector("[data-float-status]"),
};

/* Mini mascote (cabeça) usado no avatar de cada resposta */
const MINI_PARROT = `
<svg viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" focusable="false">
  <circle cx="20" cy="20" r="15" fill="#4bb356"/>
  <ellipse cx="20" cy="25" rx="11" ry="9" fill="#bfe9a8" opacity="0.55"/>
  <circle cx="14.5" cy="17" r="4.4" fill="#fff"/>
  <circle cx="25.5" cy="17" r="4.4" fill="#fff"/>
  <circle cx="15" cy="17.6" r="2.3" fill="#20303a"/>
  <circle cx="26" cy="17.6" r="2.3" fill="#20303a"/>
  <path d="M15 23 C 17 20, 23 20, 25 23 C 23.5 28, 20 30, 20 30 C 20 30, 16.5 28, 15 23 Z" fill="#e5392f"/>
</svg>`;

/* --- Identidade persistente do usuário ------------------------------------ */
function getUserId() {
  let id = localStorage.getItem(USER_ID_KEY);
  if (!id) {
    id = (crypto.randomUUID && crypto.randomUUID()) || String(Date.now());
    localStorage.setItem(USER_ID_KEY, id);
  }
  return id;
}

/* --- Renderização segura de texto (markdown leve) ------------------------- */
function escapeText(text) {
  return document.createTextNode(text);
}

// Trata **negrito**, e-mails e URLs, devolvendo nós de DOM (sem innerHTML).
function inlineNodes(text) {
  const frag = document.createDocumentFragment();
  const boldSplit = text.split(/\*\*(.+?)\*\*/g); // índices ímpares = negrito
  boldSplit.forEach((chunk, i) => {
    if (i % 2 === 1) {
      const strong = document.createElement("strong");
      strong.append(...linkNodes(chunk));
      frag.appendChild(strong);
    } else {
      frag.append(...linkNodes(chunk));
    }
  });
  return frag;
}

function linkNodes(text) {
  const nodes = [];
  const pattern = /(https?:\/\/[^\s<]+|[\w.+-]+@[\w-]+\.[\w.-]+)/g;
  let last = 0;
  let m;
  while ((m = pattern.exec(text)) !== null) {
    if (m.index > last) nodes.push(escapeText(text.slice(last, m.index)));
    const value = m[0];
    const a = document.createElement("a");
    a.textContent = value;
    a.href = value.includes("@") ? `mailto:${value}` : value;
    if (!value.includes("@")) { a.target = "_blank"; a.rel = "noopener"; }
    nodes.push(a);
    last = m.index + value.length;
  }
  if (last < text.length) nodes.push(escapeText(text.slice(last)));
  return nodes;
}

function renderMarkdown(text) {
  const frag = document.createDocumentFragment();
  const lines = String(text).replace(/\r/g, "").split("\n");
  let list = null;
  let para = null;

  const flushPara = () => { if (para) { frag.appendChild(para); para = null; } };
  const flushList = () => { if (list) { frag.appendChild(list); list = null; } };

  for (const raw of lines) {
    const line = raw.trimEnd();
    const listMatch = line.match(/^\s*(?:[-*]|\d+\.)\s+(.*)$/);
    if (listMatch) {
      flushPara();
      if (!list) list = document.createElement("ul");
      const li = document.createElement("li");
      li.appendChild(inlineNodes(listMatch[1]));
      list.appendChild(li);
      continue;
    }
    if (line === "") {
      flushList();
      flushPara();
      continue;
    }
    flushList();
    if (!para) para = document.createElement("p");
    else para.appendChild(document.createElement("br"));
    para.appendChild(inlineNodes(line));
  }
  flushList();
  flushPara();
  return frag;
}

/* --- Construção de mensagens ---------------------------------------------- */
function addMessage(role, content, { markdown = false, state = "" } = {}) {
  const row = document.createElement("div");
  row.className = `msg msg--${role === "user" ? "user" : "bot"}${state ? " msg--" + state : ""}`;

  const avatar = document.createElement("div");
  avatar.className = "msg__avatar";
  avatar.setAttribute("aria-hidden", "true");
  if (role === "user") {
    avatar.textContent = "Você";
  } else {
    avatar.innerHTML = MINI_PARROT;
  }

  const body = document.createElement("div");
  body.className = "msg__body";

  const name = document.createElement("p");
  name.className = "msg__name";
  name.textContent = role === "user" ? "Você" : ASSISTANT_NAME;

  const bubble = document.createElement("div");
  bubble.className = "bubble";
  if (markdown) bubble.appendChild(renderMarkdown(content));
  else bubble.appendChild(escapeText(content));

  body.append(name, bubble);
  row.append(avatar, body);
  els.messages.appendChild(row);
  scrollToBottom();
  return row;
}

function scrollToBottom() {
  els.messages.scrollTop = els.messages.scrollHeight;
}

/* --- Estados do assistente ------------------------------------------------ */
function setAvatarState(stateClass) {
  els.avatar.classList.remove("is-thinking", "is-talking");
  if (stateClass) els.avatar.classList.add(stateClass);
}
function setStatus(text) {
  if (els.statusText) els.statusText.textContent = text;
  if (els.floatStatus) els.floatStatus.textContent = text;
}
function showTyping(show) {
  els.typing.hidden = !show;
  if (show) scrollToBottom();
}

/* --- Envio ---------------------------------------------------------------- */
async function sendMessage(text) {
  addMessage("user", text);
  els.send.disabled = true;
  showTyping(true);
  setAvatarState("is-thinking");
  setStatus("Consultando as fontes…");

  try {
    const res = await fetch("/api/v1/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text, user_id: getUserId(), channel: "web" }),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();

    showTyping(false);
    setAvatarState("is-talking");
    setStatus("Respondendo…");
    addMessage("assistant", data.reply, { markdown: true });

    setTimeout(() => {
      setAvatarState("");
      setStatus("Pronto para ajudar");
    }, 1800);
  } catch (err) {
    console.error(err);
    showTyping(false);
    setAvatarState("");
    setStatus("Tive um problema ao responder");
    addMessage(
      "assistant",
      "Peço desculpas, não foi possível processar sua mensagem no momento. Por favor, tente novamente em instantes ou contate o PoP-SE em info@pop-se.rnp.br.",
      { markdown: true, state: "error" }
    );
  } finally {
    els.send.disabled = false;
    els.input.focus();
  }
}

/* --- Textarea: auto-crescimento ------------------------------------------- */
function autoGrow() {
  els.input.style.height = "auto";
  els.input.style.height = Math.min(els.input.scrollHeight, 180) + "px";
}

/* --- Ligações de eventos -------------------------------------------------- */
els.form.addEventListener("submit", (e) => {
  e.preventDefault();
  const text = els.input.value.trim();
  if (!text) return;
  els.input.value = "";
  autoGrow();
  sendMessage(text);
});

// Enter envia; Shift+Enter quebra linha. Seguro para IME (isComposing / keyCode 229).
els.input.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    if (e.isComposing || e.keyCode === 229) return;
    els.form.requestSubmit();
  }
});
els.input.addEventListener("input", autoGrow);

// Clique no mascote flutuante leva o foco ao campo de mensagem.
if (els.avatar) {
  els.avatar.addEventListener("click", () => els.input.focus());
}

/* --- Saudação inicial ----------------------------------------------------- */
addMessage(
  "assistant",
  "Olá! Sou o **Calisto**, assistente virtual do PoP-SE. Estou à disposição para ajudá-lo com informações sobre conectividade, manutenções e a situação dos links da sua instituição. Como posso ajudá-lo hoje?",
  { markdown: true }
);
els.input.focus();
