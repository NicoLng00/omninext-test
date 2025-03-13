from flask import jsonify
from bson import ObjectId
from ..Contracts.UserContract import UserContract
from ..User import User
from mongoengine.errors import DoesNotExist, ValidationError, NotUniqueError
import re

class UserService(UserContract):
    
    def find_by_id(self, user_id):
        try:
            user = User.objects.get(id=ObjectId(user_id))
            user_dict = user.to_mongo().to_dict()
            user_dict['_id'] = str(user_dict['_id'])
            return {"user": user_dict}, 200
        except (DoesNotExist, ValidationError):
            return {"error": "User not found"}, 404

    def validate_email(self, email):
        pattern = r"^(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|\"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*\")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])$"
        return re.match(pattern, email, re.IGNORECASE) is not None


    def create(self, data):
        try:
            name = data.get('name')
            email = data.get('email')
            
            if not name or not email:
                return {"error": "Name and email are required"}, 400
                
            if not self.validate_email(email):
                return {"error": "Invalid email format"}, 400
                                
            name = name.strip().title()
            
            new_user = User(name=name, email=email)
            new_user.save()
            
            user_dict = new_user.to_mongo().to_dict()
            user_dict['_id'] = str(user_dict['_id'])
            
            return {"user": user_dict}, 201
        except NotUniqueError:
            return {"error": "A user with this email already exists"}, 400
        except Exception as e:
            return {"error": str(e)}, 500
