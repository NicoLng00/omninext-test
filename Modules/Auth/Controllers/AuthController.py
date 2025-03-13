from flask import request
from flask_restx import Namespace, Resource, fields
from ..Services.AuthService import AuthService

auth_ns = Namespace('auth', description='Authentication operations')

# Define models for Swagger
login_model = auth_ns.model('Login', {
    'email': fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description='User password')
})

register_model = auth_ns.model('Register', {
    'name': fields.String(required=True, description='User name'),
    'email': fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description='User password')
})

auth_response = auth_ns.model('AuthResponse', {
    'access_token': fields.String(description='JWT access token'),
    'user': fields.Nested(auth_ns.model('UserInfo', {
        'id': fields.String(description='User ID'),
        'name': fields.String(description='User name'),
        'email': fields.String(description='User email')
    }))
})

error_model = auth_ns.model('ErrorResponse', {
    'error': fields.String(description='Error message')
})

@auth_ns.route('/login')
class Login(Resource):
    @auth_ns.doc('user_login')
    @auth_ns.expect(login_model)
    @auth_ns.response(200, 'Login successful', auth_response)
    @auth_ns.response(401, 'Invalid credentials', error_model)
    def post(self):
        """Log in an existing user"""
        data = request.get_json()
        auth_service = AuthService()
        return auth_service.login(data.get('email'), data.get('password'))

@auth_ns.route('/register')
class Register(Resource):
    @auth_ns.doc('user_register')
    @auth_ns.expect(register_model)
    @auth_ns.response(201, 'User registered', auth_response)
    @auth_ns.response(400, 'Validation error', error_model)
    def post(self):
        """Register a new user"""
        data = request.get_json()
        auth_service = AuthService()
        return auth_service.register(data) 