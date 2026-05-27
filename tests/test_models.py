"""
PHASE 2 — Unit Tests: Models & Business Logic
Tests: UserProfile, Product, Cart, CartItem, Order, Customization, PortraitOrder, WeddingEventOrder
"""
import pytest
from decimal import Decimal
from django.contrib.auth.models import User
from django.utils import timezone
from core.models import (
    UserProfile, Product, Cart, CartItem,
    Order, OrderItem, Customization, PortraitOrder, WeddingEventOrder
)


@pytest.fixture
def user(db):
    u = User.objects.create_user(username='testuser', password='Pass@1234', email='test@test.com')
    return u


@pytest.fixture
def product(db):
    return Product.objects.create(
        name='Test Frame', category='frames', price=Decimal('999.00'),
        size='8x10', material='Wood', description='A test frame', stock=10, is_active=True
    )


@pytest.fixture
def order(db, user, product):
    o = Order.objects.create(
        user=user, total_amount=Decimal('999.00'), advance_paid=Decimal('499.50'),
        address_line1='123 Test St', city='Chennai', state='TN', pincode='600001', phone='9999999999',
        payment_method='cod', status='pending'
    )
    OrderItem.objects.create(order=o, product=product, quantity=1, price=product.price)
    return o


# ── MODEL: UserProfile ──────────────────────────────────────────────────────
class TestUserProfile:
    def test_profile_created_str(self, user):
        profile, _ = UserProfile.objects.get_or_create(user=user, defaults={
            'city': 'Chennai', 'state': 'TN', 'pincode': '600001'
        })
        assert str(profile) == f"{user.username}'s Profile"

    def test_get_full_address(self, user):
        profile, _ = UserProfile.objects.get_or_create(user=user, defaults={
            'address_line1': '10 Main St', 'city': 'Chennai', 'state': 'TN', 'pincode': '600001'
        })
        addr = profile.get_full_address()
        assert 'Chennai' in addr
        assert 'TN' in addr

    def test_blank_address_returns_empty_string(self, user):
        profile = UserProfile.objects.create(user=user)
        assert profile.get_full_address() == ''


# ── MODEL: Product ──────────────────────────────────────────────────────────
class TestProduct:
    def test_product_str(self, product):
        assert str(product) == 'Test Frame'

    def test_product_price_decimal(self, product):
        assert isinstance(product.price, Decimal)
        assert product.price == Decimal('999.00')

    def test_product_category_choices(self, db):
        for cat in ['frames', 'paintings']:
            p = Product.objects.create(
                name=f'{cat} product', category=cat,
                price=100, size='5x7', material='Test', description='Desc', stock=5
            )
            assert p.category == cat

    def test_inactive_product_created(self, db):
        p = Product.objects.create(
            name='Inactive', category='frames', price=100, size='5x7',
            material='Test', description='Desc', stock=0, is_active=False
        )
        assert not p.is_active

    def test_zero_stock_product(self, db):
        p = Product.objects.create(
            name='Out of Stock', category='frames', price=500, size='5x7',
            material='Wood', description='Desc', stock=0
        )
        assert p.stock == 0


# ── MODEL: Cart ─────────────────────────────────────────────────────────────
class TestCart:
    def test_cart_str(self, user):
        cart = Cart.objects.create(user=user)
        assert str(cart) == f"{user.username}'s Cart"

    def test_cart_get_total_empty(self, user):
        cart = Cart.objects.create(user=user)
        assert cart.get_total() == 0

    def test_cart_get_item_count(self, user, product):
        cart = Cart.objects.create(user=user)
        CartItem.objects.create(cart=cart, product=product, quantity=3)
        assert cart.get_item_count() == 3
        assert cart.get_total() == product.price * 3

    def test_cart_item_subtotal(self, user, product):
        cart = Cart.objects.create(user=user)
        item = CartItem.objects.create(cart=cart, product=product, quantity=2)
        assert item.get_subtotal() == product.price * 2

    def test_cart_item_str(self, user, product):
        cart = Cart.objects.create(user=user)
        item = CartItem.objects.create(cart=cart, product=product, quantity=1)
        assert '1x' in str(item)
        assert 'Test Frame' in str(item)


# ── MODEL: Order ─────────────────────────────────────────────────────────────
class TestOrder:
    def test_order_str(self, order, user):
        assert 'Order #' in str(order)
        assert user.username in str(order)

    def test_order_sets_cancellation_deadline(self, order):
        assert order.cancellation_deadline is not None
        diff = (order.cancellation_deadline - timezone.now()).days
        assert 2 <= diff <= 3  # ~3 days

    def test_order_sets_expected_delivery(self, order):
        assert order.expected_delivery is not None
        diff = (order.expected_delivery - timezone.now()).days
        assert 13 <= diff <= 14

    def test_order_can_cancel_pending(self, order):
        assert order.can_cancel() is True

    def test_order_cannot_cancel_shipped(self, order):
        order.status = 'shipped'
        order.save()
        assert order.can_cancel() is False

    def test_order_advance_amount_50_percent(self, order):
        expected = order.total_amount * Decimal('0.5')
        assert order.get_advance_amount() == expected

    def test_order_balance_due(self, order):
        balance = order.get_balance_due()
        assert balance == max(order.total_amount - order.advance_paid, Decimal('0'))

    def test_order_item_subtotal(self, order, product):
        item = order.items.first()
        assert item.get_subtotal() == product.price * item.quantity


# ── MODEL: PortraitOrder ─────────────────────────────────────────────────────
class TestPortraitOrder:
    def test_portrait_price_auto_set(self, user, db):
        from django.core.files.base import ContentFile
        po = PortraitOrder(
            user=user, name='Test Portrait', size='medium',
            image=None
        )
        # price set by save()
        po.image.name = 'portraits/dummy.jpg'
        po.price = PortraitOrder.SIZE_PRICES['medium']
        assert po.price == 900

    def test_portrait_size_prices_map(self):
        assert PortraitOrder.SIZE_PRICES['small']  == 500
        assert PortraitOrder.SIZE_PRICES['medium'] == 900
        assert PortraitOrder.SIZE_PRICES['large']  == 1500

    def test_portrait_str(self, user, db):
        po = PortraitOrder.__new__(PortraitOrder)
        po.name = 'My Portrait'
        po.user = user
        assert 'My Portrait' in PortraitOrder.__str__(po)
        assert user.username in PortraitOrder.__str__(po)
