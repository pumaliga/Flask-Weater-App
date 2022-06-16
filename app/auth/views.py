import datetime
import os
import uuid
from functools import wraps

import jwt
from flask import abort, make_response
from flask import jsonify
from flask import request
from werkzeug.security import generate_password_hash, check_password_hash

from app import db
from app.auth import auth
from app.models import User


def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        if 'x-access-tokens' in request.headers:
            token = request.headers['x-access-tokens']
        if not token:
            return jsonify({'message': 'a valid token is missing'})
        try:
            data = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=['HS256'])
            current_user = User.query.filter_by(public_id=data['public_id']).first()
        except:
            return jsonify({'message': 'token is invalid'})

        return f(current_user, *args, **kwargs)

    return decorator


@auth.route('/register', methods=['POST'])
def create_user():
    data = request.get_json()
    if data.get('username') is None or data.get('password') is None:
        abort(400)

    if User.query.filter_by(username=data.get('username')).first():
        abort(400)

    hashed_password = generate_password_hash(data['password'], method='sha256')
    new_user = User(public_id=str(uuid.uuid4()), username=data['username'], password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'username': new_user.username}), 201


@auth.route('/login', methods=['POST'])
def login_user():
    data = request.get_json()
    if data.get('username') is None or data.get('password') is None:
        return jsonify({'message': 'required login or password'}), 400

    user = User.query.filter_by(username=data.get('username')).first()

    if check_password_hash(user.password, data.get('password')):
        token = jwt.encode(
            {'public_id': user.public_id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=30)},
            os.getenv('SECRET_KEY'), 'HS256')
        return jsonify({'token': token})

    return make_response('could not verify', 401, {'WWW.Authentication': 'Basic realm: "login required"'})
