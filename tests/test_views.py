"""
PHASE 2 — Integration Tests: Views, Authentication, Cart, Orders
"""
import pytest
from decimal import Decimal
from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from core.models import Product, Cart, CartItem, Order, OrderItem


@pytest.fixture
def client_anon():
    return Client()


@pytest.fixture
def user(db):
    return User.objects.create_user(username='qauser', password='QApass@123', email='qa@test.com')


@pytest.fixture
def auth_client(user):
    c = Client()
    c.login(username='qauser', password='QApass@123')
    return c


@pytest.fixture
def product(db):
    return Product.objects.create(
        name='QA Frame', category='frames', price=Decimal('799.00'),
        size='8x10', material='Wood', description='QA test product', stock=10, is_active=True
    )


@pytest.fixture
def cart_with_item(user, product):
    cart = Cart.objects.create(user=user)
    CartItem.objects.create(cart=cart, product=product, quantity=1)
    return cart


# ── SMOKE TESTS: All Public Pages Load ──────────────────────────────────────
class TestPublicPages:
    PUBLIC_URLS = [
        ('home',     {}),
        ('frames',   {}),
        ('paintings',{}),
        ('about',    {}),
        ('contact',  {}),
        ('login',    {}),
        ('register', {}),
        ('service_paintings', {}),
    ]

    @pytest.mark.parametrize("url_name,kwargs", PUBLIC_URLS)
    def test_public_page_loads_200(self, client_anon, url_name, kwargs):
        url = reverse(url_name, kwargs=kwargs)
        resp = client_anon.get(url)
        assert resp.status_code == 200, f"{url_name} returned {resp.status_code}"

    def test_product_detail_loads(self, client_anon, product):
        url = reverse('product_detail', kwargs={'pk': product.pk})
        resp = client_anon.get(url)
        assert resp.status_code == 200

    def test_nonexistent_product_returns_404(self, client_anon, db):
        url = reverse('product_detail', kwargs={'pk': 99999})
        resp = client_anon.get(url)
        assert resp.status_code == 404

    def test_frames_contains_products(self, client_anon, product):
        resp = client_anon.get(reverse('frames'))
        assert b'QA Frame' in resp.content

    def test_paintings_page_category_filter(self, client_anon, db):
        p = Product.objects.create(
            name='QA Painting', category='paintings', price=500,
            size='12x16', material='Canvas', description='Test', stock=5, is_active=True
        )
        resp = client_anon.get(reverse('paintings'))
        assert b'QA Painting' in resp.content


# ── AUTHENTICATION TESTS ─────────────────────────────────────────────────────
class TestAuthentication:
    def test_register_get(self, client_anon):
        resp = client_anon.get(reverse('register'))
        assert resp.status_code == 200
        assert b'form' in resp.content.lower()

    def test_register_valid_user(self, client_anon, db):
        resp = client_anon.post(reverse('register'), {
            'first_name': 'Test', 'last_name': 'User',
            'username': 'newqauser', 'email': 'newqa@test.com',
            'password1': 'Str0ng@Pass!', 'password2': 'Str0ng@Pass!'
        }, follow=True)
        assert User.objects.filter(username='newqauser').exists()

    def test_register_duplicate_email_rejected(self, client_anon, user):
        resp = client_anon.post(reverse('register'), {
            'first_name': 'Test', 'last_name': 'User2',
            'username': 'anotheruser', 'email': 'qa@test.com',  # same email as fixture user
            'password1': 'Str0ng@Pass!', 'password2': 'Str0ng@Pass!'
        })
        assert resp.status_code == 200  # form re-rendered with error

    def test_register_password_mismatch_rejected(self, client_anon, db):
        resp = client_anon.post(reverse('register'), {
            'first_name': 'Test', 'last_name': 'User',
            'username': 'mismatch', 'email': 'mm@test.com',
            'password1': 'Str0ng@Pass!', 'password2': 'WrongPass!'
        })
        assert resp.status_code == 200  # stays on register

    def test_login_valid(self, client_anon, user):
        resp = client_anon.post(reverse('login'), {
            'username': 'qauser', 'password': 'QApass@123'
        }, follow=True)
        assert resp.status_code == 200
        assert '_auth_user_id' in client_anon.session

    def test_login_invalid_password(self, client_anon, user):
        resp = client_anon.post(reverse('login'), {
            'username': 'qauser', 'password': 'WrongPass!'
        })
        assert resp.status_code == 200
        assert '_auth_user_id' not in client_anon.session

    def test_login_nonexistent_user(self, client_anon, db):
        resp = client_anon.post(reverse('login'), {
            'username': 'ghost', 'password': 'Pass@1234'
        })
        assert '_auth_user_id' not in client_anon.session

    def test_logout_redirects(self, auth_client):
        resp = auth_client.post(reverse('logout'), follow=True)
        assert resp.status_code == 200

    def test_protected_pages_redirect_to_login(self, client_anon):
        protected = ['cart', 'checkout', 'order_list', 'profile']
        for page in protected:
            resp = client_anon.get(reverse(page))
            assert resp.status_code in [302, 301], f"{page} should redirect, got {resp.status_code}"


