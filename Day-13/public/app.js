const API_URL = '/api/todos';

const form = document.getElementById('todo-form');
const input = document.getElementById('todo-input');
const prioritySelect = document.getElementById('todo-priority');
const list = document.getElementById('todo-list');

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

        const prioritySelectEl = document.createElement('select');
        ['LOW', 'MEDIUM', 'HIGH'].forEach(level => {
            const option = document.createElement('option');
            option.value = level;
            option.textContent = level;
            if (todo.priority === level) option.selected = true;
            prioritySelectEl.appendChild(option);
        });
        prioritySelectEl.addEventListener('change', () => updatePriority(todo.id, prioritySelectEl.value));

        const deleteBtn = document.createElement('button');
        deleteBtn.textContent = 'Delete';
        deleteBtn.className = 'delete-btn';
        deleteBtn.addEventListener('click', () => deleteTodo(todo.id));

        li.appendChild(checkbox);
        li.appendChild(span);
        li.appendChild(prioritySelectEl);
        li.appendChild(deleteBtn);
        list.appendChild(li);
    });
}

async function addTodo(title, priority) {
    await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, priority }),
    });
    fetchTodos();
}

async function toggleTodo(id, completed) {
    await fetch(`${API_URL}/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ completed }),
    });
    fetchTodos();
}

async function updatePriority(id, priority) {
    await fetch(`${API_URL}/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ priority }),
    });
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
    addTodo(title, prioritySelect.value);
    input.value = '';
    prioritySelect.value = 'MEDIUM';
});

fetchTodos();
