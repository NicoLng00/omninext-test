from flask import Blueprint, jsonify, request
from flask_restx import Namespace, Resource, fields
from ..Services.UserService import UserService

user_blueprint = Blueprint('user', __name__)
user_ns = Namespace('users', description='User operations')

#  models for swagger documentation
user_model = user_ns.model('User', {
    '_id': fields.String(description='User unique identifier'),
    'name': fields.String(required=True, description='User name'),
    'email': fields.String(required=True, description='User email address')
})

user_input_model = user_ns.model('UserInput', {
    'name': fields.String(required=True, description='User name'),
    'email': fields.String(required=True, description='User email address')
})

user_response_model = user_ns.model('UserResponse', {
    'user': fields.Nested(user_model)
})

error_model = user_ns.model('Error', {
    'error': fields.String(description='Error message')
})


@user_ns.route('/<string:user_id>')
class UserResource(Resource):
    @user_ns.doc('get_user')
    @user_ns.response(200, 'Success', user_response_model)
    @user_ns.response(404, 'User not found', error_model)
    def get(self, user_id):
        user_service = UserService()
        response, status_code = user_service.find_by_id(user_id)
        return response, status_code

@user_ns.route('/create')
class UserListResource(Resource):
    @user_ns.doc('create_user')
    @user_ns.expect(user_input_model)
    @user_ns.response(201, 'User created', user_response_model)
    @user_ns.response(400, 'Validation error', error_model)
    @user_ns.response(500, 'Internal server error', error_model)
    def post(self):
        data = request.get_json()
        user_service = UserService()
        response, status_code = user_service.create(data)
        return response, status_code


    