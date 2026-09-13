import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def load_env():
    env_path = BASE_DIR / '.env'
    if env_path.exists():
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ.setdefault(key.strip(), value.strip())

load_env()

LLM_API_KEY = os.environ.get('LLM_API_KEY', '')
LLM_API_BASE = os.environ.get('LLM_API_BASE', 'https://api.deepseek.com/v1')
LLM_CHAT_MODEL = os.environ.get('LLM_CHAT_MODEL', 'deepseek-chat')
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-only-change-this-secret-key')

DB_PATH = BASE_DIR / 'reviews.db'
