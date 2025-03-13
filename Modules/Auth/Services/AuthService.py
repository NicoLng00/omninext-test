from ..Contracts.AuthContract import AuthContract
from flask_jwt_extended import create_access_token
from Modules.Users.User import User
from Modules.Users.Services.UserService import UserService
from mongoengine.errors import NotUniqueError
import bcrypt

class AuthService(AuthContract):
    
    def __init__(self):
        self.user_service = UserService()
    
    def login(self, email, password):
        """
        Authenticate a user with email and password
        Returns access token if authentication is successful
        """
        try:
            if not email or not password:
                return {"error": "Email and password are required"}, 400
                
            user = User.objects.get(email=email)
            
            # Verify password with bcrypt
            if not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
                return {"error": "Invalid credentials"}, 401
            
            access_token = create_access_token(identity=str(user.id))
            
            return {
                "access_token": access_token,
                "user": {
                    "id": str(user.id),
                    "name": user.name,
                    "email": user.email
                }
            }, 200
            
        except User.DoesNotExist:
            return {"error": "Invalid credentials"}, 401
        except Exception as e:
            return {"error": str(e)}, 500
    
    def register(self, user_data):
        """
        Register a new user using UserService for user creation
        """
        try:
            # Validate all required fields
            if not user_data.get('name') or not user_data.get('email') or not user_data.get('password'):
                return {"error": "Name, email, and password are required"}, 400
            
            # Use UserService to create the user with password
            response, status_code = self.user_service.create(user_data)
            
            # If user creation failed, return the error
            if status_code != 201:
                return response, status_code
                
            # Generate token
            user_id = response['user']['_id']
            access_token = create_access_token(identity=user_id)
            
            # Add token to response
            response['access_token'] = access_token
            
            return response, 201
            
        except Exception as e:
            return {"error": str(e)}, 500