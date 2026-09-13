import sqlite3
import uuid
from datetime import datetime
from config import DB_PATH

def get_conn():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id TEXT PRIMARY KEY,
            user_id TEXT,
            filename TEXT,
            language TEXT,
            code TEXT,
            total_lines INTEGER,
            issues_count INTEGER,
            result_json TEXT,
            created_at TEXT
        )
    ''')
    columns = {row['name'] for row in conn.execute('PRAGMA table_info(reviews)').fetchall()}
    if 'user_id' not in columns:
        conn.execute('ALTER TABLE reviews ADD COLUMN user_id TEXT')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_reviews_user_id ON reviews(user_id)')
    conn.commit()
    conn.close()

def create_user(username, password_hash):
    conn = get_conn()
    user_id = str(uuid.uuid4())
    created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    conn.execute(
        'INSERT INTO users (id, username, password_hash, created_at) VALUES (?, ?, ?, ?)',
        (user_id, username, password_hash, created_at)
    )
    conn.commit()
    conn.close()
    return user_id

def get_user_by_username(username):
    conn = get_conn()
    row = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    return dict(row) if row else None

def get_user(user_id):
    conn = get_conn()
    row = conn.execute('SELECT id, username, created_at FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def insert_review(user_id, filename, language, code, total_lines, issues_count, result_json):
    conn = get_conn()
    review_id = str(uuid.uuid4())
    created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    conn.execute(
        'INSERT INTO reviews (id, user_id, filename, language, code, total_lines, issues_count, result_json, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
        (review_id, user_id, filename, language, code, total_lines, issues_count, result_json, created_at)
    )
    conn.commit()
    conn.close()
    return review_id

def get_history(user_id):
    conn = get_conn()
    rows = conn.execute(
        'SELECT id, filename, language, issues_count, created_at FROM reviews WHERE user_id = ? ORDER BY created_at DESC',
        (user_id,)
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_review(review_id, user_id):
    conn = get_conn()
    row = conn.execute('SELECT * FROM reviews WHERE id = ? AND user_id = ?', (review_id, user_id)).fetchone()
    conn.close()
    return dict(row) if row else None

def delete_review(review_id, user_id):
    conn = get_conn()
    conn.execute('DELETE FROM reviews WHERE id = ? AND user_id = ?', (review_id, user_id))
    conn.commit()
    conn.close()
