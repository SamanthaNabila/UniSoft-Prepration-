require('dotenv').config();
const express = require('express');
const path = require('path');
const pool = require('./db');

const app = express();
const PORT = process.env.PORT || 3000;

const VALID_PRIORITIES = ['LOW', 'MEDIUM', 'HIGH'];
const TITLE_MAX_LENGTH = 100;

app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// --- Validation helpers -----------------------------------------------

// Validates a todo title. `required` controls whether a missing title is an
// error (POST, where a title must be supplied) or acceptable (PUT, where the
// title is optional and other fields may be updated instead).
function validateTitle(title, { required }) {
    if (title === undefined || title === null) {
        if (required) {
            return { error: 'Title is required' };
        }
        return { value: undefined };
    }

    if (typeof title !== 'string') {
        return { error: 'Title must be a string' };
    }

    const trimmed = title.trim();

    if (trimmed.length === 0) {
        return { error: 'Title cannot be empty' };
    }

    if (trimmed.length > TITLE_MAX_LENGTH) {
        return { error: `Title cannot exceed ${TITLE_MAX_LENGTH} characters` };
    }

    return { value: trimmed };
}

// Validates a priority value. `required` mirrors validateTitle's behavior.
function validatePriority(priority, { required }) {
    if (priority === undefined || priority === null) {
        if (required) {
            return { error: 'Priority is required' };
        }
        return { value: undefined };
    }

    if (typeof priority !== 'string') {
        return { error: 'Priority must be a string' };
    }

    const normalized = priority.trim().toUpperCase();

    if (!VALID_PRIORITIES.includes(normalized)) {
        return { error: `Priority must be one of: ${VALID_PRIORITIES.join(', ')}` };
    }

    return { value: normalized };
}

// Validates a completed flag. Accepts a real boolean only — string coercion
// ("true"/"false") is intentionally rejected to avoid ambiguous input from
// callers, since JSON bodies should already send real booleans.
function validateCompleted(completed, { required }) {
    if (completed === undefined || completed === null) {
        if (required) {
            return { error: 'Completed status is required' };
        }
        return { value: undefined };
    }

    if (typeof completed !== 'boolean') {
        return { error: 'Completed must be a boolean' };
    }

    return { value: completed };
}

// Validates a route param `id`, ensuring it's a positive integer.
function validateId(rawId) {
    if (!/^\d+$/.test(rawId)) {
        return { error: 'Id must be a positive integer' };
    }
    return { value: parseInt(rawId, 10) };
}

// --- Routes --------------------------------------------------------------

// GET all todos
app.get('/api/todos', async (req, res) => {
    try {
        const result = await pool.query('SELECT * FROM todos ORDER BY id ASC');
        res.json(result.rows);
    } catch (err) {
        console.error(err);
        res.status(500).json({ error: 'Failed to fetch todos' });
    }
});

// GET todos filtered by completion status and/or priority
// Examples: /api/todos/filter?completed=true&priority=HIGH
app.get('/api/todos/filter', async (req, res) => {
    try {
        const { completed, priority } = req.query;

        const conditions = [];
        const values = [];

        if (completed !== undefined) {
            if (completed !== 'true' && completed !== 'false') {
                return res.status(400).json({ error: 'completed must be "true" or "false"' });
            }
            values.push(completed === 'true');
            conditions.push(`completed = $${values.length}`);
        }

        if (priority !== undefined) {
            const { value, error } = validatePriority(priority, { required: false });
            if (error) {
                return res.status(400).json({ error });
            }
            values.push(value);
            conditions.push(`priority = $${values.length}`);
        }

        const whereClause = conditions.length > 0 ? `WHERE ${conditions.join(' AND ')}` : '';
        const result = await pool.query(
            `SELECT * FROM todos ${whereClause} ORDER BY id ASC`,
            values
        );
        res.json(result.rows);
    } catch (err) {
        console.error(err);
        res.status(500).json({ error: 'Failed to filter todos' });
    }
});

// POST a new todo
app.post('/api/todos', async (req, res) => {
    try {
        const body = req.body || {};

        const titleResult = validateTitle(body.title, { required: true });
        if (titleResult.error) {
            return res.status(400).json({ error: titleResult.error });
        }

        const priorityResult = validatePriority(body.priority, { required: false });
        if (priorityResult.error) {
            return res.status(400).json({ error: priorityResult.error });
        }
        const priority = priorityResult.value || 'MEDIUM';

        const result = await pool.query(
            'INSERT INTO todos (title, priority) VALUES ($1, $2) RETURNING *',
            [titleResult.value, priority]
        );
        res.status(201).json(result.rows[0]);
    } catch (err) {
        console.error(err);
        res.status(500).json({ error: 'Failed to create todo' });
    }
});

// PUT update a todo (title, completed, and/or priority)
app.put('/api/todos/:id', async (req, res) => {
    try {
        const idResult = validateId(req.params.id);
        if (idResult.error) {
            return res.status(400).json({ error: idResult.error });
        }
        const id = idResult.value;

        const body = req.body || {};

        if (body.title === undefined && body.completed === undefined && body.priority === undefined) {
            return res.status(400).json({ error: 'At least one of title, completed, or priority must be provided' });
        }

        const titleResult = validateTitle(body.title, { required: false });
        if (titleResult.error) {
            return res.status(400).json({ error: titleResult.error });
        }

        const completedResult = validateCompleted(body.completed, { required: false });
        if (completedResult.error) {
            return res.status(400).json({ error: completedResult.error });
        }

        const priorityResult = validatePriority(body.priority, { required: false });
        if (priorityResult.error) {
            return res.status(400).json({ error: priorityResult.error });
        }

        const existing = await pool.query('SELECT * FROM todos WHERE id = $1', [id]);
        if (existing.rows.length === 0) {
            return res.status(404).json({ error: 'Todo not found' });
        }

        const current = existing.rows[0];
        const newTitle = titleResult.value !== undefined ? titleResult.value : current.title;
        const newCompleted = completedResult.value !== undefined ? completedResult.value : current.completed;
        const newPriority = priorityResult.value !== undefined ? priorityResult.value : current.priority;

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

// DELETE a todo
app.delete('/api/todos/:id', async (req, res) => {
    try {
        const idResult = validateId(req.params.id);
        if (idResult.error) {
            return res.status(400).json({ error: idResult.error });
        }

        const result = await pool.query('DELETE FROM todos WHERE id = $1 RETURNING *', [idResult.value]);
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
