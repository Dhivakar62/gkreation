"""
PHASE 2 — Security Tests: XSS, CSRF, SQL Injection, Auth, Session
"""
import pytest
from django.test import Client
from django.urls import reverse
from django.contrib.auth.models import User
from core.models import Product


@pytest.fixture
def client_anon():
    return Client()


@pytest.fixture
def user(db):
    return User.objects.create_user(username='secuser', password='Sec@Pass123')


# ── XSS TESTS ────────────────────────────────────────────────────────────────
class TestXSS:
    XSS_PAYLOADS = [
        '<script>alert(1)</script>',
        '"><script>alert(1)</script>',
        "';alert('xss');",
        '<img src=x onerror=alert(1)>',
        'javascript:alert(1)',
    ]

    @pytest.mark.parametrize("payload", XSS_PAYLOADS)
    def test_register_xss_in_username(self, client_anon, db, payload):
        resp = client_anon.post(reverse('register'), {
            'first_name': payload, 'last_name': 'Test',
            'username': 'xsstest', 'email': 'xss@test.com',
            'password1': 'Str0ng@Pass!', 'password2': 'Str0ng@Pass!'
        })
        # XSS payload must NOT appear unescaped in response
        content = resp.content.decode()
        assert '<script>alert(1)</script>' not in content

    @pytest.mark.parametrize("payload", XSS_PAYLOADS)
    def test_contact_form_xss(self, client_anon, payload):
        resp = client_anon.post(reverse('contact'), {
            'name': payload, 'email': 'x@x.com',
            'subject': payload, 'message': payload
        })
        content = resp.content.decode()
        assert '<script>alert(1)</script>' not in content


# ── CSRF TESTS ────────────────────────────────────────────────────────────────
class TestCSRF:
    def test_csrf_enforced_on_login(self, client_anon, user):
        # Client without CSRF enforcement — Django test client bypasses this
        # but we verify CSRF middleware is active
        from django.middleware.csrf import CsrfViewMiddleware
        from django.conf import settings
        assert 'django.middleware.csrf.CsrfViewMiddleware' in settings.MIDDLEWARE

    def test_login_requires_post_not_get_for_auth(self, client_anon, user):
        # GET to login should not authenticate
        resp = client_anon.get(reverse('login'))
        assert '_auth_user_id' not in client_anon.session

    def test_csrf_token_present_in_form(self, client_anon):
        resp = client_anon.get(reverse('login'))
        assert b'csrfmiddlewaretoken' in resp.content


# ── SQL INJECTION TESTS ───────────────────────────────────────────────────────
class TestSQLInjection:
    SQL_PAYLOADS = [
        "' OR 1=1 --",
        "'; DROP TABLE users; --",
        "' UNION SELECT * FROM auth_user --",
        "1' AND '1'='1",
        "admin'--",
    ]

    @pytest.mark.parametrize("payload", SQL_PAYLOADS)
    def test_sql_injection_in_login_username(self, client_anon, db, payload):
        resp = client_anon.post(reverse('login'), {
            'username': payload, 'password': 'anypass'
        })
        # Must NOT be authenticated — injection must fail
        assert '_auth_user_id' not in client_anon.session

    @pytest.mark.parametrize("payload", SQL_PAYLOADS)
    def test_sql_injection_in_register(self, client_anon, db, payload):
        resp = client_anon.post(reverse('register'), {
            'first_name': payload, 'last_name': 'Test',
            'username': 'sqlinj_user', 'email': 'sqlinj@test.com',
            'password1': 'Str0ng@Pass!', 'password2': 'Str0ng@Pass!'
        })
        # App should not crash (500)
        assert resp.status_code != 500


# ── BROKEN AUTH TESTS ─────────────────────────────────────────────────────────
class TestBrokenAuth:
    def test_direct_order_access_blocked(self, client_anon, db):
        resp = client_anon.get(reverse('order_list'))
        assert resp.status_code == 302
        assert '/login' in resp['Location'] or 'login' in resp['Location']

    def test_direct_checkout_blocked(self, client_anon, db):
        resp = client_anon.get(reverse('checkout'))
        assert resp.status_code == 302

    def test_profile_access_blocked(self, client_anon, db):
        resp = client_anon.get(reverse('profile'))
        assert resp.status_code == 302

    def test_order_detail_wrong_user_blocked(self, db):
        u1 = User.objects.create_user(username='owner', password='Pass@1234')
        u2 = User.objects.create_user(username='attacker', password='Pass@1234')
        from core.models import Order
        o = Order.objects.create(
            user=u1, total_amount=100,
            address_line1='A', city='B', state='C', pincode='D', phone='E'
        )
        c = Client()
        c.login(username='attacker', password='Pass@1234')
        resp = c.get(reverse('order_detail', kwargs={'pk': o.pk}))
        assert resp.status_code in [403, 404, 302]

    def test_admin_panel_blocks_regular_user(self, db):
        u = User.objects.create_user(username='regular', password='Pass@1234')
        c = Client()
        c.login(username='regular', password='Pass@1234')
        resp = c.get('/admin/')
        assert resp.status_code in [302, 403]


# ── SECURITY HEADERS ──────────────────────────────────────────────────────────
class TestSecuritySettings:
    def test_debug_is_false(self):
        from django.conf import settings
        assert settings.DEBUG is False

    def test_secret_key_not_default(self):
        from django.conf import settings
        assert 'insecure' not in settings.SECRET_KEY.lower()
        assert len(settings.SECRET_KEY) > 20

    def test_whitenoise_in_middleware(self):
        from django.conf import settings
        mw_list = settings.MIDDLEWARE
        assert any('whitenoise' in m.lower() for m in mw_list)

    def test_security_middleware_present(self):
        from django.conf import settings
        assert 'django.middleware.security.SecurityMiddleware' in settings.MIDDLEWARE

    def test_csrf_middleware_present(self):
        from django.conf import settings
        assert 'django.middleware.csrf.CsrfViewMiddleware' in settings.MIDDLEWARE

    def test_static_url_configured(self):
        from django.conf import settings
        assert settings.STATIC_URL

    def test_allowed_hosts_not_wildcard(self):
        from django.conf import settings
        assert '*' not in settings.ALLOWED_HOSTS
