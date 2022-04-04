import json
import unittest

from flask import request
from flask_login import current_user
from werkzeug.security import check_password_hash

from bookreview import create_app, db
from bookreview.config import TestConfig
from bookreview.models import User, Role


class TestUserActivity(unittest.TestCase):

    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.create_roles()
        self.client = self.app.test_client(use_cookies=True)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def create_user(self):
        new_user = User(login='user', email='my@email.com', password="1234")
        db.session.add(new_user)
        db.session.commit()
        return new_user

    def test_registration_user(self):
        new_user = self.create_user()
        self.assertTrue(User.query.filter_by(login=new_user.login).first())

    def test_user_confirmed_status_after_registration(self):
        new_user = self.create_user()
        self.assertFalse(User.query.filter_by(login=new_user.login).first().confirmed)

    def test_user_role_after_registration(self):
        new_user = self.create_user()
        self.assertEqual(User.query.filter_by(login=new_user.login).first().role,
                         Role.query.filter_by(role='UnconfirmedUser').first())

