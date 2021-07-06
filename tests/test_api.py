# tests/test_api.py


import unittest

from app.models import Component, Tag
from tests.base import BaseTestCase


from flask import jsonify
import json

class TestApi(BaseTestCase):
    def login(self):
        self.client.post(
            '/login',
            data=dict(email="ad@min.com", password="admin_user"),
            follow_redirects=True
        )
    def create_single_tag(self):
        with self.client:
            self.login()
            response = self.client.get(
                '/manage-tags',
                follow_redirects=True)
            # creating cats and tags should strip down form data
            new_single_tag = 'lonely tag '
            response = self.client.post(
                '/manage-tags',
                data=dict(category='',
                          tag_name=new_single_tag,
                          make="OK"),
                follow_redirects=True)

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

    def create_purchase_order(self, sku=12345, quantity=10):
        self.login()
        self.create_vendor()
        self.create_component()
        return self.client.post('/purchase_order/create/1',
                                data=dict(sku=sku,
                                          quantity=quantity,
                                          total_price=2.00,
                                          user_id=1),
                                follow_redirects=True)

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
        self.create_component()
        response = self.client.get('/api/components/1', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'widget', response.data)

    def test_delete_tag(self):
        self.create_single_tag()
        tag = Tag.query.first()
        self.assertEqual(tag.id, 1)
        tag_id = tag.id
        response = self.client.delete('/api/tag/'+'39282')
        self.assertEqual(response.status_code, 404)
        response = self.client.delete('/api/tag/'+str(tag_id))
        self.assertEqual(str(tag_id).encode(),response.data.strip())

    def test_remove_tag(self):
        # tag a component
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
        component = Component.query.get(1)
        tag_id = Tag.query.filter_by(name='WEST COAST').first().id
        response = self.client.delete('/api/component-tags/%s/%s' % (component.id, tag_id))
        response = self.client.delete('/api/tag/'+str(tag_id))
        self.assertEqual(str(tag_id).encode(),response.data.strip())

    def test_tag_component(self):
        # tag a component
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
        component = Component.query.get(1)
        tag_id = Tag.query.filter_by(name='WEST COAST').first().id
        response = self.client.put('/api/component-tags/%s' % (1, ),
                data = json.dumps({'tag_text':'MY tag  ','cat_text':'  custom Cat'}),
                content_type = 'application/json'
            )
        response = self.client.get('/api/components/1', follow_redirects=True)
        self.assertIn(b'MY TAG', response.data)

        response = self.client.get('/api/categories', follow_redirects=True)
        self.assertIn(b'CUSTOM CAT', response.data)        
        # with self.client:
        #     self.login()
        #     self.create_component()
        #     response = self.client.post(
        #         '/tag-component/1',
        #         data=dict(category='Region',
        #                   tag_name='west coast'),
        #         follow_redirects=True)
        #     self.assertIn(b'CUSTOM CAT', response.data)
        #     self.assertIn(b'MY TAG', response.data)
        


    def test_update_component(self):
        with self.app.test_client() as c:
            response = c.post(
                    '/login',
                    data=dict(email="ad@min.com", password="admin_user"),
                    follow_redirects=True
                )
            self.create_component()
            response = c.put('/api/components/900',
                data = json.dumps({'sku':'sku123','description':'should fail'}),
                content_type='application/json')
            response = c.put('/api/components/1',
                data = json.dumps({'sku':'OK123','description':'should update'}),
                content_type='application/json')
            comp = Component.query.get(1)
            # raise ValueError(comp.sku)
            self.assertEqual(comp.sku, u'OK123')
            self.assertEqual(comp.description, u'should update')
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
