CREATE TABLE IF NOT EXISTS topics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_id INTEGER NOT NULL,
    next_review_date DATE NOT NULL,
    interval INTEGER DEFAULT 1,
    ease_factor REAL DEFAULT 2.5,
    FOREIGN KEY(topic_id) REFERENCES topics(id)
);

CREATE TABLE IF NOT EXISTS journal (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    keywords TEXT
);

CREATE TABLE IF NOT EXISTS study_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,
    reviews_completed INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS pomodoro_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,
    duration_minutes INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS formulas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    latex_code TEXT NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS citations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date_added DATE NOT NULL,
    url TEXT NOT NULL,
    title TEXT,
    authors TEXT,
    pub_date TEXT,
    notes TEXT
);
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT
);

CREATE TABLE IF NOT EXISTS homework (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject TEXT NOT NULL,
    title TEXT NOT NULL,
    deadline DATE NOT NULL,
    priority INTEGER DEFAULT 3,
    status TEXT DEFAULT 'A faire'
);

CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'En cours',
    start_date DATE NOT NULL
);

CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT NOT NULL,
    status TEXT DEFAULT 'A faire',
    priority INTEGER DEFAULT 3,
    deadline DATE,
    project_id INTEGER,
    parent_id INTEGER,
    completed_at DATE,
    FOREIGN KEY(project_id) REFERENCES projects(id),
    FOREIGN KEY(parent_id) REFERENCES tasks(id)
);
