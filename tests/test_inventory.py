# tests/test_vendor.py


import unittest


from base import BaseTestCase
from project.models import Vendor
from project.inventory.forms import RegisterForm, PurchaseOrderForm


class TestInventoryBlueprint(BaseTestCase):

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

    def test_edit_route_with_valid_vendor(self):
        # Ensure edit route behaves correctly when logged in.
        with self.client:
            self.client.post(
                '/login',
                data=dict(email="ad@min.com", password="admin_user"),
                follow_redirects=True)
            self.client.post(
                '/vendor/register',
                data=dict(name="Achme", state="NC"),
                follow_redirects=True)
            response = self.client.get('/vendor/edit/1',
                                    follow_redirects=True)
        self.assertIn(b'<h1>Edit Vendor</h1>\n', response.data)
        self.assertIn(b'value="Achme"', response.data)


    def test_edit_route_fails_with_invalid_vendor(self):
        with self.client:
            self.client.post(
                '/login',
                data=dict(email="ad@min.com", password="admin_user"),
                follow_redirects=True)
            response = self.client.get('/vendor/edit/1000',
                                    follow_redirects=True)
        self.assertEqual(response.status_code, 404)

    def test_edit_updates_to_database(self):
        with self.client:
            self.client.post(
                '/login',
                data=dict(email="ad@min.com", password="admin_user"),
                follow_redirects=True)
            self.client.post(
                '/vendor/register',
                data=dict(name="Achme", state="NC"),
                follow_redirects=True)
            response = self.client.post('/vendor/edit/1',
                                    data=dict(name="Achme LLC", state="NC"),
                                    follow_redirects=True)
        self.assertIn(b'<h1>Vendors</h1>\n', response.data)
        self.assertIn(b'Achme LLC', response.data)


    def test_register_route_requires_login(self):
        # Ensure member route requres logged in user.
        response = self.client.get('/vendor/register', follow_redirects=True)
        self.assertIn(b'Please log in to access this page', response.data)

    def test_view_route_requires_login(self):
        # Ensure member route requres logged in user.
        response = self.client.get('/vendor/view', follow_redirects=True)
        self.assertIn(b'Please log in to access this page', response.data)

    def test_edit_route_requires_login(self):
        # Ensure member route requres logged in user.
        response = self.client.get('/vendor/edit/1', follow_redirects=True)
        self.assertIn(b'Please log in to access this page', response.data)

    def test_vendor_registration(self):
        with self.client:
            self.client.post(
                '/login',
                data=dict(email="ad@min.com", password="admin_user"),
                follow_redirects=True)
            response = self.client.post(
                '/vendor/register',
                data=dict(name="Achme", state="NC"),
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
                data=dict(name="Achme", state="NC"),
                follow_redirects=True)
            response = self.client.post(
                '/vendor/register',
                data=dict(name="Achme", state="NC"),
                follow_redirects=True)
        self.assertIn(b'Vendor already exist\n', response.data)
        self.assertEqual(response.status_code, 200)

    def test_validate_registration_form(self):
        form  = RegisterForm(name="Achme",
                        contact="", phone="",
                        website="www.achme.com",
                        line1="", line2="",
                        city="", state="NC",
                        zipcode="")
        self.assertTrue(form.validate())

    def test_view_purchase_order_404_with_unknown_id(self):
        with self.client:
            self.client.post(
                '/login',
                data=dict(email="ad@min.com", password="admin_user"),
                follow_redirects=True)
            response = self.client.get('/inventory/view_po/1001', follow_redirects=True)
        self.assertEqual(response.status_code, 404)

    def test_validate_purchase_order_form(self):
        form = PurchaseOrderForm(item="1", quantity="10", unit_price="2.99")
        self.assertTrue(form.validate())

    def test_invalid_purchase_order_form(self):
        form = PurchaseOrderForm(quantity="10", unit_price="2.99")
        self.assertFalse(form.validate())

if __name__ == '__main__':
    unittest.main()
