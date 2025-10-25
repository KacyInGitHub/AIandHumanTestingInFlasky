import unittest
from unittest.mock import patch, MagicMock
from flask import g
from app import create_app,db  # Replace with your actual application import
from app.models import Role  # Adjust the import according to your structure

class TokenResourceTestCase(unittest.TestCase):

    def setUp(self):
        # self.app = app.test_client()
        # self.app.testing = True
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        self.client = self.app.test_client()

    @patch('app.models.User')  # Adjust the path as necessary
    def test_get_token_anonymous_user(self, mock_user):
        mock_user.is_anonymous = True
        with patch('flask.g', g):
            response = self.client.post('/api/v1/tokens/')
            self.assertEqual(response.status_code, 401)
            self.assertIn('Invalid credentials', response.get_data(as_text=True))

    @patch('app.models.User')  # Adjust the path as necessary
    def test_get_token_with_used_token(self, mock_user):
        mock_user.is_anonymous = False
        g.current_user = mock_user
        g.token_used = True
        with patch('flask.g', g):
            response = self.client.post('/api/v1/tokens/')
            self.assertEqual(response.status_code, 401)
            self.assertIn('Invalid credentials', response.get_data(as_text=True))

    @patch('app.models.User')  # Adjust the path as necessary
    def test_get_token_success(self, mock_user):
        mock_user.is_anonymous = False
        g.current_user = mock_user
        g.token_used = False
        mock_user.generate_auth_token.return_value = 'test_token'
        
        with patch('flask.g', g):
            response = self.client.post('/api/v1/tokens/')
            self.assertEqual(response.status_code, 200)
            self.assertIn('token', response.get_json())
            self.assertEqual(response.get_json()['token'], 'test_token')
            self.assertIn('expiration', response.get_json())
            self.assertEqual(response.get_json()['expiration'], 3600)

if __name__ == '__main__':
    unittest.main()