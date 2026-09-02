"use strict";

const API = "/api";

const state = {
  filters: { search: "", status: "", priority: "", sort: "created_desc" },
  editingId: null,
};

/* ------------------------------------------------------------------ helpers */

async function request(path, options = {}) {
  const res = await fetch(API + path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  if (res.status === 204) return null;

  let body = null;
  try {
    body = await res.json();
  } catch (_) {
    /* no JSON body */
  }

  if (!res.ok) {
    const message = body && body.error ? body.error : `Request failed (${res.status})`;
    const err = new Error(message);
    err.details = body && body.details ? body.details : null;
    throw err;
  }
  return body;
}

function showMessage(text) {
  const el = document.getElementById("message");
  el.textContent = text;
  el.hidden = !text;
}

function escapeHtml(value) {
  const div = document.createElement("div");
  div.textContent = value == null ? "" : String(value);
  return div.innerHTML;
}

/* ------------------------------------------------------------------ rendering */

function taskCard(task) {
  const el = document.createElement("article");
  el.className = `task-card priority-${task.priority} status-${task.status}`;

  const due = task.due_date
    ? `<span class="badge">Due ${escapeHtml(task.due_date)}</span>`
    : "";
  const desc = task.description
    ? `<p class="task-desc">${escapeHtml(task.description)}</p>`
    : "";

  el.innerHTML = `
    <div class="task-main">
      <p class="task-title">${escapeHtml(task.title)}</p>
      ${desc}
      <div class="task-meta">
        <span class="badge priority-${task.priority}">${task.priority}</span>
        <span class="badge status-${task.status}">${task.status}</span>
        ${due}
      </div>
    </div>
    <div class="task-actions">
      <button class="btn btn-small" data-action="toggle">
        ${task.status === "completed" ? "Reopen" : "Complete"}
      </button>
      <button class="btn btn-small" data-action="edit">Edit</button>
      <button class="btn btn-small btn-danger" data-action="delete">Delete</button>
    </div>
  `;

  el.querySelector('[data-action="toggle"]').addEventListener("click", () =>
    toggleStatus(task)
  );
  el.querySelector('[data-action="edit"]').addEventListener("click", () =>
    openDialog(task)
  );
  el.querySelector('[data-action="delete"]').addEventListener("click", () =>
    deleteTask(task)
  );

  return el;
}

function renderTasks(tasks) {
  const list = document.getElementById("task-list");
  list.innerHTML = "";
  tasks.forEach((t) => list.appendChild(taskCard(t)));
  document.getElementById("empty-state").hidden = tasks.length > 0;
}

function renderDashboard(stats) {
  document.getElementById("stat-total").textContent = stats.total_tasks;
  document.getElementById("stat-pending").textContent = stats.pending_tasks;
  document.getElementById("stat-completed").textContent = stats.completed_tasks;
  document.getElementById("stat-high").textContent = stats.high_priority_tasks;
}

/* ------------------------------------------------------------------ data ops */

async function refresh() {
  showMessage("");
  try {
    const params = new URLSearchParams();
    const { search, status, priority, sort } = state.filters;
    if (search) params.set("search", search);
    if (status) params.set("status", status);
    if (priority) params.set("priority", priority);
    if (sort) params.set("sort", sort);

    const [tasks, stats] = await Promise.all([
      request("/tasks?" + params.toString()),
      request("/dashboard"),
    ]);
    renderTasks(tasks);
    renderDashboard(stats);
  } catch (err) {
    showMessage(err.message);
  }
}

async function toggleStatus(task) {
  const next = task.status === "completed" ? "pending" : "completed";
  try {
    await request(`/tasks/${task.id}`, {
      method: "PATCH",
      body: JSON.stringify({ status: next }),
    });
    refresh();
  } catch (err) {
    showMessage(err.message);
  }
}

async function deleteTask(task) {
  if (!window.confirm(`Delete "${task.title}"?`)) return;
  try {
    await request(`/tasks/${task.id}`, { method: "DELETE" });
    refresh();
  } catch (err) {
    showMessage(err.message);
  }
}

/* ------------------------------------------------------------------ dialog */

const dialog = document.getElementById("task-dialog");
const form = document.getElementById("task-form");
const formError = document.getElementById("form-error");

function openDialog(task) {
  state.editingId = task ? task.id : null;
  document.getElementById("dialog-title").textContent = task ? "Edit Task" : "New Task";
  formError.hidden = true;

  form.title.value = task ? task.title : "";
  form.description.value = task ? task.description : "";
  form.priority.value = task ? task.priority : "medium";
  form.status.value = task ? task.status : "pending";
  form.due_date.value = task && task.due_date ? task.due_date : "";

  dialog.showModal();
}

function closeDialog() {
  dialog.close();
  state.editingId = null;
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  formError.hidden = true;

  const payload = {
    title: form.title.value.trim(),
    description: form.description.value,
    priority: form.priority.value,
    status: form.status.value,
    due_date: form.due_date.value || null,
  };

  const editingId = state.editingId;
  const path = editingId ? `/tasks/${editingId}` : "/tasks";
  const method = editingId ? "PUT" : "POST";

  try {
    await request(path, { method, body: JSON.stringify(payload) });
    closeDialog();
    refresh();
  } catch (err) {
    const detail = err.details
      ? Object.entries(err.details)
          .map(([k, v]) => `${k}: ${v}`)
          .join(" | ")
      : "";
    formError.textContent = detail ? `${err.message} - ${detail}` : err.message;
    formError.hidden = false;
  }
});

/* ------------------------------------------------------------------ wiring */

document.getElementById("new-task-btn").addEventListener("click", () => openDialog(null));
document.getElementById("dialog-cancel").addEventListener("click", closeDialog);

let searchTimer;
document.getElementById("search-input").addEventListener("input", (e) => {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(() => {
    state.filters.search = e.target.value.trim();
    refresh();
  }, 250);
});

document.getElementById("filter-status").addEventListener("change", (e) => {
  state.filters.status = e.target.value;
  refresh();
});
document.getElementById("filter-priority").addEventListener("change", (e) => {
  state.filters.priority = e.target.value;
  refresh();
});
document.getElementById("sort-by").addEventListener("change", (e) => {
  state.filters.sort = e.target.value;
  refresh();
});
document.getElementById("clear-filters").addEventListener("click", () => {
  state.filters = { search: "", status: "", priority: "", sort: "created_desc" };
  document.getElementById("search-input").value = "";
  document.getElementById("filter-status").value = "";
  document.getElementById("filter-priority").value = "";
  document.getElementById("sort-by").value = "created_desc";
  refresh();
});

refresh();
