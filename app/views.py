from flask import Blueprint, jsonify
from app.auth.views import token_required

views = Blueprint('views', __name__)


@views.route('/')
@token_required
def unprotected(current_user):
    return jsonify({'message':'Index page.'})




