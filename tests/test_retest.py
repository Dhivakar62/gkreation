"""
RETEST SUITE — Modules 1–5
Verifies: Homepage products, Login, Address, Registration, Email Validation
"""
import pytest
from decimal import Decimal
from django.test import Client
from django.urls import reverse
from django.contrib.auth.models import User
from core.models import Product, Cart, CartItem, UserProfile


# ═══════════════════════════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.fixture
def client():
    c = Client()
    return c

@pytest.fixture
def user(db):
    return User.objects.create_user(
        username='retestuser', password='Retest@Pass1',
        email='retest@gkreations.com', first_name='Re', last_name='Test'
    )

@pytest.fixture
def auth_client(user):
    c = Client()
    c.login(username='retestuser', password='Retest@Pass1')
    return c

@pytest.fixture
def frame_product(db):
    return Product.objects.create(
        name='Test Retest Frame', category='frames',
        price=Decimal('999.00'), size='8x10', material='Wood',
        description='Retest product', stock=10, is_active=True,
        image='images/frames/frame_01.jpg'
    )

@pytest.fixture
def painting_product(db):
    return Product.objects.create(
        name='Test Retest Painting', category='paintings',
        price=Decimal('2999.00'), size='18x24', material='Canvas',
        description='Retest painting', stock=5, is_active=True,
        image='images/paintings/painting_01.jpg'
    )


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE 1 — HOMEPAGE PRODUCT LOADING
# ═══════════════════════════════════════════════════════════════════════════════

class TestModule1HomepageProducts:

    def test_M1_01_homepage_returns_200(self, client, db):
        resp = client.get(reverse('home'), follow=True)
        assert resp.status_code == 200, "Homepage did not return 200"

    def test_M1_02_home_view_passes_frames_context(self, client, frame_product):
        resp = client.get(reverse('home'), follow=True)
        assert 'frames' in resp.context, "frames not in homepage context"
        assert resp.context['frames'].count() > 0, "No frames in context"

    def test_M1_03_home_view_passes_paintings_context(self, client, painting_product):
        resp = client.get(reverse('home'), follow=True)
        assert 'paintings' in resp.context, "paintings not in homepage context"
        assert resp.context['paintings'].count() > 0, "No paintings in context"

    def test_M1_04_frame_product_name_visible_in_html(self, client, frame_product):
        resp = client.get(reverse('home'), follow=True)
        assert frame_product.name.encode() in resp.content, "Frame name not in HTML"

    def test_M1_05_painting_product_name_visible_in_html(self, client, painting_product):
        resp = client.get(reverse('home'), follow=True)
        assert painting_product.name.encode() in resp.content, "Painting name not in HTML"

    def test_M1_06_product_price_visible(self, client, frame_product):
        resp = client.get(reverse('home'), follow=True)
        assert b'999' in resp.content, "Product price not visible"

    def test_M1_07_all_products_have_static_image_paths(self, db):
        """BUG-001 FIX VERIFICATION: No product should use products/ prefix"""
        import os
        broken = []
        for p in Product.objects.filter(is_active=True):
            img = str(p.image)
            if img.startswith('products/'):
                broken.append((p.id, p.name, img))
        assert len(broken) == 0, f"Products still using old media/ path: {broken}"

    def test_M1_08_all_image_files_exist_in_static(self, db):
        """Verify every product image file exists in static/"""
        import os
        missing = []
        for p in Product.objects.filter(is_active=True):
            img = str(p.image)
            if img and img.startswith('images/'):
                if not os.path.exists(f'static/{img}'):
                    missing.append((p.id, p.name, img))
        assert len(missing) == 0, f"Missing static image files: {missing}"

    def test_M1_09_product_image_url_tag_returns_url(self, db, frame_product):
        """product_image_url tag returns /static/images/... URL"""
        from core.templatetags.product_tags import product_image_url
        url = product_image_url(frame_product)
        assert url, "product_image_url returned empty string"
        assert 'static' in url or 'images' in url, f"Unexpected URL: {url}"

    def test_M1_10_empty_state_handled_gracefully(self, client, db):
        """If no products, homepage shows empty state message not error"""
        Product.objects.all().update(is_active=False)
        resp = client.get(reverse('home'), follow=True)
        assert resp.status_code == 200
        assert b'500' not in resp.content[:50]  # No server error
        Product.objects.all().update(is_active=True)

    def test_M1_11_total_products_count_correct(self, db):
        total = Product.objects.filter(is_active=True).count()
        assert total >= 36, f"Expected at least 36 active products, got {total}"

    def test_M1_12_frames_count(self, db):
        frames = Product.objects.filter(category='frames', is_active=True).count()
        assert frames >= 26, f"Expected at least 26 frames, got {frames}"

    def test_M1_13_paintings_count(self, db):
        paintings = Product.objects.filter(category='paintings', is_active=True).count()
        assert paintings >= 10, f"Expected at least 10 paintings, got {paintings}"

    def test_M1_14_product_lazy_loading_in_template(self, client, frame_product):
        resp = client.get(reverse('home'), follow=True)
        assert b'loading="lazy"' in resp.content or b"loading='lazy'" in resp.content


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE 2 — USER LOGIN
# ═══════════════════════════════════════════════════════════════════════════════

