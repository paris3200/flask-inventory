# tests/test_config.py


import unittest

from flask import current_app
from flask_testing import TestCase

from app import create_app

app = create_app()


class TestDevelopmentConfig(TestCase):

    def create_app(self):
        app.config.from_object('config.DevConfig')
        return app

    def test_app_is_development(self):
        self.assertTrue(app.config['DEBUG'] is True)
        self.assertTrue(app.config['WTF_CSRF_ENABLED'] is False)
        self.assertFalse(current_app is None)


class TestTestingConfig(TestCase):

    def create_app(self):
        app.config.from_object('config.TestingConfig')
        return app

    def test_app_is_testing(self):
        self.assertTrue(app.config['DEBUG'] is True)
        self.assertTrue(app.config['BCRYPT_LOG_ROUNDS'] == 1)
        self.assertTrue(app.config['WTF_CSRF_ENABLED'] is False)


class TestProductionConfig(TestCase):

    def create_app(self):
        app.config.from_object('config.ProductionConfig')
        return app

    def test_app_is_production(self):
        self.assertTrue(app.config['DEBUG'] is False)
        self.assertTrue(app.config['DEBUG_TB_ENABLED'] is False)
        self.assertTrue(app.config['WTF_CSRF_ENABLED'] is True)
        self.assertTrue(app.config['BCRYPT_LOG_ROUNDS'] == 13)


if __name__ == '__main__':
    unittest.main()
