from flask import Blueprint, jsonify
from database.db import get_history, get_review, delete_review
from middleware.auth import login_required, get_current_user_id

history_bp = Blueprint('history', __name__)

@history_bp.route('/history', methods=['GET'])
@login_required
def list_history():
    records = get_history(get_current_user_id())
    return jsonify({'history': records})

@history_bp.route('/history/<review_id>', methods=['GET'])
@login_required
def get_history_detail(review_id):
    record = get_review(review_id, get_current_user_id())
    if not record:
        return jsonify({'error': '记录不存在'}), 404

    import json
    result = json.loads(record['result_json'])
    return jsonify({
        'id': record['id'],
        'filename': record['filename'],
        'language': record['language'],
        'code': record['code'],
        'total_lines': record['total_lines'],
        'issues_count': record['issues_count'],
        'created_at': record['created_at'],
        'result': result
    })

@history_bp.route('/history/<review_id>', methods=['DELETE'])
@login_required
def delete_history(review_id):
    record = get_review(review_id, get_current_user_id())
    if not record:
        return jsonify({'error': '记录不存在'}), 404

    delete_review(review_id, get_current_user_id())
    return jsonify({'success': True})
