import re

from flask import Blueprint, jsonify, request, session
from werkzeug.security import check_password_hash, generate_password_hash

from database.db import create_user, get_user, get_user_by_username
from middleware.auth import get_current_user_id

auth_bp = Blueprint('auth', __name__)
USERNAME_PATTERN = re.compile(r'^[A-Za-z0-9_\u4e00-\u9fff]{3,20}$')


@auth_bp.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    username = str(data.get('username', '')).strip()
    password = str(data.get('password', ''))

    if not USERNAME_PATTERN.fullmatch(username):
        return jsonify({'error': '用户名需为 3-20 位中文、字母、数字或下划线'}), 400
    if len(password) < 6 or len(password) > 128:
        return jsonify({'error': '密码长度需为 6-128 位'}), 400
    if get_user_by_username(username):
        return jsonify({'error': '用户名已存在'}), 409

    user_id = create_user(username, generate_password_hash(password))
    session['user_id'] = user_id
    return jsonify({'user': get_user(user_id)}), 201


@auth_bp.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username = str(data.get('username', '')).strip()
    password = str(data.get('password', ''))
    user = get_user_by_username(username)

    if not user or not check_password_hash(user['password_hash'], password):
        return jsonify({'error': '用户名或密码错误'}), 401

    session.clear()
    session['user_id'] = user['id']
    return jsonify({'user': get_user(user['id'])})


@auth_bp.route('/auth/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True})


@auth_bp.route('/auth/me', methods=['GET'])
def me():
    user_id = get_current_user_id()
    user = get_user(user_id) if user_id else None
    if not user:
        session.clear()
        return jsonify({'user': None})
    return jsonify({'user': user})
