/* Administração — Conversador PoP-SE */

const CRED_LABELS = {
  ollama_host: "Ollama Host (URL)",
  gemini_api_key: "Gemini API Key",
  openai_api_key: "OpenAI API Key",
  openai_base_url: "OpenAI Base URL (opcional)",
  azure_openai_api_key: "Azure OpenAI API Key",
  azure_openai_endpoint: "Azure Endpoint",
  azure_openai_deployment: "Azure Deployment",
  grok_api_key: "Grok API Key",
  grok_base_url: "Grok Base URL",
};
const SECRET_FIELDS = new Set([
  "gemini_api_key", "openai_api_key", "azure_openai_api_key", "grok_api_key",
]);

const el = (sel) => document.querySelector(sel);
const state = { token: "", config: null };

const dom = {
  authForm: el("[data-auth-form]"),
  token: el("[data-token]"),
  authed: el("[data-authed]"),
  provider: el("[data-provider]"),
  model: el("[data-model]"),
  creds: el("[data-creds]"),
  llmForm: el("[data-llm-form]"),
  guardrails: el("[data-guardrails]"),
  guardrailForm: el("[data-guardrail-form]"),
  gName: el("[data-g-name]"),
  gType: el("[data-g-type]"),
  gKeywords: el("[data-g-keywords]"),
  gMessage: el("[data-g-message]"),
  feedback: el("[data-feedback]"),
  // RAG
  ragCollection: el("[data-rag-collection]"),
  ragRefresh: el("[data-rag-refresh]"),
  ragList: el("[data-rag-list]"),
  ragDetails: el("[data-rag-details]"),
  ragFormTitle: el("[data-rag-form-title]"),
  ragForm: el("[data-rag-form]"),
  ragId: el("[data-rag-id]"),
  ragSource: el("[data-rag-source]"),
  ragText: el("[data-rag-text]"),
  ragCancel: el("[data-rag-cancel]"),
  ragSubmit: el("[data-rag-submit]"),
};

function feedback(msg, ok = true) {
  dom.feedback.textContent = msg;
  dom.feedback.className = "admin-feedback " + (ok ? "is-ok" : "is-err");
}

