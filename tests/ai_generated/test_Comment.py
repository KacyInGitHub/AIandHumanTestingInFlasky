import unittest
from datetime import datetime
from app.models import db, Comment  # Adjust the import based on your project structure
from app.exceptions import ValidationError  # Adjust the import based on your project structure
from app import create_app
from flask import url_for

class CommentModelTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app("testing")
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.comment = Comment(body='Test comment', author_id=1, post_id=1)
        db.session.add(self.comment)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_comment_creation(self):
        self.assertEqual(self.comment.body, 'Test comment')
        self.assertIsInstance(self.comment.timestamp, datetime)
        self.assertFalse(self.comment.disabled)

    def test_on_changed_body(self):
        self.comment.body = 'This is a <b>test</b> comment.'
        Comment.on_changed_body(self.comment, self.comment.body, '', None)
        self.assertIn('<b>', self.comment.body_html)
        self.assertIn('</b>', self.comment.body_html)

    def test_to_json(self):
        json_comment = self.comment.to_json()
        self.assertEqual(json_comment['body'], 'Test comment')
        self.assertEqual(json_comment['author_url'], url_for('api.get_user', id=self.comment.author_id))

    def test_from_json_valid(self):
        json_data = {'body': 'This is a valid comment'}
        comment = Comment.from_json(json_data)
        self.assertEqual(comment.body, 'This is a valid comment')

    def test_from_json_invalid(self):
        json_data = {'body': ''}
        with self.assertRaises(ValidationError):
            Comment.from_json(json_data)

if __name__ == '__main__':
    unittest.main()