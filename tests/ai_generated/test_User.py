import unittest
from app import create_app, db
from app.models import User, Role
from flask import url_for

class UserModelTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app("testing")
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.role = Role(name='User', default=True)
        db.session.add(self.role)
        db.session.commit()
        self.user = User(email='test@example.com', username='testuser', password='password')
        db.session.add(self.user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_setter(self):
        user = User(password='password')
        self.assertTrue(user.password_hash is not None)

    def test_no_password_getter(self):
        user = User(password='password')
        with self.assertRaises(AttributeError):
            user.password

    def test_password_verification(self):
        user = User(password='password')
        self.assertTrue(user.verify_password('password'))
        self.assertFalse(user.verify_password('wrongpassword'))

    def test_avatar_hash(self):
        user = User(email='test@example.com')
        self.assertEqual(user.avatar_hash, user.gravatar_hash())

    def test_follow(self):
        user2 = User(email='test2@example.com', username='testuser2', password='password')
        db.session.add(user2)
        db.session.commit()
        self.user.follow(user2)
        self.assertTrue(self.user.is_following(user2))
        self.assertTrue(user2.is_followed_by(self.user))

    def test_unfollow(self):
        user2 = User(email='test2@example.com', username='testuser2', password='password')
        db.session.add(user2)
        db.session.commit()
        self.user.follow(user2)
        self.user.unfollow(user2)
        self.assertFalse(self.user.is_following(user2))
        self.assertFalse(user2.is_followed_by(self.user))

    def test_generate_confirmation_token(self):
        token = self.user.generate_confirmation_token()
        self.assertIsInstance(token, str)

    def test_confirm_token(self):
        token = self.user.generate_confirmation_token()
        self.assertTrue(self.user.confirm(token))
        self.assertTrue(self.user.confirmed)

    def test_change_email(self):
        new_email = 'new@example.com'
        token = self.user.generate_email_change_token(new_email)
        self.assertTrue(self.user.change_email(token))
        self.assertEqual(self.user.email, new_email)

    def test_generate_auth_token(self):
        token = self.user.generate_auth_token(3600)
        self.assertIsInstance(token, str)

    def test_verify_auth_token(self):
        token = self.user.generate_auth_token(3600)
        verified_user = User.verify_auth_token(token)
        self.assertEqual(verified_user.id, self.user.id)

    def test_to_json(self): # failed
        json_user = self.user.to_json()
        self.assertEqual(json_user['username'], self.user.username)
        self.assertEqual(json_user['url'], url_for('api.get_user', id=self.user.id))

if __name__ == '__main__':
    unittest.main()