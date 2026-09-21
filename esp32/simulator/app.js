const canvas = document.getElementById("screen");
const ctx = canvas.getContext("2d");
const logEl = document.getElementById("log");
const form = document.getElementById("askForm");
const messageInput = document.getElementById("message");
const apiBaseInput = document.getElementById("apiBase");
const apiKeyInput = document.getElementById("apiKey");
const useMockInput = document.getElementById("useMock");

const COLORS = {
  bg: "#122a3a",
  panel: "#1c4052",
  accent: "#4bb356",
  soft: "#bfe9a8",
  beak: "#e5392f",
  text: "#f0f8f4",
  muted: "#8caab4",
};

const state = {
  mood: "happy",
  wifi: true,
  ip: "192.168.1.50",
  model: "grok",
  bubble: "Olá! Sou Calisto. Toque num atalho ou digite abaixo.",
  blink: false,
  speakOpen: 2,
  thinkDots: 0,
};

const CHIPS = [
  { x: 8, y: 198, w: 70, h: 28, id: "hello", label: "Ola",
    prompt: "Ola! Como voce esta hoje?" },
  { x: 82, y: 198, w: 70, h: 28, id: "joke", label: "Piada",
    prompt: "Me conte uma piada curta e leve." },
  { x: 156, y: 198, w: 56, h: 28, id: "who", label: "Quem?",
    prompt: "Quem e voce e o que consegue fazer neste display?" },
  { x: 216, y: 198, w: 50, h: 28, id: "help", label: "?",
    prompt: "Como posso conversar com voce neste ESP32 CYD?" },
  { x: 270, y: 198, w: 42, h: 28, id: "ok", label: "OK", prompt: null },
];

function roundRect(x, y, w, h, r) {
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.arcTo(x + w, y, x + w, y + h, r);
  ctx.arcTo(x + w, y + h, x, y + h, r);
  ctx.arcTo(x, y + h, x, y, r);
  ctx.arcTo(x, y, x + w, y, r);
  ctx.closePath();
}

function wrapText(text, x, y, maxW, lineH, maxLines) {
  const words = String(text).split(/\s+/);
  let line = "";
  let lines = 0;
  ctx.fillStyle = COLORS.text;
  ctx.font = "12px sans-serif";
  for (const word of words) {
    const test = line ? `${line} ${word}` : word;
    if (ctx.measureText(test).width > maxW && line) {
      ctx.fillText(line, x, y + lines * lineH);
      lines += 1;
      line = word;
      if (lines >= maxLines) {
        ctx.fillText("...", x + maxW - 16, y + (lines - 1) * lineH);
        return;
      }
    } else line = test;
  }
  if (line && lines < maxLines) ctx.fillText(line, x, y + lines * lineH);
}

function drawAvatar() {
  const cx = 56, cy = 110;
  const body = state.mood === "offline" ? COLORS.muted : COLORS.accent;
  ctx.fillStyle = body;
  ctx.beginPath(); ctx.arc(cx, cy + 18, 34, 0, Math.PI * 2); ctx.fill();
  ctx.fillStyle = COLORS.soft;
  ctx.beginPath(); ctx.ellipse(cx, cy + 28, 22, 18, 0, 0, Math.PI * 2); ctx.fill();
  ctx.fillStyle = body;
  ctx.beginPath(); ctx.arc(cx, cy - 18, 28, 0, Math.PI * 2); ctx.fill();
  ctx.fillStyle = COLORS.soft;
  ctx.beginPath(); ctx.ellipse(cx, cy - 8, 18, 12, 0, 0, Math.PI * 2); ctx.fill();

  const eyeY = cy - 22;
  if (state.blink || state.mood === "thinking") {
    ctx.strokeStyle = COLORS.text; ctx.lineWidth = 2;
    ctx.beginPath(); ctx.moveTo(cx - 12, eyeY); ctx.lineTo(cx - 4, eyeY); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(cx + 4, eyeY); ctx.lineTo(cx + 12, eyeY); ctx.stroke();
  } else {
    ctx.fillStyle = "#fff";
    ctx.beginPath(); ctx.arc(cx - 10, eyeY, 7, 0, Math.PI * 2); ctx.fill();
    ctx.beginPath(); ctx.arc(cx + 10, eyeY, 7, 0, Math.PI * 2); ctx.fill();
    ctx.fillStyle = "#111";
    ctx.beginPath(); ctx.arc(cx - 10, eyeY + 1, 3, 0, Math.PI * 2); ctx.fill();
    ctx.beginPath(); ctx.arc(cx + 10, eyeY + 1, 3, 0, Math.PI * 2); ctx.fill();
  }

  let open = state.mood === "speaking" ? state.speakOpen : state.mood === "happy" ? 3 : 2;
  ctx.fillStyle = COLORS.beak;
  ctx.beginPath();
  ctx.moveTo(cx - 8, cy - 8); ctx.lineTo(cx + 8, cy - 8); ctx.lineTo(cx, cy + 2 + open);
  ctx.closePath(); ctx.fill();

  if (state.mood === "thinking") {
    for (let i = 0; i < 3; i++) {
      ctx.fillStyle = i <= state.thinkDots ? COLORS.text : COLORS.muted;
      ctx.beginPath(); ctx.arc(cx - 10 + i * 10, cy + 58, 3, 0, Math.PI * 2); ctx.fill();
    }
  }
  ctx.fillStyle = COLORS.muted; ctx.font = "11px sans-serif"; ctx.textAlign = "center";
  ctx.fillText("Calisto", cx, 178); ctx.textAlign = "left";
}

