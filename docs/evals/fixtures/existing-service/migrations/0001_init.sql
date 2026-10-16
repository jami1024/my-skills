CREATE TABLE IF NOT EXISTS orders (
    id     TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending'
);
