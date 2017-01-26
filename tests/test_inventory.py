# tests/test_vendor.py


import unittest

from tests.base import BaseTestCase
from project.models import LineItem, Component
from project.inventory.forms import VendorCreateForm, PurchaseOrderForm, \
    ComponentCreateForm


class TestInventoryBlueprint(BaseTestCase):

    def login(self):
        self.client.post(
            '/login',
            data=dict(email="ad@min.com", password="admin_user"),
            follow_redirects=True
        )

    def create_vendor(self, vendorName="Achme",
                        vendoraddress="123 Coyote Ln",
                        vendorcity="Desert Plain",
                        vendorState="CO",
                        vendorWebsite="http://www.achme.com"):
            self.login()
            return self.client.post(
                '/vendor/create',
                data=dict(name=vendorName,
                          line1=vendoraddress,
                          city=vendorcity,
                          state=vendorState,
                          website=vendorWebsite),
                follow_redirects=True)

    def test_create_vendor_route(self):
        # Ensure register behaves correctly when logged in.
        with self.client:
            self.login()
            # Ensure about route behaves correctly.
            response = self.client.get('/vendor/create', follow_redirects=True)
            self.assertIn(b'<h1>Create Vendor</h1>\n', response.data)

    def test_create_vendor_website_not_required(self):
        with self.client:
            self.login()
            response = self.create_vendor(vendorWebsite="")
        self.assertIn(b'<h1>Vendors</h1>', response.data)
        self.assertEqual(response.status_code, 200)

    def test_create_vendor_route_requires_login(self):
        # Ensure member route requres logged in user.
        response = self.client.get('/vendor/create', follow_redirects=True)
        self.assertIn(b'Please log in to access this page', response.data)

    def test_vendor_registration(self):
        with self.client:
            self.login()
            response = self.create_vendor()
            self.assertIn(b'<h1>Vendors</h1>', response.data)
            self.assertEqual(response.status_code, 200)

    def test_vendor_disallows_duplicate_registration(self):
        with self.client:
            self.login()
            self.create_vendor()
            response=self.create_vendor()
        self.assertIn(b'Vendor already exist.', response.data)
        self.assertEqual(response.status_code, 200)

    def test_edit_vendor_route_fails_with_invalid_vendor(self):
        with self.client:
            self.login()
            response = self.client.get('/vendor/edit/1000',
                                       follow_redirects=True)
            self.assertEqual(response.status_code, 404)

    def create_component(self, description="widget"):
        self.login()
        return self.client.post(
            '/component/create',
            data=dict(sku="12345", description=description),
            follow_redirects=True)


    def create_purchase_order(self, sku=1001, quantity=10):
        self.login()
        self.create_vendor()
        self.create_component()
        return self.client.post('/purchase_order/create/1',
                         data=dict(sku=sku, quantity=quantity, total_price=2),
                         follow_redirects=True)

    def test_view_all_vendors(self):
        with self.client:
            self.login()
            response = self.client.get('/vendor/', follow_redirects=True)
            self.assertIn(b'<h1>Vendors</h1>\n', response.data)

    def test_view_vendor(self):
        with self.client:
            self.login()
            self.create_vendor()
            response = self.client.get('/vendor/1', follow_redirects=True)
            self.assertIn(b'Achme', response.data)
            self.assertIn(b'123 Coyote Ln', response.data)
            self.assertIn(b'Desert Plain', response.data)
            self.assertIn(b'CO', response.data)

    def test_edit_route_with_valid_vendor(self):
        # Ensure edit route behaves correctly when logged in.
        with self.client:
            self.login()
            self.create_vendor()
            response = self.client.get('/vendor/edit/1',
                                       follow_redirects=True)
            self.assertIn(b'<h1>Edit Vendor</h1>\n', response.data)
            self.assertIn(b'value="Achme"', response.data)

    def test_edit_updates_to_database(self):
        with self.client:
            self.login()
            self.create_vendor()
            response = self.client.post('/vendor/edit/1',
                                    data=dict(name="Achme LLC",
                                              state="NC",
                                              website="http://www.achme.com"),
                                    follow_redirects=True)
        self.assertIn(b'<h1>Vendors</h1>\n', response.data)
        self.assertIn(b'Achme LLC', response.data)

    def test_view_route_requires_login(self):
        # Ensure member route requres logged in user.
        response = self.client.get('/vendor/', follow_redirects=True)
        self.assertIn(b'Please log in to access this page', response.data)

    def test_edit_route_requires_login(self):
        # Ensure member route requres logged in user.
        response = self.client.get('/vendor/edit/1', follow_redirects=True)
        self.assertIn(b'Please log in to access this page', response.data)

    def test_validate_registration_form(self):
        form  = VendorCreateForm(name="Achme",
                        contact="", phone="",
                        website="http://www.achme.com",
                        line1="", line2="",
                        city="", state="NC",
                        zipcode="")
        self.assertTrue(form.validate())

    def test_view_purchase_order_404_with_unknown_id(self):
        with self.client:
            self.login()
            response = self.client.get('/inventory/view_po/1001',
                                       follow_redirects=True)
            self.assertEqual(response.status_code, 404)

    def test_validate_purchase_order_form_data(self):
        form = PurchaseOrderForm(sku="1001", quantity="10", total_price="2.99")
        self.assertTrue(form.validate())

    def test_invalid_purchase_order_form(self):
        form = PurchaseOrderForm(quantity="10", unit_price="2.99")
        self.assertFalse(form.validate())

    def test_validate_component_create_form(self):
        form = ComponentCreateForm(sku="12345", description="Widget")
        self.assertTrue(form.validate())

    def test_invalidate_create_component_form(self):
        form = PurchaseOrderForm(name=False)
        self.assertFalse(form.validate())

    def test_create_component_database_insert(self):
        with self.client:
            self.login()
            self.create_component()
            response = self.client.get('/component/', follow_redirects=True)
            self.assertIn(b'<h1>Components</h1>', response.data)
            self.assertIn(b'widget', response.data)

    def test_create_component_exist_error(self):
        with self.client:
            self.login()
            self.create_component()
            response = self.create_component("widget")
            self.assertIn(b'Component already exist.', response.data)

    def test_lineitem_total(self):
        with self.client:
            self.login()
            self.create_component()

        widget = Component.query.get(1)
        lineitem = LineItem(component=widget, quantity=10, total_price=10.00)
        self.assertTrue(lineitem.total_price, 1.00)

    def test_view_purchase_order(self):
        with self.client:
            self.login()
            self.create_purchase_order()
            response = self.client.get('/purchase_order/1',
                                       follow_redirects=True)
            self.assertIn(b'Achme', response.data)
            self.assertIn(b'CO', response.data)
            self.assertIn(b'http://www.achme.com', response.data)
            self.assertIn(b'SKU', response.data)

    def test_view_purchase_order_all(self):
        with self.client:
            self.login()
            self.create_purchase_order()
            response = self.client.get('/purchase_order/',
                                       follow_redirects=True)
            self.assertIn(b'<h1>Purchase Orders</h1>', response.data)

    def test_create_purchaseorder_requires_valid_input(self):
        with self.client:
            self.login()
            response = self.create_purchase_order(False)
            self.assertIn(b'<h1>Purchase Order</h1>', response.data)

    def test_create_purchaseorder_requires_valid_component(self):
        with self.client:
            self.login()
            response = self.create_purchase_order(sku=1001)
            self.assertIn(b'<h1>Purchase Order</h1>', response.data)
            self.assertIn(b'Component not found.', response.data)

    def test_view_component(self):
        with self.client:
            self.login()
            self.create_component()
            response = self.client.get('/component/1', follow_redirects=True)
            self.assertIn(b'widget', response.data)
            if __name__ == '__main__':
                unittest.main()

    def test_tag_component(self):
        with self.client:
            self.login()
            self.create_component()
            response = self.client.post(
                '/tag-component/1',
                data=dict(category='Region',
                          tag_name='west coast'),
                follow_redirects=True)
            self.assertIn(b'has been tagged with', response.data)
            self.assertIn(b'WEST COAST', response.data)

