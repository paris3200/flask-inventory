# tests/test_vendor.py


import unittest

from tests.base import BaseTestCase
from project.models import LineItem, Component
from project.inventory.forms import VendorCreateForm, PurchaseOrderForm, \
    ComponentCreateForm
import json

class TestTagManagement(BaseTestCase):

    def login(self):
        self.client.post(
            '/login',
            data=dict(email="ad@min.com", password="admin_user"),
            follow_redirects=True
        )

    def create_component(self, description="widget"):
        self.login()
        return self.client.post(
            '/component/create',
            data=dict(sku="12345", description=description),
            follow_redirects=True)

    def test_create_component_database_insert(self):
        with self.client:
            self.login()
            self.create_component()
            response = self.client.get('/component/', follow_redirects=True)
            self.assertIn(b'<h1>Components</h1>', response.data)
            self.assertIn(b'widget', response.data)

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

    def test_create_single_tag(self):
        with self.client:
            self.login()
            response = self.client.get(
                '/manage-tags',
                follow_redirects=True)
            self.assertIn(b'Tag Manager', response.data)
            # creating cats and tags should strip down form data
            new_single_tag = 'lonely tag '
            response = self.client.post(
                '/manage-tags',
                data=dict(category='',
                          tag_name=new_single_tag,
                          make="OK"),
                follow_redirects=True)
            self.assertIn(new_single_tag.strip().upper(), response.data)
            response = self.client.get(
                '/api/single-tags')
            self.assertIn(new_single_tag.strip().upper(), response.data)

    def test_create_tag_in_category(self):
        with self.client:
            self.login()
            # creating cats and tags should strip down form data
            tag_in_cat = ' tag in cat '
            the_cat = '  the category  '
            response = self.client.post(
                '/manage-tags',
                data=dict(category=the_cat,
                          tag_name=tag_in_cat,
                          make="OK"),
                follow_redirects=True)
            self.assertIn("%s</span>:<span>%s" % (the_cat.strip().upper(), tag_in_cat.strip().upper()), response.data)
            response = self.client.get(
                '/api/categories')
            print 'the json'
            the_cat_with_tag = json.loads(response.data)
            print the_cat_with_tag
            self.assertEqual(
                the_cat_with_tag[0]['tags'][0]['name'],
                tag_in_cat.strip().upper())