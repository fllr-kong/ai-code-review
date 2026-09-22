import secrets
import sqlite3
import string
import uuid
from datetime import datetime
from config import DB_PATH

SHARE_CODE_ALPHABET = string.ascii_letters + string.digits
SHARE_CODE_LENGTH = 8

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
    conn.execute('''
        CREATE TABLE IF NOT EXISTS shares (
            code TEXT PRIMARY KEY,
            review_id TEXT NOT NULL,
            owner_id TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_shares_review_id ON shares(review_id)')
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
    conn.execute('DELETE FROM shares WHERE review_id = ?', (review_id,))
    conn.commit()
    conn.close()

def _generate_share_code(conn):
    for _ in range(10):
        code = ''.join(secrets.choice(SHARE_CODE_ALPHABET) for _ in range(SHARE_CODE_LENGTH))
        exists = conn.execute('SELECT 1 FROM shares WHERE code = ?', (code,)).fetchone()
        if not exists:
            return code
    raise RuntimeError('生成分享码失败，请重试')

def get_share_by_review(review_id, owner_id):
    conn = get_conn()
    row = conn.execute(
        'SELECT * FROM shares WHERE review_id = ? AND owner_id = ?',
        (review_id, owner_id)
    ).fetchone()
    conn.close()
    return dict(row) if row else None

def create_share(review_id, owner_id):
    """为指定审查记录创建分享码，已存在则直接返回原分享码（幂等）"""
    existing = get_share_by_review(review_id, owner_id)
    if existing:
        return existing

    conn = get_conn()
    code = _generate_share_code(conn)
    created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    conn.execute(
        'INSERT INTO shares (code, review_id, owner_id, created_at) VALUES (?, ?, ?, ?)',
        (code, review_id, owner_id, created_at)
    )
    conn.commit()
    conn.close()
    return {'code': code, 'review_id': review_id, 'owner_id': owner_id, 'created_at': created_at}

def delete_share(review_id, owner_id):
    conn = get_conn()
    conn.execute(
        'DELETE FROM shares WHERE review_id = ? AND owner_id = ?',
        (review_id, owner_id)
    )
    conn.commit()
    conn.close()

def get_shared_review(code):
    """凭分享码获取审查记录及分享者信息，记录被删除或码无效时返回 None"""
    conn = get_conn()
    row = conn.execute('''
        SELECT r.id, r.filename, r.language, r.code, r.total_lines,
               r.issues_count, r.result_json, r.created_at,
               s.created_at AS shared_at,
               u.username AS owner_name
        FROM shares s
        JOIN reviews r ON s.review_id = r.id
        LEFT JOIN users u ON r.user_id = u.id
        WHERE s.code = ?
    ''', (code,)).fetchone()
    conn.close()
    return dict(row) if row else None
