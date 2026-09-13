from flask import Flask
from flask_cors import CORS
from config import DB_PATH
from config import SECRET_KEY
from database.db import init_db
import os

def create_app():
    app = Flask(__name__)
    app.secret_key = SECRET_KEY
    CORS(app, resources={r"/api/*": {"origins": ["http://localhost:5175", "http://127.0.0.1:5175"]}}, supports_credentials=True)

    from routes.review import review_bp
    from routes.history import history_bp
    from routes.language import language_bp
    from routes.auth import auth_bp

    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(review_bp, url_prefix='/api')
    app.register_blueprint(history_bp, url_prefix='/api')
    app.register_blueprint(language_bp, url_prefix='/api')

    os.makedirs(DB_PATH.parent, exist_ok=True)
    init_db()

    @app.route('/api/health')
    def health():
        return {'status': 'ok'}

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5002)
