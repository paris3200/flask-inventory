# tests/test_vendor.py


import unittest

from tests.base import BaseTestCase
from project.models import LineItem, Component, Vendor, VendorComponent
from project.inventory.forms import VendorCreateForm, PurchaseOrderForm, \
    ComponentCreateForm


class TestInventoryBlueprint(BaseTestCase):

    ########################
    ### Helper Functions ###
    ########################

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

    def create_component(self, description="widget"):
        self.login()
        return self.client.post(
            '/component/create',
            data=dict(sku="12345", description=description),
            follow_redirects=True)

    def create_vendor_component(self, description="widget"):
        self.login()
        return self.client.post(
            'vendor/1/component/create',
            data=dict(sku="12345", description=description, vendor_id=1),
            follow_redirects=True)

    def create_purchase_order(self, sku=12345, quantity=10):
        self.login()
        self.create_vendor()
        self.create_vendor_component()
        resp = self.client.get('/purchase_order/create/1', follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        return self.client.post('/purchase_order/create/1',
                                data=dict(sku=sku,
                                          quantity=quantity,
                                          total_price=2.00,
                                          user_id=1),
                                follow_redirects=True)

#############
### Tests ###
#############

    def test_model_print(self):
        self.login()
        self.create_vendor()
        vendor = Vendor.query.filter_by(name='Achme').first()
        self.assertIn('<Vendor Achme>', vendor.__repr__())

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
            response = self.create_vendor()
        self.assertIn(b'Vendor already exist.', response.data)
        self.assertEqual(response.status_code, 200)

    def test_edit_vendor_route_fails_with_invalid_vendor(self):
        with self.client:
            self.login()
            response = self.client.get('/vendor/edit/1000',
                                       follow_redirects=True)
            self.assertEqual(response.status_code, 404)

    # sku is not part of the create purchase_order wtform
    # component.id should be used instead.
    # In the future, an API can be written at the model class level
    # (SQLAlchemy) in order to create Purchase Orders and other tasks
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
            response = self.client.post(
                '/vendor/edit/1',
                data=dict(
                    name="Achme LLC",
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
        form = VendorCreateForm(name="Achme",
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
        form = PurchaseOrderForm(sku="1001", quantity="10", total_price="2.99",
                                 user_id="1")
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

    def test_create_vendor_component_database_insert(self):
        with self.client:
            self.login()
            self.create_vendor()
            self.create_vendor_component()
            response = self.client.get('/vendor/1/component/', follow_redirects=True)
            self.assertIn(b'<h1>Vendor Components</h1>', response.data)
            self.assertIn(b'widget', response.data)

    def test_create_vendor_component_exist_error(self):
        with self.client:
            self.login()
            self.create_vendor()
            self.create_vendor_component()
            response = self.create_vendor_component()
            self.assertIn(b'Component already exists', response.data)

    def test_view_all_vendor_component(self):
        with self.client:
            self.login()
            self.create_vendor()
            self.create_vendor_component()
            response = self.client.get('/vendor/1/component/', follow_redirects=True)
            self.assertIn(b'Vendor Components', response.data)

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
            self.assertIn(b'Component already exists', response.data)
            self.client.post('/component/create',
                    data=dict(sku="12345",
                    description='something'),
                    follow_redirects=True)
            self.assertIn(b'Component already exists', response.data)

    def test_lineitem_total(self):
        with self.client:
            self.login()
            self.create_vendor_component()

        widget = VendorComponent.query.get(1)
        lineitem = LineItem(vendor_component=widget, quantity=10, total_price=10.00)
        self.assertEqual(lineitem.total_price, 10.00)

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
            self.assertIn(b'Total: 2.00', response.data)

    def test_view_purchase_order_all(self):
        with self.client:
            self.login()
            self.create_purchase_order()
            response = self.client.get('/purchase_order/',
                                       follow_redirects=True)
            self.assertIn(b'<h1>Purchase Orders</h1>', response.data)
            self.assertIn(b'ad@min.com', response.data)

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
            response = self.client.get(
                '/tag-component/1',
                follow_redirects=True)
            self.assertIn(b'WEST COAST', response.data)

    def test_checkin_updates_transactions(self):
        with self.client:
            self.login()
            self.create_component()
            self.client.post(
                '/transactions/check-in',
                data=dict(component='1',
                          qty='6',
                          notes="Checking in 6 of em\'",
                          checkin="Check In",
                          user_id="1"))
            response = self.client.get('/transactions/')
            self.assertIn(b'1', response.data)
            self.assertIn(b'6', response.data)
            self.assertIn(b'Checking in 6 of em', response.data)
            self.assertIn(b'ad@min.com', response.data)

    def test_checkout_fails_availibility_exceeds_quantity(self):
        with self.client:
            self.login()
            self.create_component()
            self.client.post(
                '/transactions/check-in',
                data=dict(component='1',
                          qty='6',
                          notes="Checking in 6 of em\'",
                          checkin="Check In",
                          user_id="1"))
            response = self.client.post(
                '/transactions/check-out',
                data=dict(component='1',
                          qty='10',
                          notes="Checking out 10 of em\'",
                          checkout="Check Out",
                          user_id="1"),
                follow_redirects=True)
            self.assertIn(b'Not enough items', response.data)

    def test_checkout_succeeds_availibility_less_quantity(self):
        with self.client:
            self.login()
            self.create_component()
            self.client.post(
                '/transactions/check-in',
                data=dict(component='1',
                          qty='6',
                          notes="Checking in 6 of em\'",
                          checkin="Check In",
                          user_id="1"))
            response = self.client.post(
                '/transactions/check-out',
                data=dict(component='1',
                          qty='2',
                          notes="Checking out 6 of em\'",
                          checkout="Check Out",
                          user_id="1"),
                follow_redirects=True)
            self.assertIn(b'Success: Items Checked Out', response.data)

    def test_checkin_checkout(self):
        with self.client:
            self.login()
            self.create_component()
            response = self.client.post(
                '/transactions/check-in',
                data=dict(component='1',
                          qty='6',
                          notes="Checking in 6 of em\'",
                          checkin="Check In",
                          user_id="1"),
                follow_redirects=True)
            self.assertIn(b'Items Checked In', response.data)
            response = self.client.post(
                '/transactions/check-in',
                data=dict(component='1',
                          qty='',
                          notes="Checking in 6 of em\'",
                          checkin="Check In",
                          user_id="1"),
                follow_redirects=True)
            self.assertIn(b'qty', response.data)
            response = self.client.post(
                '/transactions/check-out',
                data=dict(component='1',
                          qty='',
                          notes="Checking out 6 of em\'",
                          checkout="Check Out",
                          user_id="1"),
                follow_redirects=True)
            self.assertIn(b'qty', response.data)