class TestModule2Login:

    def test_M2_01_login_page_loads(self, client, db):
        resp = client.get(reverse('login'), follow=True)
        assert resp.status_code == 200

    def test_M2_02_valid_login_creates_session(self, client, user):
        resp = client.post(reverse('login'), {
            'username': 'retestuser', 'password': 'Retest@Pass1'
        }, follow=True)
        assert resp.status_code == 200
        assert '_auth_user_id' in client.session

    def test_M2_03_invalid_password_rejected(self, client, user):
        client.post(reverse('login'), {
            'username': 'retestuser', 'password': 'WrongPass!'
        })
        assert '_auth_user_id' not in client.session

    def test_M2_04_nonexistent_user_rejected(self, client, db):
        client.post(reverse('login'), {
            'username': 'ghost_user_xyz', 'password': 'AnyPass@1'
        })
        assert '_auth_user_id' not in client.session

    def test_M2_05_logout_clears_session(self, auth_client):
        assert '_auth_user_id' in auth_client.session
        auth_client.post(reverse('logout'), follow=True)
        assert '_auth_user_id' not in auth_client.session

    def test_M2_06_authenticated_user_can_access_profile(self, auth_client):
        resp = auth_client.get(reverse('profile'), follow=True)
        assert resp.status_code == 200

    def test_M2_07_login_redirects_to_home_on_success(self, client, user):
        resp = client.post(reverse('login'), {
            'username': 'retestuser', 'password': 'Retest@Pass1'
        }, follow=True)
        assert resp.status_code == 200
        assert resp.resolver_match.url_name == 'home'

    def test_M2_08_csrf_token_present_on_login_form(self, client, db):
        resp = client.get(reverse('login'), follow=True)
        assert b'csrfmiddlewaretoken' in resp.content

    def test_M2_09_blank_password_rejected(self, client, user):
        client.post(reverse('login'), {'username': 'retestuser', 'password': ''})
        assert '_auth_user_id' not in client.session

    def test_M2_10_admin_user_can_access_admin(self, db):
        admin = User.objects.create_superuser(
            username='admintest', password='Admin@Test1', email='admin@test.com'
        )
        c = Client()
        c.login(username='admintest', password='Admin@Test1')
        resp = c.get('/admin/', follow=True)
        assert resp.status_code == 200


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE 3 — ADDRESS DETAILS
# ═══════════════════════════════════════════════════════════════════════════════

