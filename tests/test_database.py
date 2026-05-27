"""
PHASE 2 — Database Integrity Tests
"""
import pytest
from decimal import Decimal
from django.contrib.auth.models import User
from core.models import Product, Cart, CartItem, Order, OrderItem


@pytest.fixture
def user(db):
    return User.objects.create_user(username='dbuser', password='DBPass@123')


@pytest.fixture
def product(db):
    return Product.objects.create(
        name='DB Test Frame', category='frames', price=Decimal('500.00'),
        size='5x7', material='MDF', description='DB test', stock=5
    )


class TestDatabaseIntegrity:
    def test_cart_one_per_user(self, user):
        Cart.objects.create(user=user)
        with pytest.raises(Exception):
            Cart.objects.create(user=user)  # OneToOne constraint

    def test_product_price_precision(self, db):
        p = Product.objects.create(
            name='Precision Test', category='frames', price=Decimal('1234.56'),
            size='5x7', material='Wood', description='Test', stock=5
        )
        p.refresh_from_db()
        assert p.price == Decimal('1234.56')

    def test_order_total_amount_precision(self, user, db):
        o = Order.objects.create(
            user=user, total_amount=Decimal('9999.99'),
            address_line1='A', city='B', state='C', pincode='D', phone='E'
        )
        o.refresh_from_db()
        assert o.total_amount == Decimal('9999.99')

    def test_deleting_user_deletes_cart(self, user, product):
        cart = Cart.objects.create(user=user)
        CartItem.objects.create(cart=cart, product=product, quantity=1)
        user_id = user.id
        user.delete()
        assert not Cart.objects.filter(user_id=user_id).exists()
        assert not CartItem.objects.filter(cart__user_id=user_id).exists()

    def test_product_model_number_optional(self, db):
        p = Product.objects.create(
            name='No Model No', category='paintings', price=200,
            size='10x12', material='Canvas', description='Test', model_number=''
        )
        assert p.model_number == ''

    def test_product_is_active_default_true(self, db):
        p = Product.objects.create(
            name='Active Test', category='frames', price=100,
            size='5x7', material='Wood', description='Test'
        )
        assert p.is_active is True

    def test_order_created_at_auto(self, user, db):
        o = Order.objects.create(
            user=user, total_amount=100,
            address_line1='A', city='B', state='C', pincode='D', phone='E'
        )
        assert o.created_at is not None

    def test_frames_products_exist_in_db(self, db):
        count = Product.objects.filter(category='frames', is_active=True).count()
        assert count > 0, "No frame products in DB!"

    def test_paintings_products_exist_in_db(self, db):
        count = Product.objects.filter(category='paintings', is_active=True).count()
        assert count > 0, "No painting products in DB!"

    def test_product_stock_non_negative(self, db):
        products = Product.objects.all()
        for p in products:
            assert p.stock >= 0, f"Product {p.name} has negative stock!"

    def test_order_item_references_valid_product(self, user, product, db):
        o = Order.objects.create(
            user=user, total_amount=500,
            address_line1='A', city='B', state='C', pincode='D', phone='E'
        )
        oi = OrderItem.objects.create(order=o, product=product, quantity=1, price=product.price)
        oi.refresh_from_db()
        assert oi.product == product

    def test_duplicate_username_blocked(self, user, db):
        with pytest.raises(Exception):
            User.objects.create_user(username='dbuser', password='AnotherPass@1')
