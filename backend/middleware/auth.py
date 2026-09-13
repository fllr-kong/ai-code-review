from functools import wraps

from flask import jsonify, session


def get_current_user_id():
    return session.get('user_id')


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not get_current_user_id():
            return jsonify({'error': '请先登录'}), 401
        return view(*args, **kwargs)

    return wrapped