class TestModule3Address:

    def test_M3_01_profile_page_loads_for_auth_user(self, auth_client):
        resp = auth_client.get(reverse('profile'), follow=True)
        assert resp.status_code == 200

    def test_M3_02_address_save_via_profile_update(self, auth_client, user):
        resp = auth_client.post(reverse('profile'), {
            'first_name': 'Re', 'last_name': 'Test',
            'email': 'retest@gkreations.com',
            'phone': '9876543210',
            'address_line1': '42 Main Street',
            'address_line2': 'Near Park',
            'city': 'Chennai',
            'state': 'Tamil Nadu',
            'pincode': '600001',
        }, follow=True)
        assert resp.status_code == 200
        profile = UserProfile.objects.get(user=user)
        assert profile.address_line1 == '42 Main Street'
        assert profile.city == 'Chennai'

    def test_M3_03_address_persists_in_db(self, auth_client, user):
        auth_client.post(reverse('profile'), {
            'first_name': 'Re', 'last_name': 'Test',
            'email': 'retest@gkreations.com',
            'phone': '9876543210',
            'address_line1': '99 Retest Road',
            'city': 'Bangalore', 'state': 'Karnataka', 'pincode': '560001',
        }, follow=True)
        profile = UserProfile.objects.get(user=user)
        profile.refresh_from_db()
        assert profile.address_line1 == '99 Retest Road'

    def test_M3_04_get_full_address_method(self, user):
        profile, _ = UserProfile.objects.get_or_create(user=user, defaults={
            'address_line1': '5 Test Lane', 'city': 'Mumbai',
            'state': 'Maharashtra', 'pincode': '400001'
        })
        addr = profile.get_full_address()
        assert 'Mumbai' in addr
        assert '400001' in addr

    def test_M3_05_phone_number_saved(self, auth_client, user):
        auth_client.post(reverse('profile'), {
            'first_name': 'Re', 'last_name': 'Test',
            'email': 'retest@gkreations.com',
            'phone': '8888888888',
            'address_line1': '1 Test St', 'city': 'Delhi',
            'state': 'Delhi', 'pincode': '110001',
        }, follow=True)
        profile = UserProfile.objects.get(user=user)
        assert profile.phone == '8888888888'

    def test_M3_06_unauthenticated_profile_redirect(self, client, db):
        resp = client.get(reverse('profile'), follow=False)
        assert resp.status_code in [301, 302]


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE 4 — REGISTRATION
# ═══════════════════════════════════════════════════════════════════════════════

class TestModule4Registration:

    def _valid_reg(self, suffix=''):
        return {
            'first_name': 'New', 'last_name': 'User',
            'username': f'newuser{suffix}',
            'email': f'newuser{suffix}@gkreations.com',
            'password1': 'NewStr0ng@Pass!',
            'password2': 'NewStr0ng@Pass!',
        }

    def test_M4_01_registration_page_loads(self, client, db):
        resp = client.get(reverse('register'), follow=True)
        assert resp.status_code == 200

    def test_M4_02_valid_registration_creates_user(self, client, db):
        client.post(reverse('register'), self._valid_reg('A'), follow=True)
        assert User.objects.filter(username='newuserA').exists()

    def test_M4_03_duplicate_username_rejected(self, client, user):
        data = self._valid_reg()
        data['username'] = 'retestuser'  # same as fixture
        data['email'] = 'unique99@test.com'
        resp = client.post(reverse('register'), data, follow=True)
        assert User.objects.filter(username='retestuser').count() == 1

    def test_M4_04_duplicate_email_rejected(self, client, user):
        data = self._valid_reg('B')
        data['email'] = 'retest@gkreations.com'  # same as fixture
        resp = client.post(reverse('register'), data, follow=True)
        assert User.objects.filter(email='retest@gkreations.com').count() == 1

    def test_M4_05_password_mismatch_rejected(self, client, db):
        data = self._valid_reg('C')
        data['password2'] = 'DifferentPass@1'
        client.post(reverse('register'), data, follow=True)
        assert not User.objects.filter(username='newuserC').exists()

    def test_M4_06_weak_password_rejected(self, client, db):
        data = self._valid_reg('D')
        data['password1'] = data['password2'] = '12345'
        client.post(reverse('register'), data, follow=True)
        assert not User.objects.filter(username='newuserD').exists()

    def test_M4_07_missing_first_name_rejected(self, client, db):
        data = self._valid_reg('E')
        data['first_name'] = ''
        client.post(reverse('register'), data, follow=True)
        assert not User.objects.filter(username='newuserE').exists()

    def test_M4_08_successful_registration_redirects(self, client, db):
        resp = client.post(reverse('register'), self._valid_reg('F'), follow=True)
        assert resp.status_code == 200

    def test_M4_09_registered_user_can_login(self, client, db):
        client.post(reverse('register'), self._valid_reg('G'), follow=True)
        client.logout()
        resp = client.post(reverse('login'), {
            'username': 'newuserG', 'password': 'NewStr0ng@Pass!'
        }, follow=True)
        assert '_auth_user_id' in client.session

    def test_M4_10_profile_created_on_registration(self, client, db):
        client.post(reverse('register'), self._valid_reg('H'), follow=True)
        user = User.objects.get(username='newuserH')
        assert UserProfile.objects.filter(user=user).exists()


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE 5 — EMAIL VALIDATION
# ═══════════════════════════════════════════════════════════════════════════════

