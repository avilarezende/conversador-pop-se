/**
 * SegPortal — dashboard, arquivos, navegador embutido e computadores.
 * Sem exposição de stack interna de sessões ao usuário final.
 */

const state = {
  user: null,
  dashboard: null,
  panel: "home",
  shareId: null,
  path: "",
};

const BROWSER_HOME = "/browser/home.html";
const BROWSER_PRESETS = {
  "segportal://inicio": "/browser/home.html",
  "segportal://bacen": "/browser/bacen.html",
  "https://www.bcb.gov.br/": "/browser/bacen.html",
  "https://www.bcb.gov.br": "/browser/bacen.html",
};

const COMPUTERS = [
  {
    id: "browser-html",
    title: "Navegador Web SegPortal",
    description: "Navegação corporativa HTML5 já disponível na aba Navegador.",
    kind: "browser",
    badge: "Padrão",
  },
  {
    id: "desktop-financeiro",
    title: "Desktop Financeiro",
    description: "Estação remota com sistemas financeiros (liberação sob demanda).",
    kind: "desktop",
    badge: "RDP",
    embed: "/browser/desktop.html?name=Desktop%20Financeiro",
  },
  {
    id: "desktop-admin",
    title: "Desktop Administrativo",
    description: "Estação remota para tarefas administrativas.",
    kind: "desktop",
    badge: "RDP",
    embed: "/browser/desktop.html?name=Desktop%20Administrativo",
    adminOnly: true,
  },
];

const $ = (sel, root = document) => root.querySelector(sel);
const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];

function toast(msg) {
  const el = $("#toast");
  if (!el) return;
  el.textContent = msg;
  el.hidden = false;
  clearTimeout(toast._t);
  toast._t = setTimeout(() => {
    el.hidden = true;
  }, 3200);
}

async function api(path, options = {}) {
  const opts = { credentials: "same-origin", ...options };
  if (opts.body && !(opts.body instanceof FormData) && typeof opts.body === "object") {
    opts.headers = { "Content-Type": "application/json", ...(opts.headers || {}) };
    opts.body = JSON.stringify(opts.body);
  }
  const res = await fetch(path, opts);
  if (res.status === 401 && !path.includes("/login")) {
    showLogin();
    throw new Error("Sessão expirada");
  }
  const ct = res.headers.get("content-type") || "";
  const data = ct.includes("application/json") ? await res.json() : null;
  if (!res.ok) {
    const detail = data && data.detail;
    const msg = Array.isArray(detail)
      ? detail.map((d) => d.msg || d).join("; ")
      : detail || (data && data.message) || `Erro ${res.status}`;
    throw new Error(msg);
  }
  return data;
}

function showLogin() {
  $("#view-login").hidden = false;
  $("#view-app").hidden = true;
  setProductivityVisible(false);
  closeCalendarDrawer();
}

function showApp() {
  $("#view-login").hidden = true;
  $("#view-app").hidden = false;
  setProductivityVisible(true);
  initRemindersPanel();
  initCalendarDrawer();
}

function setPanel(name) {
  state.panel = name;
  $$(".nav-btn").forEach((b) => b.classList.toggle("active", b.dataset.panel === name));
  $$(".panel").forEach((p) => {
    p.hidden = p.id !== `panel-${name}`;
  });
  const titles = {
    home: "Dashboard pessoal",
    files: "Arquivos",
    browser: "Navegador corporativo",
    computers: "Computadores",
  };
  const sub = $("#nav-subtitle");
  if (sub) sub.textContent = titles[name] || "SegPortal";
  if (name === "files") {
    if (state.shareId) loadListing().catch((e) => toast(e.message));
    else renderPlaces();
  }
  if (name === "browser") {
    ensureBrowserLoaded();
  }
  if (name === "computers") {
    renderComputers();
  }
}

function formatSize(n) {
  if (n == null) return "—";
  if (n < 1024) return `${n} B`;
  if (n < 1024 * 1024) return `${(n / 1024).toFixed(1)} KB`;
  return `${(n / (1024 * 1024)).toFixed(1)} MB`;
}

