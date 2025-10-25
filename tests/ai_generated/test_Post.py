import unittest
from app.models import Post  # Replace 'your_application' with the actual module name
from app.exceptions import ValidationError  # Adjust the import based on your project structure
from app import create_app, db

class PostModelTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app("testing")
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.post = Post(body='Test body', author_id=1)

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_post_creation(self):
        db.session.add(self.post)
        db.session.commit()
        self.assertEqual(self.post.body, 'Test body')
        self.assertIsNotNone(self.post.timestamp)

    def test_on_changed_body(self):
        self.post.body = 'Check <a href="#">link</a> and <script>alert("xss")</script>'
        Post.on_changed_body(self.post, self.post.body, None, None)
        self.assertIn('<a href="#">link</a>', self.post.body_html)
        self.assertNotIn('<script>', self.post.body_html)

    def test_to_json(self):
        db.session.add(self.post)
        db.session.commit()
        json_post = self.post.to_json()
        self.assertEqual(json_post['body'], 'Test body')
        self.assertTrue('url' in json_post)

    def test_from_json(self):
        json_data = {'body': 'New body'}
        new_post = Post.from_json(json_data)
        self.assertEqual(new_post.body, 'New body')

    def test_from_json_missing_body(self):
        json_data = {}
        with self.assertRaises(ValidationError):
            Post.from_json(json_data)

    def test_from_json_empty_body(self):
        json_data = {'body': ''}
        with self.assertRaises(ValidationError):
            Post.from_json(json_data)

if __name__ == '__main__':
    unittest.main()