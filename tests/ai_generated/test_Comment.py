import pytest

```python
import unittest
from datetime import datetime
from your_application import db, Comment  # Adjust the import according to your project structure

class CommentModelTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app('testing')  # Assuming you have a function to create your app
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.comment = Comment(body='Test comment', author_id=1, post_id=1)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_comment_creation(self):
        db.session.add(self.comment)
        db.session.commit()
        self.assertEqual(self.comment.body, 'Test comment')
        self.assertIsNotNone(self.comment.timestamp)

    def test_on_changed_body(self):
        self.comment.body = 'New comment with <a href="#">link</a>'
        Comment.on_changed_body(self.comment, self.comment.body, '', None)
        self.assertIn('<a href=', self.comment.body_html)

    def test_to_json(self):
        db.session.add(self.comment)
        db.session.commit()
        json_comment = self.comment.to_json()
        self.assertEqual(json_comment['body'], 'Test comment')
        self.assertIn('url', json_comment)
        self.assertIn('post_url', json_comment)

    def test_from_json_valid(self):
        json_data = {'body': 'A valid comment'}
        comment = Comment.from_json(json_data)
        self.assertEqual(comment.body, 'A valid comment')

    def test_from_json_invalid(self):
        json_data = {'body': ''}
        with self.assertRaises(ValidationError):
            Comment.from_json(json_data)

if __name__ == '__main__':
    unittest.main()
```