function draw() {
  ctx.fillStyle = COLORS.bg; ctx.fillRect(0, 0, 320, 240);
  ctx.fillStyle = COLORS.panel; ctx.fillRect(0, 0, 320, 24);
  ctx.font = "12px sans-serif";
  ctx.fillStyle = state.wifi ? COLORS.accent : COLORS.beak;
  ctx.fillText(state.wifi ? "WiFi" : "off", 6, 16);
  ctx.fillStyle = COLORS.muted; ctx.fillText(state.ip, 42, 16);
  ctx.fillStyle = COLORS.text; ctx.fillText("Calisto", 130, 16);
  ctx.fillStyle = COLORS.accent; ctx.textAlign = "right";
  ctx.fillText(state.model, 314, 16); ctx.textAlign = "left";
  drawAvatar();
  ctx.fillStyle = COLORS.panel; roundRect(110, 28, 200, 130, 10); ctx.fill();
  ctx.strokeStyle = COLORS.accent; ctx.stroke();
  wrapText(state.bubble, 118, 48, 184, 16, 7);
  for (const c of CHIPS) {
    ctx.fillStyle = COLORS.panel; roundRect(c.x, c.y, c.w, c.h, 8); ctx.fill();
    ctx.strokeStyle = COLORS.accent; ctx.stroke();
    ctx.fillStyle = COLORS.text; ctx.font = "12px sans-serif"; ctx.textAlign = "center";
    ctx.fillText(c.label, c.x + c.w / 2, c.y + 18);
  }
  ctx.textAlign = "left";
}

function inferMood(reply) {
  const low = reply.toLowerCase();
  if (/(desculpe|problema|falha|infelizmente)/.test(low)) return "concerned";
  if (/(bom dia|tudo bem|ótimo|otimo|prazer)/.test(low)) return "happy";
  return "speaking";
}

async function askBot(message) {
  if (!message) return;
  state.mood = "listening"; state.bubble = `> ${message}`; draw();
  logEl.textContent = "Consultando…";
  await new Promise((r) => setTimeout(r, 200));
  state.mood = "thinking"; draw();

  let reply;
  if (useMockInput.checked) {
    await new Promise((r) => setTimeout(r, 500));
    if (/piada/i.test(message)) {
      reply = "Por que o chip foi ao médico? Porque estava com overload… e melhorou com um reset!";
    } else if (/quem/i.test(message)) {
      reply = "Sou Calisto, avatar neste ESP32-CYD. Converso com você via Grok neste display.";
    } else if (/ajuda|\?/i.test(message)) {
      reply = "Toque nos chips, digite no Serial, ou use o campo abaixo. Eu respondo pelo Grok.";
    } else {
      reply = "Oi! Tudo bem por aqui. Em que posso te ajudar hoje?";
    }
  } else {
    const key = apiKeyInput.value.trim();
    if (!key) {
      state.mood = "concerned";
      state.bubble = "Informe a GROK API key ou ative o modo mock.";
      draw(); logEl.textContent = "missing api key"; return;
    }
    try {
      const base = apiBaseInput.value.replace(/\/$/, "");
      const resp = await fetch(`${base}/chat/completions`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${key}`,
        },
        body: JSON.stringify({
          model: "grok-2-latest",
          messages: [
            {
              role: "system",
              content:
                "You are Calisto, a friendly avatar on an ESP32 CYD. Reply in Brazilian Portuguese, briefly (under 280 chars).",
            },
            { role: "user", content: message },
          ],
        }),
      });
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const data = await resp.json();
      reply = data.choices?.[0]?.message?.content || "(sem resposta)";
    } catch (err) {
      state.mood = "concerned";
      state.bubble = `Falha Grok: ${err.message}`;
      draw(); logEl.textContent = String(err.message); return;
    }
  }

  state.mood = inferMood(reply);
  state.bubble = reply;
  draw();
  logEl.textContent = `mood=${state.mood}`;
}

canvas.addEventListener("click", (ev) => {
  const rect = canvas.getBoundingClientRect();
  const x = Math.round((ev.clientX - rect.left) * (320 / rect.width));
  const y = Math.round((ev.clientY - rect.top) * (240 / rect.height));
  for (const c of CHIPS) {
    if (x >= c.x && x < c.x + c.w && y >= c.y && y < c.y + c.h) {
      if (c.id === "ok") { askBot(messageInput.value.trim()); messageInput.value = ""; }
      else if (c.prompt) askBot(c.prompt);
      return;
    }
  }
});

form.addEventListener("submit", (ev) => {
  ev.preventDefault();
  const msg = messageInput.value.trim();
  messageInput.value = "";
  askBot(msg);
});

setInterval(() => {
  state.blink = Math.random() < 0.08;
  if (state.mood === "speaking") state.speakOpen = state.speakOpen === 2 ? 6 : 2;
  if (state.mood === "thinking") state.thinkDots = (state.thinkDots + 1) % 3;
  draw();
}, 280);

draw();
