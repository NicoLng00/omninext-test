from flask import jsonify
from bson import ObjectId
from ..Contracts.UserContract import UserContract
from ..User import User
from mongoengine.errors import DoesNotExist, ValidationError, NotUniqueError
import re
import bcrypt

class UserService(UserContract):
    
    def find_by_id(self, user_id):
        try:
            user = User.objects.get(id=ObjectId(user_id))
            user_dict = user.to_mongo().to_dict()
            user_dict['_id'] = str(user_dict['_id'])
            # Rimuovi la password dalla risposta
            if 'password' in user_dict:
                del user_dict['password']
            return {"user": user_dict}, 200
        except (DoesNotExist, ValidationError):
            return {"error": "User not found"}, 404

    def validate_email(self, email):
        pattern = r"^(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|\"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*\")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])$"
        return re.match(pattern, email, re.IGNORECASE) is not None

    def create(self, data):
        try:
            # Extract data from request
            name = data.get('name')
            email = data.get('email')
            password = data.get('password')
            
            # Validate required fields
            if not name or not email:
                return {"error": "Name and email are required"}, 400
            
            # Validate email format
            if not self.validate_email(email):
                return {"error": "Invalid email format"}, 400
            
            # Controlla se è presente la password
            if not password:
                return {"error": "Password is required"}, 400
                
            # Hash the password with bcrypt
            hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            password_hash = hashed_pw.decode('utf-8')
            
            # Format name properly
            name = name.strip().title()
            
            # Create new user with hashed password
            new_user = User(
                name=name,
                email=email,
                password=password_hash
            )
            new_user.save()
            
            # Convert to dict, remove password and format _id to string
            user_dict = new_user.to_mongo().to_dict()
            user_dict['_id'] = str(user_dict['_id'])
            del user_dict['password']  # Non inviare mai la password nelle risposte
            
            return {"user": user_dict}, 201
        except NotUniqueError:
            return {"error": "A user with this email already exists"}, 400
        except Exception as e:
            return {"error": str(e)}, 500
