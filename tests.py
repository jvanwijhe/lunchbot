import os
from app import app
import unittest
import tempfile

class AppTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, app.config['DATABASE'] = tempfile.mkstemp()
        app.testing = True
        self.app = app.test_client()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(app.config['DATABASE'])

    def test_get_root(self):
        response = self.app.get('/')

        message = b"Welcome to lunchbot"
        self.assertEqual(message, response.data)

    def test_post_root(self):
        response = self.app.post('/', data=dict(
            channel_id='12',
            channel_name='test'
        ))

        message = b"Sorry, your team 'test' is not subscribed to TQ's lunch plan, but you should really consider joining!"
        self.assertEqual(message, response.data)

    def test_get_reports(self):
        response = self.app.get('/reports')
        self.assertEqual(404, response.status_code) # no directory listing

        response = self.app.get('/reports/.gitignore')
        self.assertEqual(200, response.status_code)

if __name__ == '__main__':
    unittest.main()