function formatDate(ts) {
  if (!ts) return "—";
  return new Date(ts * 1000).toLocaleString("pt-BR", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function parentPath(path) {
  const parts = (path || "").split("/").filter(Boolean);
  parts.pop();
  return parts.join("/");
}

function escapeHtml(str) {
  return String(str ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function askName(title, initial = "") {
  const dlg = $("#name-dialog");
  const form = $("#name-dialog-form");
  const input = $("#name-dialog-input");
  const heading = $("#name-dialog-title");
  if (!dlg || !form || !input) {
    return Promise.resolve(window.prompt(title, initial));
  }
  heading.textContent = title;
  input.value = initial || "";
  return new Promise((resolve) => {
    const onClose = () => {
      form.removeEventListener("submit", onSubmit);
      dlg.removeEventListener("close", onClose);
      resolve(dlg.returnValue === "ok" ? input.value.trim() : null);
    };
    const onSubmit = (ev) => {
      const submitter = ev.submitter;
      dlg.returnValue = submitter && submitter.value === "cancel" ? "cancel" : "ok";
    };
    form.addEventListener("submit", onSubmit);
    dlg.addEventListener("close", onClose);
    dlg.showModal();
    input.focus();
    input.select();
  });
}

function ensureBrowserLoaded() {
  const frame = $("#browser-frame");
  const urlInput = $("#browser-url");
  if (!frame.src || frame.src === "about:blank") {
    frame.src = BROWSER_HOME;
    urlInput.value = "segportal://inicio";
  }
}

function navigateBrowser(raw) {
  const value = (raw || "").trim();
  const mapped = BROWSER_PRESETS[value] || BROWSER_PRESETS[value.replace(/\/$/, "")];
  const frame = $("#browser-frame");
  const urlInput = $("#browser-url");
  if (mapped) {
    frame.src = mapped;
    urlInput.value = value.startsWith("http") ? value : Object.keys(BROWSER_PRESETS).find((k) => BROWSER_PRESETS[k] === mapped) || value;
    return;
  }
  if (value.startsWith("/browser/")) {
    frame.src = value;
    urlInput.value = value;
    return;
  }
  // Sites externos: abre página orientativa dentro do portal (mesmo iframe)
  frame.src = `/browser/home.html?q=${encodeURIComponent(value)}`;
  urlInput.value = value;
  toast("Neste ambiente demo, use atalhos segportal://inicio ou segportal://bacen");
}

function renderDashboard() {
  const d = state.dashboard;
  if (!d) return;
  const u = d.user;
  $("#user-name").textContent = u.display_name;
  $("#user-meta").textContent = `${u.username} · ${u.auth_source === "ldap" ? "Active Directory" : "Local"} · ${u.role}`;
  $("#hello-name").textContent = (u.display_name || "usuário").split(" ")[0];

  const shares = d.shares || [];
  const adShares = shares.filter((s) => s.source !== "cloud");
  const grid = $("#shares-grid");
  const empty = $("#shares-empty");
  grid.innerHTML = "";
  if (!adShares.length) {
    empty.hidden = false;
  } else {
    empty.hidden = true;
    adShares.forEach((s) => {
      const card = document.createElement("article");
      card.className = "place-card";
      card.setAttribute("role", "listitem");
      const detail = s.unc || s.mount_hint || "Pasta disponível no dashboard";
      card.innerHTML = `
        <span class="badge ${s.from_active_directory ? "ad" : ""}">${s.from_active_directory ? "Active Directory" : "Corporativo"}</span>
        <h4>${escapeHtml(s.label)}</h4>
        <p>${escapeHtml(detail)}</p>
        <div class="card-actions">
          <button type="button" class="btn primary" data-action="open" data-share="${escapeHtml(s.id)}">Abrir</button>
        </div>`;
      grid.appendChild(card);
    });
  }

  const cloudGrid = $("#cloud-grid");
  cloudGrid.innerHTML = "";
  (d.cloud_drives || []).forEach((c) => {
    const card = document.createElement("article");
    card.className = "cloud-card";
    card.setAttribute("role", "listitem");
    const status = c.mounted
      ? `<span class="badge ok">Montado${c.mode === "demo" ? " (demo)" : ""}</span>`
      : `<span class="badge">Disponível</span>`;
    const actions = c.mounted
      ? `<button type="button" class="btn primary" data-action="open" data-share="${escapeHtml(c.share_id || `cloud-${c.id}`)}">Abrir</button>
         <button type="button" class="btn secondary" data-action="unmount" data-provider="${escapeHtml(c.id)}">Desmontar</button>`
      : `<button type="button" class="btn primary" data-action="mount" data-provider="${escapeHtml(c.id)}">Montar</button>`;
    card.innerHTML = `
      ${status}
      <h4>${escapeHtml(c.label)}</h4>
      <p>${escapeHtml(c.description || "")}</p>
      <div class="card-actions">${actions}</div>`;
    cloudGrid.appendChild(card);
  });

  renderPlaces();
}

function renderComputers() {
  const grid = $("#computers-grid");
  const session = $("#computer-session");
  if (!grid) return;
  const isAdmin = state.dashboard?.user?.role === "admin";
  grid.hidden = false;
  if (session) session.hidden = true;
  grid.innerHTML = "";
  COMPUTERS.filter((c) => !c.adminOnly || isAdmin).forEach((c) => {
    const card = document.createElement("article");
    card.className = "place-card computer-card";
    card.setAttribute("role", "listitem");
    card.innerHTML = `
      <span class="badge">${escapeHtml(c.badge)}</span>
      <h4>${escapeHtml(c.title)}</h4>
      <p>${escapeHtml(c.description)}</p>
      <div class="card-actions">
        <button type="button" class="btn primary" data-action="computer" data-id="${escapeHtml(c.id)}">
          ${c.kind === "browser" ? "Abrir na aba Navegador" : "Conectar"}
        </button>
      </div>`;
    grid.appendChild(card);
  });
}

function openComputer(id) {
  const item = COMPUTERS.find((c) => c.id === id);
  if (!item) return;
  if (item.kind === "browser") {
    setPanel("browser");
    navigateBrowser("segportal://inicio");
    toast("Navegador aberto nesta mesma aba do SegPortal");
    return;
  }
  const grid = $("#computers-grid");
  const session = $("#computer-session");
  const frame = $("#computer-frame");
  const title = $("#computer-session-title");
  grid.hidden = true;
  session.hidden = false;
  title.textContent = item.title;
  frame.src = item.embed || "/browser/desktop.html";
}

function closeComputerSession() {
  const grid = $("#computers-grid");
  const session = $("#computer-session");
  const frame = $("#computer-frame");
  session.hidden = true;
  grid.hidden = false;
  frame.src = "about:blank";
}

function renderPlaces() {
  const d = state.dashboard;
  if (!d) return;
  const places = $("#files-places");
  const cloudPlaces = $("#files-cloud-places");
  places.innerHTML = "";
  cloudPlaces.innerHTML = "";
  (d.shares || []).forEach((s) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "place-btn" + (state.shareId === s.id ? " active" : "");
    btn.textContent = s.label;
    btn.dataset.action = "open";
    btn.dataset.share = s.id;
    if (s.source === "cloud") cloudPlaces.appendChild(btn);
    else places.appendChild(btn);
  });
  if (!cloudPlaces.children.length) {
    cloudPlaces.innerHTML =
      `<p class="empty" style="padding:0.35rem 0.65rem;margin:0;font-size:0.85rem">Monte OneDrive ou Google Drive no Início.</p>`;
  }
}

async function openShare(shareId, path = "") {
  state.shareId = shareId;
  state.path = path || "";
  setPanel("files");
  renderPlaces();
  await loadListing();
}

async function loadListing() {
  const tbody = $("#files-tbody");
  const empty = $("#files-empty");
  const crumbs = $("#breadcrumbs");
  if (!state.shareId) {
    tbody.innerHTML = "";
    empty.hidden = false;
    empty.textContent = "Selecione um local à esquerda.";
    crumbs.innerHTML = "";
    return;
  }
  const q = new URLSearchParams({ path: state.path });
  const data = await api(`/api/files/${encodeURIComponent(state.shareId)}?${q}`);
  renderBreadcrumbs(data);
  tbody.innerHTML = "";
  if (!data.entries.length) {
    empty.hidden = false;
    empty.textContent = "Esta pasta está vazia. Arraste arquivos aqui ou use Enviar.";
  } else {
    empty.hidden = true;
  }
  data.entries.forEach((e) => {
    const tr = document.createElement("tr");
    const icon = e.is_dir ? "DIR" : "DOC";
    const nameCell = e.is_dir
      ? `<button type="button" class="linkish" data-action="enter" data-path="${escapeHtml(e.path)}">${escapeHtml(e.name)}</button>`
      : `<span>${escapeHtml(e.name)}</span>`;
    tr.innerHTML = `
      <td><div class="name-cell"><span class="icon ${e.is_dir ? "dir" : ""}">${icon}</span>${nameCell}</div></td>
      <td>${e.is_dir ? "—" : formatSize(e.size)}</td>
      <td>${formatDate(e.modified)}</td>
      <td class="actions-col"><div class="row-actions">
        ${e.is_dir ? "" : `<a class="btn ghost" href="/api/files/${encodeURIComponent(state.shareId)}/download?path=${encodeURIComponent(e.path)}">Baixar</a>`}
        <button type="button" class="btn ghost" data-action="rename" data-path="${escapeHtml(e.path)}" data-name="${escapeHtml(e.name)}">Renomear</button>
        <button type="button" class="btn danger" data-action="delete" data-path="${escapeHtml(e.path)}">Excluir</button>
      </div></td>`;
    tbody.appendChild(tr);
  });
}

function renderBreadcrumbs(data) {
  const nav = $("#breadcrumbs");
  nav.innerHTML = "";
  const root = document.createElement("button");
  root.type = "button";
  root.textContent = (data.share && data.share.label) || "Raiz";
  root.addEventListener("click", () => openShare(state.shareId, ""));
  nav.appendChild(root);
  (data.breadcrumbs || []).forEach((c) => {
    const sep = document.createElement("span");
    sep.className = "sep";
    sep.textContent = "/";
    nav.appendChild(sep);
    const b = document.createElement("button");
    b.type = "button";
    b.textContent = c.name;
    b.addEventListener("click", () => openShare(state.shareId, c.path));
    nav.appendChild(b);
  });
}

async function refreshDashboard() {
  state.dashboard = await api("/api/dashboard");
  state.user = state.dashboard.user;
  renderDashboard();
}

async function mountCloud(provider) {
  const data = await api(`/api/cloud/${provider}/mount`, { method: "POST", body: {} });
  if (data.authorize_url) {
    window.location.href = data.authorize_url;
    return;
  }
  await refreshDashboard();
  toast(data.message || `${provider} montado`);
}

async function unmountCloud(provider) {
  await api(`/api/cloud/${provider}/unmount`, { method: "POST", body: {} });
  if (state.shareId === `cloud-${provider}`) {
    state.shareId = null;
    state.path = "";
  }
  await refreshDashboard();
  toast("Desmontado");
}

async function uploadFiles(fileList) {
  if (!state.shareId || !fileList?.length) return;
  for (const file of fileList) {
    const fd = new FormData();
    fd.append("path", state.path);
    fd.append("file", file);
    await api(`/api/files/${encodeURIComponent(state.shareId)}/upload`, { method: "POST", body: fd });
  }
  toast(`${fileList.length} arquivo(s) enviado(s)`);
  await loadListing();
}

async function handleAction(el) {
  const action = el.dataset.action;
  try {
    if (action === "open" && el.dataset.share) {
      await openShare(el.dataset.share);
      return;
    }
    if (action === "mount" && el.dataset.provider) {
      await mountCloud(el.dataset.provider);
      return;
    }
    if (action === "unmount" && el.dataset.provider) {
      await unmountCloud(el.dataset.provider);
      return;
    }
    if (action === "enter" && el.dataset.path != null) {
      await openShare(state.shareId, el.dataset.path);
      return;
    }
    if (action === "computer" && el.dataset.id) {
      openComputer(el.dataset.id);
      return;
    }
    if (action === "rename" && el.dataset.path) {
      const name = await askName("Renomear", el.dataset.name || "");
      if (!name) return;
      await api(`/api/files/${encodeURIComponent(state.shareId)}/rename`, {
        method: "POST",
        body: { path: el.dataset.path, new_name: name },
      });
      await loadListing();
      return;
    }
    if (action === "delete" && el.dataset.path) {
      if (!confirm("Excluir este item?")) return;
      await api(
        `/api/files/${encodeURIComponent(state.shareId)}?path=${encodeURIComponent(el.dataset.path)}`,
        { method: "DELETE" },
      );
      await loadListing();
    }
  } catch (err) {
    toast(err.message || "Falha na operação");
  }
}

function bindUi() {
  $("#login-form").addEventListener("submit", async (ev) => {
    ev.preventDefault();
    const err = $("#login-error");
    err.hidden = true;
    try {
      await api("/api/login", {
        method: "POST",
        body: {
          username: $("#username").value,
          password: $("#password").value,
          use_active_directory: $("#use-ad").checked,
        },
      });
      await refreshDashboard();
      showApp();
      setPanel("home");
      toast("Bem-vindo ao SegPortal");
    } catch (e) {
      err.textContent = e.message || "Falha no login";
      err.hidden = false;
    }
  });

  $("#btn-logout").addEventListener("click", async () => {
    try {
      await api("/api/logout", { method: "POST", body: {} });
    } catch {
      /* ignore */
    }
    state.user = null;
    state.dashboard = null;
    state.shareId = null;
    showLogin();
  });

  $("#btn-open-computers").addEventListener("click", () => setPanel("computers"));
  $("#btn-close-session")?.addEventListener("click", closeComputerSession);
  bindProductivityUi();

  $("#browser-url-form").addEventListener("submit", (ev) => {
    ev.preventDefault();
    navigateBrowser($("#browser-url").value);
  });
  $("#btn-browser-home").addEventListener("click", () => navigateBrowser("segportal://inicio"));
  $("#btn-browser-reload").addEventListener("click", () => {
    const frame = $("#browser-frame");
    frame.src = frame.src;
  });

  document.addEventListener("click", (ev) => {
    const nav = ev.target.closest(".nav-btn[data-panel]");
    if (nav) {
      ev.preventDefault();
      setPanel(nav.dataset.panel);
      if (nav.dataset.panel === "files" && !state.shareId) {
        const first = state.dashboard?.shares?.[0];
        if (first) openShare(first.id).catch((e) => toast(e.message));
      }
      return;
    }

    const quick = ev.target.closest(".quick-card[data-panel]");
    if (quick) {
      ev.preventDefault();
      setPanel(quick.dataset.panel);
      if (quick.dataset.panel === "files") {
        const first = state.dashboard?.shares?.[0];
        if (first) openShare(first.id).catch((e) => toast(e.message));
      }
      return;
    }

    const actionEl = ev.target.closest("[data-action]");
    if (actionEl) {
      ev.preventDefault();
      handleAction(actionEl);
    }
  });

  $("#btn-up").addEventListener("click", () => {
    if (!state.shareId) return;
    openShare(state.shareId, parentPath(state.path)).catch((e) => toast(e.message));
  });

  $("#btn-new-folder").addEventListener("click", async () => {
    if (!state.shareId) return toast("Selecione um local");
    const name = await askName("Nova pasta", "Nova pasta");
    if (!name) return;
    try {
      await api(`/api/files/${encodeURIComponent(state.shareId)}/mkdir`, {
        method: "POST",
        body: { path: state.path, name },
      });
      await loadListing();
    } catch (e) {
      toast(e.message);
    }
  });

  $("#file-input").addEventListener("change", (ev) => {
    uploadFiles(ev.target.files)
      .catch((e) => toast(e.message))
      .finally(() => {
        ev.target.value = "";
      });
  });

  const dz = $("#dropzone");
  ["dragenter", "dragover"].forEach((evt) =>
    dz.addEventListener(evt, (e) => {
      e.preventDefault();
      dz.classList.add("dragover");
    }),
  );
  ["dragleave", "drop"].forEach((evt) =>
    dz.addEventListener(evt, (e) => {
      e.preventDefault();
      dz.classList.remove("dragover");
    }),
  );
  dz.addEventListener("drop", (e) => {
    uploadFiles(e.dataTransfer.files).catch((err) => toast(err.message));
  });
}

async function boot() {
  bindUi();
  try {
    await refreshDashboard();
    showApp();
    setPanel("home");
    const params = new URLSearchParams(location.search);
    if (params.get("cloud") === "connected") toast("Conta de nuvem conectada");
  } catch {
    showLogin();
  }
}

boot();

/* —— Lembretes arrastáveis + calendário deslizante (Google / Microsoft) —— */

const productivity = {
  reminders: [],
  calendarProvider: "google",
  calendarSrc: { google: "", microsoft: "" },
  localMonth: new Date(),
  dragBound: false,
  calendarBound: false,
};

function storageKey(suffix) {
  const user = state.user?.username || state.dashboard?.user?.username || "anon";
  return `segportal.${suffix}.${user}`;
}

function setProductivityVisible(visible) {
  const panel = $("#reminders-panel");
  const tab = $("#calendar-tab");
  if (panel) panel.hidden = !visible;
  if (tab) tab.hidden = !visible;
  if (!visible) closeCalendarDrawer();
}

function loadReminders() {
  try {
    const raw = localStorage.getItem(storageKey("reminders"));
    productivity.reminders = raw ? JSON.parse(raw) : [];
  } catch {
    productivity.reminders = [];
  }
  if (!Array.isArray(productivity.reminders)) productivity.reminders = [];
}

function saveReminders() {
  localStorage.setItem(storageKey("reminders"), JSON.stringify(productivity.reminders));
}

function loadReminderPosition() {
  try {
    return JSON.parse(localStorage.getItem(storageKey("remindersPos")) || "null");
  } catch {
    return null;
  }
}

function saveReminderPosition(pos) {
  localStorage.setItem(storageKey("remindersPos"), JSON.stringify(pos));
}

function loadCalendarConfig() {
  try {
    const raw = JSON.parse(localStorage.getItem(storageKey("calendar")) || "{}");
    productivity.calendarProvider = raw.provider || "google";
    productivity.calendarSrc = {
      google: raw.google || "",
      microsoft: raw.microsoft || "",
    };
  } catch {
    productivity.calendarProvider = "google";
    productivity.calendarSrc = { google: "", microsoft: "" };
  }
}

function saveCalendarConfig() {
  localStorage.setItem(
    storageKey("calendar"),
    JSON.stringify({
      provider: productivity.calendarProvider,
      google: productivity.calendarSrc.google,
      microsoft: productivity.calendarSrc.microsoft,
    }),
  );
}

function clamp(n, min, max) {
  return Math.max(min, Math.min(max, n));
}

function placeRemindersPanel(x, y) {
  const panel = $("#reminders-panel");
  if (!panel) return;
  const pad = 12;
  const rect = panel.getBoundingClientRect();
  const left = clamp(x, pad, window.innerWidth - rect.width - pad);
  const top = clamp(y, pad, window.innerHeight - Math.min(rect.height, 120) - pad);
  panel.style.left = `${left}px`;
  panel.style.top = `${top}px`;
  panel.style.right = "auto";
  panel.style.bottom = "auto";
  saveReminderPosition({ left, top });
}

function applyReminderPosition() {
  const panel = $("#reminders-panel");
  if (!panel) return;
  const saved = loadReminderPosition();
  if (saved && Number.isFinite(saved.left) && Number.isFinite(saved.top)) {
    placeRemindersPanel(saved.left, saved.top);
    return;
  }
  // Posição padrão ergonomicamente à direita, abaixo do header
  placeRemindersPanel(window.innerWidth - 340, 88);
}

function renderReminders() {
  const list = $("#reminders-list");
  const empty = $("#reminders-empty");
  if (!list) return;
  list.innerHTML = "";
  const items = productivity.reminders;
  if (empty) empty.hidden = items.length > 0;
  items
    .slice()
    .sort((a, b) => Number(a.done) - Number(b.done) || (a.when || "").localeCompare(b.when || ""))
    .forEach((item) => {
      const li = document.createElement("li");
      li.className = "reminder-item" + (item.done ? " done" : "");
      li.dataset.id = item.id;
      const whenLabel = item.when
        ? new Date(item.when).toLocaleString("pt-BR", {
            day: "2-digit",
            month: "short",
            hour: "2-digit",
            minute: "2-digit",
          })
        : "Sem horário";
      li.innerHTML = `
        <p class="reminder-text">${escapeHtml(item.text)}</p>
        <div class="reminder-actions">
          <button type="button" class="btn ghost sm" data-reminder-action="toggle" title="${item.done ? "Reabrir" : "Concluir"}">${item.done ? "↺" : "✓"}</button>
          <button type="button" class="btn ghost sm" data-reminder-action="delete" title="Excluir">✕</button>
        </div>
        <p class="reminder-when">${escapeHtml(whenLabel)}</p>`;
      list.appendChild(li);
    });
}

function focusRemindersPanel() {
  const panel = $("#reminders-panel");
  if (!panel) return;
  panel.hidden = false;
  panel.classList.remove("collapsed");
  const collapseBtn = $("#btn-reminders-collapse");
  if (collapseBtn) {
    collapseBtn.textContent = "−";
    collapseBtn.setAttribute("aria-expanded", "true");
  }
  panel.classList.remove("pulse");
  void panel.offsetWidth;
  panel.classList.add("pulse");
  $("#reminder-text")?.focus();
}

function initRemindersPanel() {
  loadReminders();
  renderReminders();
  applyReminderPosition();
  if (productivity.dragBound) return;
  productivity.dragBound = true;

  const panel = $("#reminders-panel");
  const handle = $("#reminders-drag");
  if (!panel || !handle) return;

  let dragging = false;
  let offsetX = 0;
  let offsetY = 0;

  const onMove = (ev) => {
    if (!dragging) return;
    const point = ev.touches ? ev.touches[0] : ev;
    placeRemindersPanel(point.clientX - offsetX, point.clientY - offsetY);
  };
  const onUp = () => {
    if (!dragging) return;
    dragging = false;
    document.body.style.userSelect = "";
  };

  handle.addEventListener("pointerdown", (ev) => {
    if (ev.target.closest("button")) return;
    const rect = panel.getBoundingClientRect();
    dragging = true;
    offsetX = ev.clientX - rect.left;
    offsetY = ev.clientY - rect.top;
    document.body.style.userSelect = "none";
    handle.setPointerCapture?.(ev.pointerId);
  });
  handle.addEventListener("pointermove", onMove);
  handle.addEventListener("pointerup", onUp);
  handle.addEventListener("pointercancel", onUp);
  window.addEventListener("resize", () => applyReminderPosition());

  $("#btn-reminders-collapse")?.addEventListener("click", () => {
    const collapsed = panel.classList.toggle("collapsed");
    const btn = $("#btn-reminders-collapse");
    btn.textContent = collapsed ? "+" : "−";
    btn.setAttribute("aria-expanded", String(!collapsed));
  });

  $("#reminder-form")?.addEventListener("submit", (ev) => {
    ev.preventDefault();
    const text = $("#reminder-text").value.trim();
    if (!text) return;
    const when = $("#reminder-when").value || "";
    productivity.reminders.unshift({
      id: `r-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
      text,
      when,
      done: false,
    });
    saveReminders();
    renderReminders();
    $("#reminder-form").reset();
    toast("Lembrete adicionado");
  });

  $("#reminders-list")?.addEventListener("click", (ev) => {
    const btn = ev.target.closest("[data-reminder-action]");
    if (!btn) return;
    const itemEl = btn.closest(".reminder-item");
    const id = itemEl?.dataset.id;
    const item = productivity.reminders.find((r) => r.id === id);
    if (!item) return;
    if (btn.dataset.reminderAction === "toggle") item.done = !item.done;
    if (btn.dataset.reminderAction === "delete") {
      productivity.reminders = productivity.reminders.filter((r) => r.id !== id);
    }
    saveReminders();
    renderReminders();
  });
}

function openCalendarDrawer() {
  const drawer = $("#calendar-drawer");
  const backdrop = $("#calendar-backdrop");
  const tab = $("#calendar-tab");
  const navBtn = $("#btn-open-calendar");
  if (!drawer) return;
  drawer.hidden = false;
  drawer.setAttribute("aria-hidden", "false");
  requestAnimationFrame(() => drawer.classList.add("open"));
  if (backdrop) backdrop.hidden = false;
  if (tab) tab.setAttribute("aria-expanded", "true");
  if (navBtn) navBtn.setAttribute("aria-expanded", "true");
  renderCalendarView();
}

function closeCalendarDrawer() {
  const drawer = $("#calendar-drawer");
  const backdrop = $("#calendar-backdrop");
  const tab = $("#calendar-tab");
  const navBtn = $("#btn-open-calendar");
  if (!drawer) return;
  drawer.classList.remove("open");
  drawer.setAttribute("aria-hidden", "true");
  setTimeout(() => {
    if (!drawer.classList.contains("open")) drawer.hidden = true;
  }, 280);
  if (backdrop) backdrop.hidden = true;
  if (tab) tab.setAttribute("aria-expanded", "false");
  if (navBtn) navBtn.setAttribute("aria-expanded", "false");
}

function renderLocalMonth() {
  const host = $("#calendar-local");
  if (!host) return;
  const cursor = productivity.localMonth;
  const year = cursor.getFullYear();
  const month = cursor.getMonth();
  const first = new Date(year, month, 1);
  const startPad = (first.getDay() + 6) % 7; // semana começa na segunda
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const title = cursor.toLocaleDateString("pt-BR", { month: "long", year: "numeric" });
  const dows = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"];
  const today = new Date();
  let cells = "";
  for (let i = 0; i < startPad; i += 1) cells += `<div class="day muted"></div>`;
  for (let d = 1; d <= daysInMonth; d += 1) {
    const isToday =
      d === today.getDate() && month === today.getMonth() && year === today.getFullYear();
    cells += `<div class="day${isToday ? " today" : ""}">${d}</div>`;
  }
  host.innerHTML = `
    <div class="cal-nav">
      <button type="button" class="btn ghost sm" id="cal-prev-month" aria-label="Mês anterior">←</button>
      <h3 style="text-transform:capitalize;margin:0">${escapeHtml(title)}</h3>
      <button type="button" class="btn ghost sm" id="cal-next-month" aria-label="Próximo mês">→</button>
    </div>
    <div class="cal-month-grid">
      ${dows.map((d) => `<div class="dow">${d}</div>`).join("")}
      ${cells}
    </div>
    <p class="calendar-config-hint">Agenda local do SegPortal. Conecte Google ou Microsoft para ver eventos corporativos.</p>`;
  $("#cal-prev-month")?.addEventListener("click", () => {
    productivity.localMonth = new Date(year, month - 1, 1);
    renderLocalMonth();
  });
  $("#cal-next-month")?.addEventListener("click", () => {
    productivity.localMonth = new Date(year, month + 1, 1);
    renderLocalMonth();
  });
}

function renderCalendarView() {
  const provider = productivity.calendarProvider;
  $$(".cal-tab").forEach((btn) => {
    const active = btn.dataset.calProvider === provider;
    btn.classList.toggle("active", active);
    btn.setAttribute("aria-selected", String(active));
  });
  const input = $("#calendar-src-input");
  const frame = $("#calendar-frame");
  const local = $("#calendar-local");
  const placeholder = $("#calendar-placeholder");
  if (input) {
    input.value =
      provider === "local" ? "" : productivity.calendarSrc[provider] || "";
    input.disabled = provider === "local";
    input.placeholder =
      provider === "microsoft"
        ? "URL de incorporação do Outlook / Microsoft 365"
        : provider === "google"
          ? "URL de incorporação do Google Calendar"
          : "Agenda local do SegPortal";
  }
  if (provider === "local") {
    if (frame) {
      frame.hidden = true;
      frame.src = "about:blank";
    }
    if (placeholder) placeholder.hidden = true;
    if (local) {
      local.hidden = false;
      renderLocalMonth();
    }
    return;
  }
  if (local) local.hidden = true;
  const src = productivity.calendarSrc[provider];
  if (src) {
    if (placeholder) placeholder.hidden = true;
    if (frame) {
      frame.hidden = false;
      if (frame.src !== src) frame.src = src;
    }
  } else {
    if (frame) {
      frame.hidden = true;
      frame.src = "about:blank";
    }
    if (placeholder) placeholder.hidden = false;
  }
}

function initCalendarDrawer() {
  loadCalendarConfig();
  renderCalendarView();
  if (productivity.calendarBound) return;
  productivity.calendarBound = true;
}

function bindProductivityUi() {
  $("#btn-open-calendar")?.addEventListener("click", () => openCalendarDrawer());
  $("#calendar-tab")?.addEventListener("click", () => openCalendarDrawer());
  $("#btn-close-calendar")?.addEventListener("click", () => closeCalendarDrawer());
  $("#calendar-backdrop")?.addEventListener("click", () => closeCalendarDrawer());
  $("#btn-focus-reminders")?.addEventListener("click", () => focusRemindersPanel());
  $("#prod-open-reminders")?.addEventListener("click", () => focusRemindersPanel());
  $("#prod-open-calendar")?.addEventListener("click", () => openCalendarDrawer());

  $$(".cal-tab").forEach((btn) => {
    btn.addEventListener("click", () => {
      productivity.calendarProvider = btn.dataset.calProvider || "google";
      saveCalendarConfig();
      renderCalendarView();
    });
  });

  $("#btn-save-calendar-src")?.addEventListener("click", () => {
    const provider = productivity.calendarProvider;
    if (provider === "local") {
      toast("Agenda local não usa URL externa");
      return;
    }
    const value = ($("#calendar-src-input")?.value || "").trim();
    if (value && !/^https:\/\//i.test(value)) {
      toast("Use uma URL https:// de incorporação");
      return;
    }
    productivity.calendarSrc[provider] = value;
    saveCalendarConfig();
    renderCalendarView();
    toast(value ? "Calendário conectado" : "URL removida");
  });

  document.addEventListener("keydown", (ev) => {
    if (ev.key === "Escape") closeCalendarDrawer();
  });
}
