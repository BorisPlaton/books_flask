import re
import unittest

from bookreview import create_app, db
from bookreview.config import TestConfig
from bookreview.models import User, Role, Book, Review


class TestUserActivity(unittest.TestCase):

    def setUp(self):
        self.app = create_app(TestConfig)
        self.app.config['WTF_CSRF_METHODS'] = []
        self.app.config["WTF_CSRF_ENABLED"] = False
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.create_roles()
        self.client = self.app.test_client(use_cookies=True)

        self.new_user = self.create_user()
        db.session.add(self.new_user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def create_user(self):
        new_user = User(
            login='user',
            email='my@email.com',
            password="1234")
        db.session.add(new_user)
        db.session.commit()
        return new_user

    def test_registration_user(self):
        self.assertTrue(User.query.filter_by(login=self.new_user.login).first())

    def test_user_confirmed_status_after_registration(self):
        self.assertFalse(User.query.filter_by(login=self.new_user.login).first().confirmed)

    def test_user_role_after_registration(self):
        self.assertEqual(User.query.filter_by(login=self.new_user.login).first().role,
                         Role.query.filter_by(role='UnconfirmedUser').first())

    def test_check_password_hash_after_registration(self):
        self.assertNotEqual(self.new_user.password, "1234")

    def test_home_page(self):
        response = self.client.get("/")
        self.assertFalse("Мой профиль" in response.get_data(as_text=True))

    def test_home_page_after_login(self):
        response = self.client.get("/login")
        self.assertEqual(response.status_code, 200)
        response = self.client.post("/login", json={
            "login": self.new_user.login,
            "password": "1234qwerty"
        }, follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertTrue(re.search("Неверный пароль", data))
        response = self.client.post("/login", data={
            "login": self.new_user.login,
            "password": "1234"
        }, follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertTrue(re.search("Мой профиль", data))

    def test_user_registration(self):
        response = self.client.post('/register', data={
            'login': "user1",
            'email': 'email@email.com',
            'password': '1234',
            'confirm_password': '12345',
        }, follow_redirects=True)
        self.assertTrue(re.search('Пароли должны совпадать', response.get_data(as_text=True)))
        response = self.client.post('/register', data={
            'login': "user1",
            'email': 'email@email.com',
            'password': '1234',
            'confirm_password': '1234',
        }, follow_redirects=True)
        self.assertTrue(re.search('На вашу почту отправлено письмо для подтверждения регистрации аккаунта', response.get_data(as_text=True)))

    def test_month_translation(self):
        from bookreview.utils import month_translate
        month = 'March'
        rus_month = month_translate(month)
        self.assertEqual(rus_month, 'Марта')
        month = '11'
        rus_month = month_translate(month)
        self.assertFalse(rus_month)
        month = '22 february'
        rus_month = month_translate(month)
        self.assertEqual(rus_month, '22 Февраля')

    def test_create_fake_db_data(self):
        from bookreview.utils import create_fake_db_data
        create_fake_db_data(amount_users=15, amount_reviews=15, amount_books=15)
        self.assertTrue(len(User.query.all()) <= 15)
        self.assertTrue(len(Book.query.all()) <= 15)
        self.assertTrue(len(Review.query.all()) <= 15)

    def test_unconfirmed_user_permissions(self):
        response = self.client.post("/login", data={
            "login": self.new_user.login,
            "password": "1234"
        }, follow_redirects=True)
        response = self.client.get(f'/books/{self.new_user.id}')
        self.assertTrue(re.search(''))

