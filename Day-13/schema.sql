CREATE TABLE IF NOT EXISTS todos (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    priority VARCHAR(10) NOT NULL DEFAULT 'MEDIUM' CHECK (priority IN ('LOW', 'MEDIUM', 'HIGH')),
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Safe to re-run against a pre-existing table created before the priority column was added.
ALTER TABLE todos ADD COLUMN IF NOT EXISTS priority VARCHAR(10) NOT NULL DEFAULT 'MEDIUM';
ALTER TABLE todos DROP CONSTRAINT IF EXISTS todos_priority_check;
ALTER TABLE todos ADD CONSTRAINT todos_priority_check CHECK (priority IN ('LOW', 'MEDIUM', 'HIGH'));
