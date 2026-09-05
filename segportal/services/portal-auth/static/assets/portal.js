/**
 * SegPortal — dashboard pessoal + gerenciador de arquivos
 * IDs alinhados com static/index.html
 */

const state = {
  user: null,
  dashboard: null,
  panel: "home",
  shareId: null,
  path: "",
};

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
}

function showApp() {
  $("#view-login").hidden = true;
  $("#view-app").hidden = false;
}

function setPanel(name) {
  state.panel = name;
  $$(".nav-btn").forEach((b) => b.classList.toggle("active", b.dataset.panel === name));
  $$(".panel").forEach((p) => {
    p.hidden = p.id !== `panel-${name}`;
  });
  const titles = { home: "Dashboard pessoal", files: "Arquivos", sessions: "Sessões remotas" };
  const sub = $("#nav-subtitle");
  if (sub) sub.textContent = titles[name] || "SegPortal";
  if (name === "files") {
    if (state.shareId) loadListing().catch((e) => toast(e.message));
    else renderPlaces();
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

/** Diálogo acessível no lugar de window.prompt (melhor ergonomia). */
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
      if (submitter && submitter.value === "cancel") {
        dlg.returnValue = "cancel";
      } else {
        dlg.returnValue = "ok";
      }
    };
    form.addEventListener("submit", onSubmit);
    dlg.addEventListener("close", onClose);
    dlg.showModal();
    input.focus();
    input.select();
  });
}

function renderDashboard() {
  const d = state.dashboard;
  if (!d) return;
  const u = d.user;
  $("#user-name").textContent = u.display_name;
  $("#user-meta").textContent = `${u.username} · ${u.auth_source === "ldap" ? "Active Directory" : "Local"} · ${u.role}`;
  $("#hello-name").textContent = (u.display_name || "usuário").split(" ")[0];
  const guac = d.guacamole_url || "http://localhost:8080/guacamole";
  $("#btn-open-guacamole").href = guac;
  $("#btn-sessions-guac").href = guac;
  $("#btn-session-browser").href = guac;

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

  $("#quick-browser").addEventListener("click", () => {
    const guac = state.dashboard?.guacamole_url || "http://localhost:8080/guacamole";
    window.open(guac, "_blank", "noopener");
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
