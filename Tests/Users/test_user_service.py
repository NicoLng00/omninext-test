import unittest
from unittest.mock import patch, MagicMock
from bson import ObjectId
from bson.errors import InvalidId
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from Modules.Users.Services.UserService import UserService
from Modules.Users.User import User
from mongoengine.errors import DoesNotExist, ValidationError, NotUniqueError

class TestUserService(unittest.TestCase):
    """Test unitari per i metodi della classe UserService."""
    
    def setUp(self):
        self.user_service = UserService()
    
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
    def test_find_by_id_existing_user(self, mock_objects):
        """Test recupero di un utente esistente tramite ID."""

        mock_user = MagicMock()
        mock_user.to_mongo.return_value.to_dict.return_value = {
            '_id': ObjectId('507f1f77bcf86cd799439011'),
            'name': 'Test User',
            'email': 'test@example.com'
        }
        
        mock_objects.get.return_value = mock_user
        
        response, status_code = self.user_service.find_by_id('507f1f77bcf86cd799439011')
        
        self.assertEqual(status_code, 200)
        self.assertIn('user', response)
        self.assertEqual(response['user']['name'], 'Test User')
        self.assertEqual(response['user']['email'], 'test@example.com')
        self.assertEqual(response['user']['_id'], '507f1f77bcf86cd799439011')
        
        mock_objects.get.assert_called_once()
    
    @patch('Modules.Users.Services.UserService.User.objects')
    def test_find_by_id_nonexistent_user(self, mock_objects):
        """Test recupero di un utente inesistente."""
        mock_objects.get.side_effect = DoesNotExist()
        
        response, status_code = self.user_service.find_by_id('507f1f77bcf86cd799439011')
        
        self.assertEqual(status_code, 404)
        self.assertIn('error', response)
        self.assertEqual(response['error'], 'User not found')
    
    
    @patch('Modules.Users.Services.UserService.User')
    def test_create_valid_user(self, mock_user_class):
        """Test creazione di un utente con dati validi."""

        mock_user = MagicMock()
        mock_user.to_mongo.return_value.to_dict.return_value = {
            '_id': ObjectId('507f1f77bcf86cd799439011'),
            'name': 'Nuovo Utente',
            'email': 'nuovo@example.com'
        }
        
        mock_user_class.return_value = mock_user
        
        data = {
            'name': 'nuovo utente',
            'email': 'nuovo@example.com'
        }
        
       
        response, status_code = self.user_service.create(data)
        
        self.assertEqual(status_code, 201)
        self.assertIn('user', response)
        self.assertEqual(response['user']['name'], 'Nuovo Utente')
        self.assertEqual(response['user']['email'], 'nuovo@example.com')
        
        mock_user_class.assert_called_once_with(name='Nuovo Utente', email='nuovo@example.com')
        mock_user.save.assert_called_once()
    
    def test_create_user_missing_fields(self):
        """Test creazione utente con campi mancanti."""
        test_cases = [
            {'name': 'Solo Nome'},
            {'email': 'solo@email.com'},
            {}
        ]
        
        for data in test_cases:
            response, status_code = self.user_service.create(data)
            self.assertEqual(status_code, 400)
            self.assertIn('error', response)
            self.assertEqual(response['error'], 'Name and email are required')
    
    def test_create_user_invalid_email(self):
        """Test creazione utente con email non valida."""
        data = {
            'name': 'Utente Test',
            'email': 'non-valida'
        }
        
        response, status_code = self.user_service.create(data)
        self.assertEqual(status_code, 400)
        self.assertIn('error', response)
        self.assertEqual(response['error'], 'Invalid email format')
    
    @patch('Modules.Users.Services.UserService.User')
    def test_create_user_duplicate_email(self, mock_user_class):
        """Test creazione utente con email duplicata."""
        mock_user = MagicMock()
        mock_user.save.side_effect = NotUniqueError()
        mock_user_class.return_value = mock_user
        
        data = {
            'name': 'Altro Utente',
            'email': 'duplicate@example.com'
        }
        
        response, status_code = self.user_service.create(data)
        self.assertEqual(status_code, 400)
        self.assertIn('error', response)
        self.assertEqual(response['error'], 'A user with this email already exists')
    
    @patch('Modules.Users.Services.UserService.User')
    def test_create_user_unexpected_error(self, mock_user_class):
        """Test gestione di errori imprevisti durante la creazione."""
        mock_user = MagicMock()
        mock_user.save.side_effect = Exception('Unexpected error')
        mock_user_class.return_value = mock_user
        
        data = {
            'name': 'Utente Test',
            'email': 'test@example.com'
        }
        
        response, status_code = self.user_service.create(data)
        self.assertEqual(status_code, 500)
        self.assertIn('error', response)
        self.assertEqual(response['error'], 'Unexpected error')


if __name__ == '__main__':
    unittest.main() 