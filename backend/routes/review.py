from flask import Blueprint, request, jsonify
from services.review_service import review_code
from database.db import insert_review
from middleware.auth import login_required, get_current_user_id

review_bp = Blueprint('review', __name__)

@review_bp.route('/review', methods=['POST'])
@login_required
def review():
    data = request.get_json()
    if not data:
        return jsonify({'error': '请求体不能为空'}), 400

    code = data.get('code', '')
    language = data.get('language', 'python')
    filename = data.get('filename', 'untitled')

    if not code.strip():
        return jsonify({'error': '代码不能为空'}), 400

    result = review_code(code, language)

    total_lines = result.get('summary', {}).get('total_lines', len(code.splitlines()))
    issues_count = result.get('summary', {}).get('issues_count', len(result.get('issues', [])))

    review_id = insert_review(
        user_id=get_current_user_id(),
        filename=filename,
        language=language,
        code=code,
        total_lines=total_lines,
        issues_count=issues_count,
        result_json=__import__('json').dumps(result, ensure_ascii=False)
    )

    result['review_id'] = review_id
    return jsonify(result)

@review_bp.route('/review/batch', methods=['POST'])
@login_required
def review_batch():
    files = request.files.getlist('files')
    if not files:
        return jsonify({'error': '请上传文件'}), 400

    results = []
    for file in files:
        content = file.read().decode('utf-8', errors='replace')
        lang = request.form.get('language', 'python')
        result = review_code(content, lang)

        total_lines = result.get('summary', {}).get('total_lines', len(content.splitlines()))
        issues_count = result.get('summary', {}).get('issues_count', len(result.get('issues', [])))

        review_id = insert_review(
            user_id=get_current_user_id(),
            filename=file.filename,
            language=lang,
            code=content,
            total_lines=total_lines,
            issues_count=issues_count,
            result_json=__import__('json').dumps(result, ensure_ascii=False)
        )

        result['review_id'] = review_id
        result['filename'] = file.filename
        results.append(result)

    return jsonify({'results': results})
