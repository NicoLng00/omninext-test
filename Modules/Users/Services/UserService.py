from flask import jsonify
from bson import ObjectId
from ..Contracts.UserContract import UserContract
from ..User import User
from mongoengine.errors import DoesNotExist, ValidationError

class UserService(UserContract):
    
    
    def find_by_id(self, user_id):
        try:
            user = User.objects.get(id=ObjectId(user_id))
            user_dict = user.to_mongo().to_dict()
            user_dict['_id'] = str(user_dict['_id'])  # Convert ObjectId to string
            return {"user": user_dict}, 200
        except (DoesNotExist, ValidationError):
            return {"error": "User not found"}, 404
