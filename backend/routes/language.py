from flask import Blueprint, request, jsonify
from services.language_detect import detect_language

language_bp = Blueprint('language', __name__)

@language_bp.route('/detect-language', methods=['POST'])
def detect():
    data = request.get_json()
    if not data:
        return jsonify({'error': '请求体不能为空'}), 400

    code = data.get('code', '')
    language, confidence = detect_language(code)
    return jsonify({'language': language, 'confidence': confidence})