# ── CART TESTS ───────────────────────────────────────────────────────────────
class TestCart:
    def test_add_to_cart(self, auth_client, product):
        resp = auth_client.post(
            reverse('add_to_cart', kwargs={'product_id': product.pk}), follow=True
        )
        assert resp.status_code == 200
        assert CartItem.objects.filter(product=product).exists()

    def test_add_same_product_increments_quantity(self, auth_client, product):
        auth_client.post(reverse('add_to_cart', kwargs={'product_id': product.pk}))
        auth_client.post(reverse('add_to_cart', kwargs={'product_id': product.pk}))
        items = CartItem.objects.filter(product=product)
        total_qty = sum(i.quantity for i in items)
        assert total_qty >= 2

    def test_cart_page_loads(self, auth_client, cart_with_item, user):
        resp = auth_client.get(reverse('cart'))
        assert resp.status_code == 200

    def test_remove_from_cart(self, auth_client, cart_with_item):
        item = cart_with_item.items.first()
        resp = auth_client.post(
            reverse('remove_from_cart', kwargs={'item_id': item.pk}), follow=True
        )
        assert resp.status_code == 200
        assert not CartItem.objects.filter(pk=item.pk).exists()

    def test_add_nonexistent_product_returns_404(self, auth_client, db):
        resp = auth_client.post(reverse('add_to_cart', kwargs={'product_id': 99999}))
        assert resp.status_code == 404


# ── CHECKOUT TESTS ───────────────────────────────────────────────────────────
class TestCheckout:
    def test_checkout_requires_login(self, client_anon):
        resp = client_anon.get(reverse('checkout'))
        assert resp.status_code == 302

    def test_checkout_empty_cart_redirects(self, auth_client, user):
        # Ensure no cart items
        Cart.objects.filter(user=user).delete()
        resp = auth_client.get(reverse('checkout'), follow=True)
        assert resp.status_code == 200  # redirects to cart or home

    def test_checkout_with_items_loads(self, auth_client, cart_with_item):
        resp = auth_client.get(reverse('checkout'))
        assert resp.status_code == 200

    def test_checkout_post_cod_creates_order(self, auth_client, user, product, db):
        cart = Cart.objects.get_or_create(user=user)[0]
        CartItem.objects.get_or_create(cart=cart, product=product, defaults={'quantity': 1})
        resp = auth_client.post(reverse('checkout'), {
            'address_line1': '10 Test Road',
            'address_line2': '',
            'city': 'Chennai',
            'state': 'Tamil Nadu',
            'pincode': '600001',
            'phone': '9876543210',
            'payment_method': 'cod',
        }, follow=True)
        assert resp.status_code == 200
        assert Order.objects.filter(user=user).exists()


# ── ORDER TESTS ───────────────────────────────────────────────────────────────
class TestOrders:
    @pytest.fixture
    def order(self, user, product, db):
        o = Order.objects.create(
            user=user, total_amount=Decimal('799.00'), advance_paid=0,
            address_line1='10 Test Rd', city='Chennai', state='TN',
            pincode='600001', phone='9876543210', payment_method='cod', status='pending'
        )
        OrderItem.objects.create(order=o, product=product, quantity=1, price=product.price)
        return o

    def test_order_list_loads(self, auth_client):
        resp = auth_client.get(reverse('order_list'))
        assert resp.status_code == 200

    def test_order_detail_loads(self, auth_client, order):
        resp = auth_client.get(reverse('order_detail', kwargs={'pk': order.pk}))
        assert resp.status_code == 200

    def test_order_detail_wrong_user(self, db, product):
        other_user = User.objects.create_user(username='other', password='Pass@1234')
        c = Client()
        c.login(username='other', password='Pass@1234')
        o = Order.objects.create(
            user=User.objects.get(username='qauser') if User.objects.filter(username='qauser').exists()
            else User.objects.create_user('qauser2', password='Pass@1234'),
            total_amount=100, address_line1='A', city='B', state='C', pincode='D', phone='E'
        )
        resp = c.get(reverse('order_detail', kwargs={'pk': o.pk}))
        assert resp.status_code in [403, 404, 302]

    def test_cancel_pending_order(self, auth_client, order):
        resp = auth_client.post(
            reverse('cancel_order', kwargs={'pk': order.pk}), follow=True
        )
        assert resp.status_code == 200
        order.refresh_from_db()
        assert order.status == 'cancelled'