async function api(method, path, body) {
  const res = await fetch(`/api/v1/admin${path}`, {
    method,
    headers: {
      "Content-Type": "application/json",
      "X-Admin-Token": state.token,
    },
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) {
    let detail = `HTTP ${res.status}`;
    try { detail = (await res.json()).detail || detail; } catch (_) {}
    throw new Error(detail);
  }
  return res.status === 204 ? null : res.json();
}

function providerById(id) {
  return (state.config.providers || []).find((p) => p.id === id);
}

/* --- Renderização de IA --------------------------------------------------- */
function renderProviders() {
  const active = state.config.active || {};
  dom.provider.innerHTML = "";
  for (const p of state.config.providers) {
    const opt = document.createElement("option");
    opt.value = p.id;
    opt.textContent = p.label;
    dom.provider.appendChild(opt);
  }
  dom.provider.value = active.provider || state.config.providers[0].id;
  renderModelsAndCreds();
}

function renderModelsAndCreds() {
  const provider = providerById(dom.provider.value);
  const active = state.config.active || {};
  const activeModel = (active.models || {})[provider.id] || provider.default_model;

  dom.model.innerHTML = "";
  for (const m of provider.models) {
    const opt = document.createElement("option");
    opt.value = m;
    opt.textContent = m;
    dom.model.appendChild(opt);
  }
  dom.model.value = activeModel;

  const masked = state.config.credentials_masked || {};
  const set = state.config.credentials_set || {};
  dom.creds.innerHTML = "";
  for (const field of provider.credential_fields) {
    const wrap = document.createElement("div");
    wrap.className = "field";

    const label = document.createElement("label");
    label.setAttribute("for", `cred-${field}`);
    label.textContent = CRED_LABELS[field] || field;
    wrap.appendChild(label);

    const input = document.createElement("input");
    input.id = `cred-${field}`;
    input.type = SECRET_FIELDS.has(field) ? "password" : "text";
    input.autocomplete = "off";
    input.dataset.cred = field;
    input.placeholder = set[field] ? `Configurado (${masked[field]}) — deixe em branco p/ manter` : "Não configurado";
    wrap.appendChild(input);

    dom.creds.appendChild(wrap);
  }
}

/* --- Renderização de guardrails ------------------------------------------- */
function renderGuardrails() {
  const list = state.config.guardrails || [];
  dom.guardrails.innerHTML = "";
  if (!list.length) {
    const li = document.createElement("li");
    li.className = "muted";
    li.textContent = "Nenhum guardrail configurado.";
    dom.guardrails.appendChild(li);
    return;
  }
  for (const g of list) {
    const li = document.createElement("li");
    li.className = "guardrail" + (g.enabled ? "" : " guardrail--off");

    const main = document.createElement("div");
    main.className = "guardrail__main";

    const name = document.createElement("p");
    name.className = "guardrail__name";
    name.textContent = g.name;
    const tag = document.createElement("span");
    tag.className = "guardrail__tag";
    tag.textContent = g.type === "scope" ? "escopo" : "bloqueio";
    name.appendChild(tag);

    const msg = document.createElement("p");
    msg.className = "guardrail__msg";
    msg.textContent = g.message || "";

    const kw = document.createElement("p");
    kw.className = "guardrail__kw";
    const label = g.type === "scope" ? "Permitidas" : "Bloqueadas";
    kw.textContent = `${label}: ${(g.keywords || []).join(", ") || "—"}`;

    main.append(name, msg, kw);

    const actions = document.createElement("div");
    actions.className = "guardrail__actions";

    const toggle = document.createElement("label");
    toggle.className = "switch";
    const cb = document.createElement("input");
    cb.type = "checkbox";
    cb.checked = !!g.enabled;
    cb.addEventListener("change", () => toggleGuardrail(g.id, cb.checked));
    toggle.append(cb, document.createTextNode("Ativo"));

    const del = document.createElement("button");
    del.type = "button";
    del.className = "btn btn--danger";
    del.textContent = "Excluir";
    del.addEventListener("click", () => deleteGuardrail(g.id));

    actions.append(toggle, del);
    li.append(main, actions);
    dom.guardrails.appendChild(li);
  }
}

/* --- Base de conhecimento (RAG) ------------------------------------------- */
async function loadRagCollections() {
  const previous = dom.ragCollection.value;
  const data = await api("GET", "/rag/collections");
  dom.ragCollection.innerHTML = "";
  for (const c of data.collections) {
    const opt = document.createElement("option");
    opt.value = c.name;
    opt.textContent = `${c.name} (${c.count})`;
    dom.ragCollection.appendChild(opt);
  }
  if (previous) dom.ragCollection.value = previous;
  if (!dom.ragCollection.value && data.collections.length) {
    dom.ragCollection.value = data.collections[0].name;
  }
  await loadRagDocuments();
}

async function loadRagDocuments() {
  const collection = dom.ragCollection.value;
  if (!collection) return;
  const data = await api("GET", `/rag/documents?collection=${encodeURIComponent(collection)}`);
  dom.ragList.innerHTML = "";
  if (!data.documents.length) {
    const li = document.createElement("li");
    li.className = "muted";
    li.textContent = "Nenhum documento nesta coleção.";
    dom.ragList.appendChild(li);
    return;
  }
  for (const doc of data.documents) {
    const li = document.createElement("li");
    li.className = "guardrail";

    const main = document.createElement("div");
    main.className = "guardrail__main";

    const name = document.createElement("p");
    name.className = "guardrail__name";
    name.textContent = doc.id;
    const tag = document.createElement("span");
    tag.className = "guardrail__tag";
    tag.textContent = (doc.metadata && doc.metadata.source) || "manual";
    name.appendChild(tag);

    const text = document.createElement("p");
    text.className = "guardrail__msg";
    text.textContent = doc.text;

    main.append(name, text);

    const actions = document.createElement("div");
    actions.className = "guardrail__actions";

    const edit = document.createElement("button");
    edit.type = "button";
    edit.className = "btn btn--ghost";
    edit.textContent = "Editar";
    edit.addEventListener("click", () => startEditRag(doc));

    const del = document.createElement("button");
    del.type = "button";
    del.className = "btn btn--danger";
    del.textContent = "Excluir";
    del.addEventListener("click", () => deleteRag(doc.id));

    actions.append(edit, del);
    li.append(main, actions);
    dom.ragList.appendChild(li);
  }
}

function startEditRag(doc) {
  dom.ragId.value = doc.id;
  dom.ragSource.value = (doc.metadata && doc.metadata.source) || "";
  dom.ragText.value = doc.text;
  dom.ragFormTitle.textContent = `Editar documento: ${doc.id}`;
  dom.ragSubmit.textContent = "Salvar alterações";
  dom.ragCancel.hidden = false;
  dom.ragDetails.open = true;
  dom.ragId.focus();
}

function resetRagForm() {
  dom.ragForm.reset();
  dom.ragFormTitle.textContent = "+ Adicionar documento";
  dom.ragSubmit.textContent = "Salvar documento";
  dom.ragCancel.hidden = true;
}

async function deleteRag(docId) {
  const collection = dom.ragCollection.value;
  try {
    await api(
      "DELETE",
      `/rag/documents?collection=${encodeURIComponent(collection)}&doc_id=${encodeURIComponent(docId)}`
    );
    await loadRagCollections();
    feedback("Documento removido.");
  } catch (e) { feedback(e.message, false); }
}

/* --- Ações ---------------------------------------------------------------- */
async function loadConfig() {
  state.config = await api("GET", "/config");
  dom.authed.hidden = false;
  renderProviders();
  renderGuardrails();
  await loadRagCollections();
}

async function toggleGuardrail(id, enabled) {
  try {
    await api("PATCH", `/guardrails/${id}`, { enabled });
    await loadConfig();
    feedback("Guardrail atualizado.");
  } catch (e) { feedback(e.message, false); }
}

async function deleteGuardrail(id) {
  try {
    await api("DELETE", `/guardrails/${id}`);
    await loadConfig();
    feedback("Guardrail removido.");
  } catch (e) { feedback(e.message, false); }
}

/* --- Eventos -------------------------------------------------------------- */
dom.authForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  state.token = dom.token.value.trim();
  try {
    await loadConfig();
    sessionStorage.setItem("popse_admin_token", state.token);
    feedback("Conectado à administração.");
  } catch (err) {
    dom.authed.hidden = true;
    feedback(err.message || "Falha ao autenticar.", false);
  }
});

