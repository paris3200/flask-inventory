# tests/test_vendor.py


import unittest


from base import BaseTestCase
from project.models import Vendor
from project.vendor.forms import RegisterForm


class TestVendorBlueprint(BaseTestCase):

    def test_register_route(self):
        # Ensure register behaves correctly when logged in.
        with self.client:
            self.client.post(
                '/login',
                data=dict(email="ad@min.com", password="admin_user"),
                follow_redirects=True
            )
        # Ensure about route behaves correctly.
        response = self.client.get('/vendor/register', follow_redirects=True)
        self.assertIn(b'<h1>Register Vendor</h1>\n', response.data)

    def test_view_route(self):
        # Ensure view route behaves correctly when logged in.
        with self.client:
            self.client.post(
                '/login',
                data=dict(email="ad@min.com", password="admin_user"),
                follow_redirects=True
            )
        response = self.client.get('/vendor/view', follow_redirects=True)
        self.assertIn(b'<h1>Vendors</h1>\n', response.data)

    def test_register_route_requires_login(self):
        # Ensure member route requres logged in user.
        response = self.client.get('/vendor/register', follow_redirects=True)
        self.assertIn(b'Please log in to access this page', response.data)

    def test_view_route_requires_login(self):
        # Ensure member route requres logged in user.
        response = self.client.get('/vendor/view', follow_redirects=True)
        self.assertIn(b'Please log in to access this page', response.data)

    def test_vendor_registration(self):
        with self.client:
            self.client.post(
                '/login',
                data=dict(email="ad@min.com", password="admin_user"),
                follow_redirects=True)
            response = self.client.post(
                '/vendor/register',
                data=dict(company_name="Achme", state="NC"),
                follow_redirects=True)
        self.assertIn(b'<h1>Vendors</h1>\n', response.data)
        self.assertEqual(response.status_code, 200)

    def test_vendor_disallows_duplicate_registration(self):
        with self.client:
            self.client.post(
                '/login',
                data=dict(email="ad@min.com", password="admin_user"),
                follow_redirects=True)
            self.client.post(
                '/vendor/register',
                data=dict(company_name="Achme", state="NC"),
                follow_redirects=True)
            response = self.client.post(
                '/vendor/register',
                data=dict(company_name="Achme", state="NC"),
                follow_redirects=True)
        self.assertIn(b'Vendor already exist\n', response.data)
        self.assertEqual(response.status_code, 200)

    def test_validate_success_registration_form(self):
        # Ensure invalid email format throws error.
        form  = RegisterForm(company_name="Achme",
                        contact="", phone="",
                        website="www.achme.com",
                        line1="", line2="",
                        city="", state="NC",
                        zipcode="")
        self.assertTrue(form.validate())

if __name__ == '__main__':
    unittest.main()
