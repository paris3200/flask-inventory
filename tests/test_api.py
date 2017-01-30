# tests/test_api.py


import unittest

from tests.base import BaseTestCase


class TestApi(BaseTestCase):

    def test_get_resources(self):
        # Components
        response = self.client.post(
                '/login',
                data=dict(email="ad@min.com", password="admin_user"),
                follow_redirects=True
            )
        response = self.client.get('/api/components', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'[]', response.data)
        # Single Tags
        response = self.client.get('/api/single-tags', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'[]', response.data)
        # Categories
        response = self.client.get('/api/single-tags', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'[]', response.data)


    def test_about(self):
        # Ensure about route behaves correctly.
        response = self.client.get('/about', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'About', response.data)

    def test_404(self):
        # Ensure 404 error is handled.
        response = self.client.get('/404')
        self.assert404(response)
        self.assertTemplateUsed('errors/404.html')


if __name__ == '__main__':
    unittest.main()