dom.provider.addEventListener("change", renderModelsAndCreds);

dom.llmForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const credentials = {};
  dom.creds.querySelectorAll("[data-cred]").forEach((inp) => {
    if (inp.value.trim()) credentials[inp.dataset.cred] = inp.value.trim();
  });
  try {
    await api("PUT", "/llm", {
      provider: dom.provider.value,
      model: dom.model.value,
      credentials,
    });
    await loadConfig();
    feedback("Configuração de IA salva com sucesso.");
  } catch (err) { feedback(err.message, false); }
});

dom.guardrailForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const keywords = dom.gKeywords.value.split(",").map((s) => s.trim()).filter(Boolean);
  try {
    await api("POST", "/guardrails", {
      name: dom.gName.value.trim(),
      type: dom.gType.value,
      keywords,
      message: dom.gMessage.value.trim(),
    });
    dom.guardrailForm.reset();
    await loadConfig();
    feedback("Guardrail criado.");
  } catch (err) { feedback(err.message, false); }
});

dom.ragCollection.addEventListener("change", () => loadRagDocuments().catch((e) => feedback(e.message, false)));
dom.ragRefresh.addEventListener("click", () => loadRagCollections().catch((e) => feedback(e.message, false)));
dom.ragCancel.addEventListener("click", resetRagForm);

dom.ragForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  try {
    await api("POST", "/rag/documents", {
      collection: dom.ragCollection.value,
      id: dom.ragId.value.trim(),
      text: dom.ragText.value.trim(),
      source: dom.ragSource.value.trim(),
    });
    resetRagForm();
    await loadRagCollections();
    feedback("Documento salvo na base de conhecimento.");
  } catch (err) { feedback(err.message, false); }
});

/* --- Início: reaproveita token da sessão ---------------------------------- */
(function init() {
  const saved = sessionStorage.getItem("popse_admin_token");
  if (saved) {
    dom.token.value = saved;
    state.token = saved;
    loadConfig().catch(() => { dom.authed.hidden = true; });
  }
})();
