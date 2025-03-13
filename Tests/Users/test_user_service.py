import unittest
from unittest.mock import patch, MagicMock
from bson import ObjectId
from bson.errors import InvalidId
import sys
import os
import bcrypt
from flask import Flask
from flask_jwt_extended import JWTManager

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from Modules.Users.Services.UserService import UserService
from Modules.Users.User import User
from mongoengine.errors import DoesNotExist, ValidationError, NotUniqueError

class TestUserService(unittest.TestCase):
    
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['JWT_SECRET_KEY'] = 'test-secret-key'
        self.jwt = JWTManager(self.app)
        
        self.user_service = UserService()
        
        self.example_jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        
        self.auth_headers = {'Authorization': f'Bearer {self.example_jwt}'}
        
        self.test_password = "password123"
        self.hashed_password = bcrypt.hashpw(self.test_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def test_validate_email_valid(self):
        valid_emails = [
            "user@example.com",
            "user.name@example.co.uk",
            "user+tag@example.org",
            "user_name@example.it"
        ]
        
        for email in valid_emails:
            self.assertTrue(self.user_service.validate_email(email))
    
    def test_validate_email_invalid(self):
        invalid_emails = [
            "user@example",  # dominio incompleto
            "user.example.com",  # manca la @
            "@example.com",  # manca il local part
            "user@.com",  # manca il domain name
            "user space@example.com"  # contiene spazi
        ]
        
        for email in invalid_emails:
            self.assertFalse(self.user_service.validate_email(email))
    
    @patch('Modules.Users.Services.UserService.User.objects')
    @patch('flask_jwt_extended.verify_jwt_in_request')
    def test_find_by_id_existing_user(self, mock_verify_jwt, mock_objects):
        mock_verify_jwt.return_value = True
        
        mock_user = MagicMock()
        mock_user.to_mongo.return_value.to_dict.return_value = {
            '_id': ObjectId('507f1f77bcf86cd799439011'),
            'name': 'Test User',
            'email': 'test@example.com'
        }
        
        mock_objects.get.return_value = mock_user
        
        with self.app.test_request_context(headers=self.auth_headers):
            response, status_code = self.user_service.find_by_id('507f1f77bcf86cd799439011')
        
        self.assertEqual(status_code, 200)
        self.assertIn('user', response)
        self.assertEqual(response['user']['name'], 'Test User')
        self.assertEqual(response['user']['email'], 'test@example.com')
        self.assertEqual(response['user']['_id'], '507f1f77bcf86cd799439011')
        
        mock_objects.get.assert_called_once()
    
    @patch('Modules.Users.Services.UserService.User.objects')
    @patch('flask_jwt_extended.verify_jwt_in_request')
    def test_find_by_id_nonexistent_user(self, mock_verify_jwt, mock_objects):
        mock_verify_jwt.return_value = True
        
        mock_objects.get.side_effect = DoesNotExist()
        
        with self.app.test_request_context(headers=self.auth_headers):
            response, status_code = self.user_service.find_by_id('507f1f77bcf86cd799439011')
        
        self.assertEqual(status_code, 404)
        self.assertIn('error', response)
        self.assertEqual(response['error'], 'User not found')
    
    @patch('Modules.Users.Services.UserService.User')
    @patch('bcrypt.hashpw')
    def test_create_valid_user(self, mock_hashpw, mock_user_class):
        mock_hashpw.return_value = self.hashed_password.encode('utf-8')
        
        mock_user = MagicMock()
        mock_user.to_mongo.return_value.to_dict.return_value = {
            '_id': ObjectId('507f1f77bcf86cd799439011'),
            'name': 'Nuovo Utente',
            'email': 'nuovo@example.com'
        }
        
        mock_user_class.return_value = mock_user
        
        data = {
            'name': 'nuovo utente',
            'email': 'nuovo@example.com',
            'password': self.test_password
        }
        
        response, status_code = self.user_service.create(data)
        
        self.assertEqual(status_code, 201)
        self.assertIn('user', response)
        self.assertEqual(response['user']['name'], 'Nuovo Utente')
        self.assertEqual(response['user']['email'], 'nuovo@example.com')
        
        mock_user_class.assert_called_once()
        self.assertEqual(mock_user_class.call_args[1]['name'], 'Nuovo Utente')
        self.assertEqual(mock_user_class.call_args[1]['email'], 'nuovo@example.com')
        mock_user.save.assert_called_once()
    
    def test_create_user_missing_fields(self):
        test_cases = [
            {'name': 'Solo Nome'},
            {'email': 'solo@email.com'},
            {'password': 'solopassword'},
            {}
        ]
        
        for data in test_cases:
            response, status_code = self.user_service.create(data)
            self.assertEqual(status_code, 400)
            self.assertIn('error', response)
            self.assertTrue(
                'required' in response['error'].lower() or 
                'name' in response['error'].lower() or 
                'email' in response['error'].lower() or 
                'password' in response['error'].lower(),
                f"Expected error about missing field, got: {response['error']}"
            )
    
    def test_create_user_invalid_email(self):
        data = {
            'name': 'Utente Test',
            'email': 'non-valida',
            'password': self.test_password
        }
        
        response, status_code = self.user_service.create(data)
        self.assertEqual(status_code, 400)
        self.assertIn('error', response)
        self.assertEqual(response['error'], 'Invalid email format')
    
    @patch('Modules.Users.Services.UserService.User')
    @patch('bcrypt.hashpw')
    def test_create_user_duplicate_email(self, mock_hashpw, mock_user_class):
        mock_hashpw.return_value = self.hashed_password.encode('utf-8')
        
        mock_user = MagicMock()
        mock_user.save.side_effect = NotUniqueError()
        mock_user_class.return_value = mock_user
        
        data = {
            'name': 'Altro Utente',
            'email': 'duplicate@example.com',
            'password': self.test_password
        }
        
        response, status_code = self.user_service.create(data)
        self.assertEqual(status_code, 400)
        self.assertIn('error', response)
        self.assertEqual(response['error'], 'A user with this email already exists')
    
    @patch('Modules.Users.Services.UserService.User')
    @patch('bcrypt.hashpw')
    def test_create_user_unexpected_error(self, mock_hashpw, mock_user_class):
        mock_hashpw.return_value = self.hashed_password.encode('utf-8')
        
        mock_user = MagicMock()
        mock_user.save.side_effect = Exception('Unexpected error')
        mock_user_class.return_value = mock_user
        
        data = {
            'name': 'Utente Test',
            'email': 'test@example.com',
            'password': self.test_password
        }
        
        response, status_code = self.user_service.create(data)
        self.assertEqual(status_code, 500)
        self.assertIn('error', response)
        self.assertEqual(response['error'], 'Unexpected error')


if __name__ == '__main__':
    unittest.main() 