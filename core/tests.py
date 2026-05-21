from decimal import Decimal

from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.models import User
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory, TestCase
from django.urls import reverse

from . import views
from .models import Order, OrderItem, Product
from .views import home_view, order_detail_view


def attach_request_state(request, user):
    SessionMiddleware(lambda req: None).process_request(request)
    request.user = user
    request._messages = FallbackStorage(request)


class OrderBalanceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='buyer',
            password='testpass123',
        )

    def create_order(self, total='150.00', advance='75.00'):
        return Order.objects.create(
            user=self.user,
            total_amount=Decimal(total),
            advance_paid=Decimal(advance),
            payment_method='razorpay',
            payment_status='paid',
            status='confirmed',
            address_line1='12 Art Street',
            city='Kochi',
            state='Kerala',
            pincode='682001',
            phone='9876543210',
        )

    def test_balance_due_subtracts_paid_advance(self):
        order = self.create_order(total='150.00', advance='75.00')

        self.assertEqual(order.get_balance_due(), Decimal('75.00'))

    def test_balance_due_never_goes_negative_for_overpaid_order(self):
        order = self.create_order(total='100.00', advance='125.00')

        self.assertEqual(order.get_balance_due(), Decimal('0.00'))


class OrderDetailViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='buyer',
            password='testpass123',
        )
        self.product = Product.objects.create(
            name='QA Frame',
            category='frames',
            price=Decimal('150.00'),
            size='Medium',
            material='Wood',
            description='Regression test product',
        )

    def test_order_detail_renders_numeric_balance_due(self):
        order = Order.objects.create(
            user=self.user,
            total_amount=Decimal('150.00'),
            advance_paid=Decimal('75.00'),
            payment_method='razorpay',
            payment_status='paid',
            status='confirmed',
            address_line1='12 Art Street',
            city='Kochi',
            state='Kerala',
            pincode='682001',
            phone='9876543210',
        )
        OrderItem.objects.create(
            order=order,
            product=self.product,
            quantity=1,
            price=self.product.price,
        )
        request = self.factory.get(reverse('order_detail', args=[order.pk]))
        attach_request_state(request, self.user)

        response = order_detail_view(request, order.pk)

        self.assertEqual(response.status_code, 200)
        self.assertRegex(
            response.content.decode(),
            r'Balance Due</span>\s*<span class="fw-bold">[^<]*75\.00</span>',
        )


class AnonymousNavbarTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.product = Product.objects.create(
            name='Public QA Frame',
            category='frames',
            price=Decimal('999.00'),
            size='8x10 inch',
            material='Wood',
            description='Public route regression product',
        )

    def assert_guest_nav(self, response):
        content = response.content.decode()

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Login')
        self.assertContains(response, 'Register')
        self.assertNotIn('Logout', content)

    def anonymous_request(self, url_name, view_func, *args):
        request = self.factory.get(reverse(url_name, args=args))
        attach_request_state(request, AnonymousUser())
        return view_func(request, *args)

    def test_public_pages_show_login_register_not_logout_for_guest(self):
        public_pages = [
            ('home', views.home_view, ()),
            ('frames', views.frames_view, ()),
            ('paintings', views.paintings_view, ()),
            ('service_paintings', views.service_paintings_view, ()),
            ('about', views.about_view, ()),
            ('contact', views.contact_view, ()),
            ('login', views.login_view, ()),
            ('register', views.register_view, ()),
            ('product_detail', views.product_detail_view, (self.product.pk,)),
        ]

        for url_name, view_func, args in public_pages:
            with self.subTest(url_name=url_name):
                response = self.anonymous_request(url_name, view_func, *args)
                self.assert_guest_nav(response)

    def test_protected_pages_redirect_guest_to_login(self):
        protected_urls = [
            reverse('cart'),
            reverse('checkout'),
            reverse('order_list'),
            reverse('profile'),
            reverse('portrait'),
            reverse('wedding_event'),
            reverse('customize'),
        ]

        for url in protected_urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 302)
                self.assertIn(reverse('login'), response['Location'])

    def test_authenticated_home_nav_does_not_render_logout(self):
        user = User.objects.create_user(
            username='navbuyer',
            password='testpass123',
        )
        request = self.factory.get(reverse('home'))
        attach_request_state(request, user)

        response = home_view(request)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn('Logout', response.content.decode())
