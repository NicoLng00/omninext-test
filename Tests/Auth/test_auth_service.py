import unittest
from unittest.mock import patch, MagicMock
import bcrypt
import json
from bson import ObjectId
from mongoengine import connect, disconnect
from Modules.Auth.Services.AuthService import AuthService
from Modules.Users.User import User

class TestAuthService(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        disconnect()
        import mongomock
        connect('mongoenginetest', host='localhost', mongo_client_class=mongomock.MongoClient)
    
    @classmethod
    def tearDownClass(cls):
        disconnect()
    
    def setUp(self):
        self.auth_service = AuthService()
        
        self.test_password = "test_password"
        self.hashed_password = bcrypt.hashpw(self.test_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        self.user_id = str(ObjectId())
        self.test_user = {
            'id': self.user_id,
            'name': 'Test User',
            'email': 'test@example.com',
            'password': self.hashed_password
        }
        
        self.mock_user = MagicMock()
        self.mock_user.id = self.user_id
        self.mock_user.name = self.test_user['name']
        self.mock_user.email = self.test_user['email']
        self.mock_user.password = self.hashed_password

    @patch('Modules.Auth.Services.AuthService.User.objects.get')
    @patch('Modules.Auth.Services.AuthService.create_access_token')
    @patch('bcrypt.checkpw')
    def test_login_success(self, mock_checkpw, mock_create_token, mock_user_get):
        mock_user_get.return_value = self.mock_user
        mock_checkpw.return_value = True
        mock_create_token.return_value = "mocked_jwt_token"
        
        result, status_code = self.auth_service.login(self.test_user['email'], self.test_password)
        
        self.assertEqual(resul['access_token'], "mocked_jwt_token")
        self.assertEqual(result['user']['id'], self.user_id)
        self.assertEqual(result['user']['name'], self.test_user['name'])
        self.assertEqual(result['user']['email'], self.test_user['email'])
        
        mock_user_get.assert_called_once_with(email=self.test_user['email'])
        mock_checkpw.assert_called_once_with(self.test_password.encode('utf-8'), self.hashed_password.encode('utf-8'))
        mock_create_token.assert_called_once_with(identity=self.user_id)

    @patch('Modules.Auth.Services.AuthService.User.objects.get')
    @patch('bcrypt.checkpw')
    def test_login_invalid_password(self, mock_checkpw, mock_user_get):
        mock_user_get.return_value = self.mock_user
        mock_checkpw.return_value = False
        
        result, status_code = self.auth_service.login(self.test_user['email'], "wrong_password")
        
        self.assertEqual(status_code, 401)
        self.assertEqual(result['error'], "Invalid credentials")

    @patch('Modules.Auth.Services.AuthService.User.objects.get')
    def test_login_user_not_found(self, mock_user_get):
        mock_user_get.side_effect = User.DoesNotExist()
        
        result, status_code = self.auth_service.login("nonexistent@example.com", self.test_password)
        
        self.assertEqual(status_code, 401)
        self.assertEqual(result['error'], "Invalid credentials")

    def test_login_missing_credentials(self):
        result, status_code = self.auth_service.login("", self.test_password)
        self.assertEqual(status_code, 400)
        self.assertEqual(result['error'], "Email and password are required")
        
        result, status_code = self.auth_service.login(self.test_user['email'], "")
        self.assertEqual(status_code, 400)
        self.assertEqual(result['error'], "Email and password are required")

    @patch('Modules.Auth.Services.AuthService.UserService.create')
    @patch('Modules.Auth.Services.AuthService.create_access_token')
    def test_register_success(self, mock_create_token, mock_user_create):
        new_user_data = {
            'name': 'New User',
            'email': 'newuser@example.com',
            'password': 'newpassword123'
        }
        
        user_response = {
            'user': {
                '_id': self.user_id, 
                'name': new_user_data['name'],
                'email': new_user_data['email']
            }
        }
        mock_user_create.return_value = (user_response, 201)
        mock_create_token.return_value = "new_user_token"
        
        result, status_code = self.auth_service.register(new_user_data)
        
        self.assertEqual(status_code, 201)
        self.assertEqual(result['access_token'], "new_user_token")
        self.assertEqual(result['user']['_id'], self.user_id)
        
        mock_user_create.assert_called_once_with(new_user_data)
        mock_create_token.assert_called_once_with(identity=self.user_id)

    @patch('Modules.Auth.Services.AuthService.UserService.create')
    def test_register_user_creation_failed(self, mock_user_create):
        new_user_data = {
            'name': 'New User',
            'email': 'newuser@example.com',
            'password': 'newpassword123'
        }
        
        error_response = {'error': 'A user with this email already exists'}
        mock_user_create.return_value = (error_response, 400)
        
        result, status_code = self.auth_service.register(new_user_data)
        
        self.assertEqual(status_code, 400)
        self.assertEqual(result['error'], 'A user with this email already exists')

    def test_register_missing_fields(self):
        result, status_code = self.auth_service.register({
            'email': 'test@example.com', 
            'password': 'password'
        })
        self.assertEqual(status_code, 400)
        self.assertEqual(result['error'], "Name, email, and password are required")
        
        result, status_code = self.auth_service.register({
            'name': 'Test User',
            'password': 'password'
        })
        self.assertEqual(status_code, 400)
        self.assertEqual(result['error'], "Name, email, and password are required")
        
        result, status_code = self.auth_service.register({
            'name': 'Test User',
            'email': 'test@example.com'
        })
        self.assertEqual(status_code, 400)
        self.assertEqual(result['error'], "Name, email, and password are required")

if __name__ == '__main__':
    unittest.main()
