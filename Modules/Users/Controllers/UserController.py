from flask import Blueprint, jsonify
from ..Services.UserService import UserService

user_blueprint = Blueprint('user', __name__)

@user_blueprint.route('/<string:user_id>', methods=['GET'])
def get_user(user_id):
    user_service = UserService()
    response, status_code = user_service.find_by_id(user_id)
    return jsonify(response), status_code