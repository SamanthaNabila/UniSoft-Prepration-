const API_URL = '/api/todos';

const form = document.getElementById('todo-form');
const input = document.getElementById('todo-input');
const priorityInput = document.getElementById('priority-input');
const list = document.getElementById('todo-list');
const errorMessage = document.getElementById('error-message');

function showError(message) {
    errorMessage.textContent = message || '';
}

async function fetchTodos() {
    const res = await fetch(API_URL);
    const todos = await res.json();
    renderTodos(todos);
}

function renderTodos(todos) {
    list.innerHTML = '';

    if (todos.length === 0) {
        const empty = document.createElement('li');
        empty.className = 'empty';
        empty.textContent = 'No todos yet. Add one above!';
        list.appendChild(empty);
        return;
    }

    todos.forEach(todo => {
        const li = document.createElement('li');
        li.className = todo.completed ? 'completed' : '';

        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.checked = todo.completed;
        checkbox.addEventListener('change', () => toggleTodo(todo.id, checkbox.checked));

        const span = document.createElement('span');
        span.textContent = todo.title;

        const badge = document.createElement('span');
        badge.className = `priority-badge ${todo.priority.toLowerCase()}`;
        badge.textContent = todo.priority;

        const prioritySelect = document.createElement('select');
        prioritySelect.className = 'priority-select';
        ['LOW', 'MEDIUM', 'HIGH'].forEach(level => {
            const option = document.createElement('option');
            option.value = level;
            option.textContent = level;
            if (level === todo.priority) option.selected = true;
            prioritySelect.appendChild(option);
        });
        prioritySelect.addEventListener('change', () => updatePriority(todo.id, prioritySelect.value));

        const deleteBtn = document.createElement('button');
        deleteBtn.textContent = 'Delete';
        deleteBtn.className = 'delete-btn';
        deleteBtn.addEventListener('click', () => deleteTodo(todo.id));

        li.appendChild(checkbox);
        li.appendChild(span);
        li.appendChild(badge);
        li.appendChild(prioritySelect);
        li.appendChild(deleteBtn);
        list.appendChild(li);
    });
}

async function addTodo(title, priority) {
    const res = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, priority }),
    });
    const data = await res.json();
    if (!res.ok) {
        showError(data.error || 'Failed to add todo');
        return;
    }
    showError('');
    fetchTodos();
}

async function toggleTodo(id, completed) {
    const res = await fetch(`${API_URL}/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ completed }),
    });
    const data = await res.json();
    if (!res.ok) {
        showError(data.error || 'Failed to update todo');
        return;
    }
    showError('');
    fetchTodos();
}

async function updatePriority(id, priority) {
    const res = await fetch(`${API_URL}/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ priority }),
    });
    const data = await res.json();
    if (!res.ok) {
        showError(data.error || 'Failed to update priority');
        return;
    }
    showError('');
    fetchTodos();
}

async function deleteTodo(id) {
    await fetch(`${API_URL}/${id}`, { method: 'DELETE' });
    fetchTodos();
}

form.addEventListener('submit', (e) => {
    e.preventDefault();
    const title = input.value.trim();
    if (!title) return;
    addTodo(title, priorityInput.value);
    input.value = '';
    priorityInput.value = 'MEDIUM';
});

fetchTodos();