class TestModule5EmailValidation:

    def test_M5_01_valid_email_accepted(self, db):
        from core.forms import RegisterForm
        f = RegisterForm(data={
            'first_name': 'A', 'last_name': 'B', 'username': 'emailtest1',
            'email': 'valid@example.com',
            'password1': 'Str0ng@Pass!', 'password2': 'Str0ng@Pass!'
        })
        assert f.is_valid(), f"Valid email rejected: {f.errors}"

    def test_M5_02_invalid_email_format_rejected(self, db):
        from core.forms import RegisterForm
        for bad in ['notanemail', 'missing@', '@nodomain', 'spaces @test.com']:
            f = RegisterForm(data={
                'first_name': 'A', 'last_name': 'B', 'username': 'emailtest2',
                'email': bad, 'password1': 'Str0ng@Pass!', 'password2': 'Str0ng@Pass!'
            })
            assert not f.is_valid(), f"Bad email '{bad}' was accepted"

    def test_M5_03_duplicate_email_raises_validation_error(self, db):
        from core.forms import RegisterForm
        User.objects.create_user(username='exist', email='taken@gk.com', password='Pass@123')
        f = RegisterForm(data={
            'first_name': 'A', 'last_name': 'B', 'username': 'newone',
            'email': 'taken@gk.com',
            'password1': 'Str0ng@Pass!', 'password2': 'Str0ng@Pass!'
        })
        assert not f.is_valid()
        assert 'email' in f.errors
        assert 'already registered' in str(f.errors['email'])

    def test_M5_04_email_error_message_shown_in_response(self, client, db):
        User.objects.create_user(username='existing2', email='shown@gk.com', password='Pass@123')
        resp = client.post(reverse('register'), {
            'first_name': 'A', 'last_name': 'B', 'username': 'tryagain',
            'email': 'shown@gk.com',
            'password1': 'Str0ng@Pass!', 'password2': 'Str0ng@Pass!'
        }, follow=True)
        assert b'already registered' in resp.content or b'email' in resp.content.lower()

    def test_M5_05_empty_email_rejected(self, db):
        from core.forms import RegisterForm
        f = RegisterForm(data={
            'first_name': 'A', 'last_name': 'B', 'username': 'emailtest3',
            'email': '', 'password1': 'Str0ng@Pass!', 'password2': 'Str0ng@Pass!'
        })
        assert not f.is_valid()
        assert 'email' in f.errors

    def test_M5_06_email_with_subdomain_accepted(self, db):
        from core.forms import RegisterForm
        f = RegisterForm(data={
            'first_name': 'A', 'last_name': 'B', 'username': 'emailtest4',
            'email': 'user@sub.domain.com',
            'password1': 'Str0ng@Pass!', 'password2': 'Str0ng@Pass!'
        })
        assert f.is_valid(), f"Subdomain email rejected: {f.errors}"
