import json

from flask import Blueprint, jsonify

from database.db import (
    create_share,
    delete_share,
    get_review,
    get_share_by_review,
    get_shared_review,
)
from middleware.auth import get_current_user_id, login_required

share_bp = Blueprint('share', __name__)


def _serialize(record):
    result = json.loads(record['result_json'])
    return {
        'id': record['id'],
        'filename': record['filename'],
        'language': record['language'],
        'code': record['code'],
        'total_lines': record['total_lines'],
        'issues_count': record['issues_count'],
        'created_at': record['created_at'],
        'shared_at': record.get('shared_at'),
        'owner_name': record.get('owner_name'),
        'result': result,
    }


@share_bp.route('/history/<review_id>/share', methods=['POST'])
@login_required
def create_review_share(review_id):
    user_id = get_current_user_id()
    if not get_review(review_id, user_id):
        return jsonify({'error': '记录不存在'}), 404

    share = create_share(review_id, user_id)
    return jsonify({'code': share['code'], 'created_at': share['created_at']})


@share_bp.route('/history/<review_id>/share', methods=['GET'])
@login_required
def get_review_share(review_id):
    user_id = get_current_user_id()
    if not get_review(review_id, user_id):
        return jsonify({'error': '记录不存在'}), 404

    share = get_share_by_review(review_id, user_id)
    if not share:
        return jsonify({'shared': False})
    return jsonify({'shared': True, 'code': share['code'], 'created_at': share['created_at']})


@share_bp.route('/history/<review_id>/share', methods=['DELETE'])
@login_required
def revoke_review_share(review_id):
    user_id = get_current_user_id()
    if not get_review(review_id, user_id):
        return jsonify({'error': '记录不存在'}), 404

    delete_share(review_id, user_id)
    return jsonify({'success': True})


@share_bp.route('/share/<code>', methods=['GET'])
def view_shared_review(code):
    """公开接口：凭分享码只读查看审查结果，无需登录"""
    record = get_shared_review(code)
    if not record:
        return jsonify({'error': '分享不存在或已被取消'}), 404
    return jsonify(_serialize(record))
