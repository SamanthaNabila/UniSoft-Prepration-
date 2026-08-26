require('dotenv').config();
const express = require('express');
const path = require('path');
const pool = require('./db');

const app = express();
const PORT = process.env.PORT || 3000;

const VALID_PRIORITIES = ['LOW', 'MEDIUM', 'HIGH'];
const MAX_TITLE_LENGTH = 100;

app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

/**
 * Middleware: validates and normalizes the body of a create/update todo request.
 * `title` is required (and re-validated if present) on POST, optional on PUT;
 * when supplied it must be a non-empty string no longer than 100 characters.
 * `priority`, when supplied, must be one of LOW, MEDIUM, HIGH (case-insensitive);
 * defaults to MEDIUM on create. Normalized values are written back onto `req.body`.
 */
const validateTodoBody = (req, res, next) => {
    const body = req.body && typeof req.body === 'object' ? req.body : {};
    const isCreate = req.method === 'POST';
    const { title, priority } = body;

    if (isCreate || title !== undefined) {
        if (typeof title !== 'string' || !title.trim()) {
            return res.status(400).json({ error: 'Title is required' });
        }
        const trimmedTitle = title.trim();
        if (trimmedTitle.length > MAX_TITLE_LENGTH) {
            return res.status(400).json({ error: `Title must be at most ${MAX_TITLE_LENGTH} characters` });
        }
        body.title = trimmedTitle;
    }

    if (priority !== undefined) {
        if (typeof priority !== 'string' || !VALID_PRIORITIES.includes(priority.toUpperCase())) {
            return res.status(400).json({ error: 'Priority must be one of LOW, MEDIUM, HIGH' });
        }
        body.priority = priority.toUpperCase();
    } else if (isCreate) {
        body.priority = 'MEDIUM';
    }

    req.body = body;
    next();
};

/**
 * Middleware: validates the optional `completed` and `priority` query params
 * on the filter endpoint, normalizing them onto `req.query`.
 */
const validateFilterQuery = (req, res, next) => {
    const { completed, priority } = req.query;

    if (completed !== undefined) {
        if (completed !== 'true' && completed !== 'false') {
            return res.status(400).json({ error: 'Completed must be true or false' });
        }
        req.query.completed = completed === 'true';
    }

    if (priority !== undefined) {
        if (typeof priority !== 'string' || !VALID_PRIORITIES.includes(priority.toUpperCase())) {
            return res.status(400).json({ error: 'Priority must be one of LOW, MEDIUM, HIGH' });
        }
        req.query.priority = priority.toUpperCase();
    }

    next();
};

/**
 * GET /api/todos
 * Returns all todos, ordered by id ascending.
 */
app.get('/api/todos', async (req, res) => {
    try {
        const result = await pool.query('SELECT * FROM todos ORDER BY id ASC');
        res.json(result.rows);
    } catch (err) {
        console.error(err);
        res.status(500).json({ error: 'Failed to fetch todos' });
    }
});

/**
 * GET /api/todos/filter
 * Returns todos filtered by optional `completed` (true/false) and/or
 * `priority` (LOW/MEDIUM/HIGH) query params. With no params, behaves like
 * GET /api/todos.
 */
app.get('/api/todos/filter', validateFilterQuery, async (req, res) => {
    try {
        const { completed, priority } = req.query;
        const conditions = [];
        const values = [];

        if (completed !== undefined) {
            values.push(completed);
            conditions.push(`completed = $${values.length}`);
        }
        if (priority !== undefined) {
            values.push(priority);
            conditions.push(`priority = $${values.length}`);
        }

        const whereClause = conditions.length ? `WHERE ${conditions.join(' AND ')}` : '';
        const result = await pool.query(`SELECT * FROM todos ${whereClause} ORDER BY id ASC`, values);
        res.json(result.rows);
    } catch (err) {
        console.error(err);
        res.status(500).json({ error: 'Failed to filter todos' });
    }
});

/**
 * POST /api/todos
 * Creates a new todo from `title` (required) and `priority` (optional,
 * defaults to MEDIUM).
 */
app.post('/api/todos', validateTodoBody, async (req, res) => {
    try {
        const { title, priority } = req.body;
        const result = await pool.query(
            'INSERT INTO todos (title, priority) VALUES ($1, $2) RETURNING *',
            [title, priority]
        );
        res.status(201).json(result.rows[0]);
    } catch (err) {
        console.error(err);
        res.status(500).json({ error: 'Failed to create todo' });
    }
});

/**
 * PUT /api/todos/:id
 * Updates an existing todo. Accepts any subset of `title`, `completed`,
 * and `priority`; omitted fields keep their current value.
 */
app.put('/api/todos/:id', validateTodoBody, async (req, res) => {
    try {
        const { id } = req.params;
        const { title, completed, priority } = req.body;

        const existing = await pool.query('SELECT * FROM todos WHERE id = $1', [id]);
        if (existing.rows.length === 0) {
            return res.status(404).json({ error: 'Todo not found' });
        }

        const current = existing.rows[0];
        const newTitle = title !== undefined ? title : current.title;
        const newCompleted = completed !== undefined ? completed : current.completed;
        const newPriority = priority !== undefined ? priority : current.priority;

        const result = await pool.query(
            'UPDATE todos SET title = $1, completed = $2, priority = $3 WHERE id = $4 RETURNING *',
            [newTitle, newCompleted, newPriority, id]
        );
        res.json(result.rows[0]);
    } catch (err) {
        console.error(err);
        res.status(500).json({ error: 'Failed to update todo' });
    }
});

/**
 * DELETE /api/todos/:id
 * Deletes a todo by id.
 */
app.delete('/api/todos/:id', async (req, res) => {
    try {
        const { id } = req.params;
        const result = await pool.query('DELETE FROM todos WHERE id = $1 RETURNING *', [id]);
        if (result.rows.length === 0) {
            return res.status(404).json({ error: 'Todo not found' });
        }
        res.json({ message: 'Todo deleted', todo: result.rows[0] });
    } catch (err) {
        console.error(err);
        res.status(500).json({ error: 'Failed to delete todo' });
    }
});

app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
});
