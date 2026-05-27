"""
PHASE 2 — Form Validation Tests
"""
import pytest
from django.contrib.auth.models import User
from core.forms import RegisterForm, LoginForm, CheckoutForm, CustomizationForm


class TestRegisterForm:
    def _valid_data(self):
        return {
            'first_name': 'John', 'last_name': 'Doe',
            'username': 'johndoe', 'email': 'john@test.com',
            'password1': 'Str0ng@Pass!', 'password2': 'Str0ng@Pass!'
        }

    def test_valid_form(self, db):
        f = RegisterForm(data=self._valid_data())
        assert f.is_valid(), f.errors

    def test_missing_first_name(self, db):
        d = self._valid_data(); d['first_name'] = ''
        f = RegisterForm(data=d)
        assert not f.is_valid()
        assert 'first_name' in f.errors

    def test_missing_email(self, db):
        d = self._valid_data(); d['email'] = ''
        f = RegisterForm(data=d)
        assert not f.is_valid()

    def test_invalid_email_format(self, db):
        d = self._valid_data(); d['email'] = 'notanemail'
        f = RegisterForm(data=d)
        assert not f.is_valid()

    def test_duplicate_email_rejected(self, db):
        User.objects.create_user(username='existing', email='taken@test.com', password='Pass@123')
        d = self._valid_data(); d['email'] = 'taken@test.com'
        f = RegisterForm(data=d)
        assert not f.is_valid()
        assert 'email' in f.errors

    def test_password_mismatch(self, db):
        d = self._valid_data(); d['password2'] = 'Different@Pass!'
        f = RegisterForm(data=d)
        assert not f.is_valid()

    def test_weak_password_rejected(self, db):
        d = self._valid_data(); d['password1'] = d['password2'] = '12345'
        f = RegisterForm(data=d)
        assert not f.is_valid()


class TestLoginForm:
    def test_valid_login_form(self):
        f = LoginForm(data={'username': 'user', 'password': 'pass'})
        assert f.is_valid()

    def test_empty_username(self):
        f = LoginForm(data={'username': '', 'password': 'pass'})
        assert not f.is_valid()

    def test_empty_password(self):
        f = LoginForm(data={'username': 'user', 'password': ''})
        assert not f.is_valid()


class TestCheckoutForm:
    def _valid_data(self):
        return {
            'address_line1': '10 Main St', 'address_line2': '',
            'city': 'Chennai', 'state': 'TN',
            'pincode': '600001', 'phone': '9876543210',
            'payment_method': 'cod'
        }

    def test_valid_checkout_form(self):
        f = CheckoutForm(data=self._valid_data())
        assert f.is_valid(), f.errors

    def test_missing_address_rejected(self):
        d = self._valid_data(); d['address_line1'] = ''
        f = CheckoutForm(data=d)
        assert not f.is_valid()

    def test_missing_city_rejected(self):
        d = self._valid_data(); d['city'] = ''
        f = CheckoutForm(data=d)
        assert not f.is_valid()

    def test_missing_phone_rejected(self):
        d = self._valid_data(); d['phone'] = ''
        f = CheckoutForm(data=d)
        assert not f.is_valid()

    def test_invalid_payment_method(self):
        d = self._valid_data(); d['payment_method'] = 'bitcoin'
        f = CheckoutForm(data=d)
        assert not f.is_valid()

    def test_razorpay_payment_valid(self):
        d = self._valid_data(); d['payment_method'] = 'razorpay'
        f = CheckoutForm(data=d)
        assert f.is_valid()
