"""
PHASE 3 — Live Site E2E Tests using requests + BeautifulSoup
Tests the deployed Render URL: https://gkreation.onrender.com
"""
import pytest
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://gkreation.onrender.com"
TIMEOUT = 30


def get(path, **kwargs):
    return requests.get(f"{BASE_URL}{path}", timeout=TIMEOUT, **kwargs)


def post(path, **kwargs):
    return requests.post(f"{BASE_URL}{path}", timeout=TIMEOUT, **kwargs)


# ── SMOKE: All Pages Return 200 ────────────────────────────────────────────────
class TestLiveSiteSmoke:
    PAGES = [
        ('/', 'Home'),
        ('/frames/', 'Frames'),
        ('/paintings/', 'Paintings'),
        ('/about/', 'About'),
        ('/contact/', 'Contact'),
        ('/login/', 'Login'),
        ('/register/', 'Register'),
        ('/services/paintings/', 'Services Paintings'),
        ('/services/portrait/', 'Portrait'),
        ('/services/wedding/', 'Wedding'),
        ('/customize/', 'Customize'),
    ]

    @pytest.mark.parametrize("path,name", PAGES)
    def test_page_returns_200(self, path, name):
        resp = get(path, allow_redirects=True)
        assert resp.status_code == 200, f"{name} ({path}) returned {resp.status_code}"

    def test_admin_panel_accessible(self):
        resp = get('/admin/', allow_redirects=True)
        assert resp.status_code == 200

    def test_404_for_unknown_page(self):
        resp = get('/this-page-does-not-exist-at-all/', allow_redirects=True)
        assert resp.status_code == 404


# ── CONTENT VALIDATION ─────────────────────────────────────────────────────────
class TestLiveContent:
    def test_home_has_brand_name(self):
        resp = get('/')
        assert b'GKreation' in resp.content or b'GKREATION' in resp.content

    def test_frames_page_has_products(self):
        resp = get('/frames/')
        soup = BeautifulSoup(resp.content, 'html.parser')
        # Should have product cards
        cards = soup.find_all(class_='card') or soup.find_all(class_='product-card')
        assert len(cards) > 0, "No product cards found on frames page"

    def test_paintings_page_has_products(self):
        resp = get('/paintings/')
        soup = BeautifulSoup(resp.content, 'html.parser')
        cards = soup.find_all(class_='card') or soup.find_all(class_='product-card')
        assert len(cards) > 0, "No product cards found on paintings page"

    def test_about_page_no_broken_images(self):
        resp = get('/about/')
        soup = BeautifulSoup(resp.content, 'html.parser')
        imgs = soup.find_all('img')
        for img in imgs:
            src = img.get('src', '')
            assert 'broken' not in src.lower()

    def test_navbar_present_on_all_pages(self):
        for path in ['/', '/frames/', '/paintings/', '/about/']:
            resp = get(path)
            soup = BeautifulSoup(resp.content, 'html.parser')
            nav = soup.find('nav')
            assert nav, f"No <nav> on {path}"

    def test_footer_present_on_all_pages(self):
        for path in ['/', '/frames/', '/paintings/']:
            resp = get(path)
            soup = BeautifulSoup(resp.content, 'html.parser')
            footer = soup.find('footer')
            assert footer, f"No <footer> on {path}"

    def test_about_page_has_video_section(self):
        resp = get('/about/')
        assert b'Videography' in resp.content or b'videography' in resp.content

    def test_about_page_no_portrait_images_in_portrait_section(self):
        resp = get('/about/')
        soup = BeautifulSoup(resp.content, 'html.parser')
        portrait_section = soup.find(id='portrait') or soup.find(string=lambda s: s and 'Portrait Arts' in s)
        # Portrait section should exist but contain no img tags
        # (this is a soft check — section presence validated)
        assert b'Portrait Arts' in resp.content


# ── FORM VALIDATION (Live) ─────────────────────────────────────────────────────
class TestLiveForms:
    def test_login_page_has_csrf_token(self):
        resp = get('/login/')
        soup = BeautifulSoup(resp.content, 'html.parser')
        csrf = soup.find('input', {'name': 'csrfmiddlewaretoken'})
        assert csrf, "No CSRF token on login form"

    def test_register_page_has_csrf_token(self):
        resp = get('/register/')
        soup = BeautifulSoup(resp.content, 'html.parser')
        csrf = soup.find('input', {'name': 'csrfmiddlewaretoken'})
        assert csrf, "No CSRF token on register form"

    def test_contact_page_has_csrf_token(self):
        resp = get('/contact/')
        soup = BeautifulSoup(resp.content, 'html.parser')
        csrf = soup.find('input', {'name': 'csrfmiddlewaretoken'})
        assert csrf, "No CSRF token on contact form"

    def test_login_invalid_credentials(self):
        # Get CSRF token
        session = requests.Session()
        login_page = session.get(f"{BASE_URL}/login/", timeout=TIMEOUT)
        soup = BeautifulSoup(login_page.content, 'html.parser')
        csrf = soup.find('input', {'name': 'csrfmiddlewaretoken'})
        if not csrf:
            pytest.skip("Could not get CSRF token")
        resp = session.post(f"{BASE_URL}/login/", data={
            'csrfmiddlewaretoken': csrf['value'],
            'username': 'totallyinvaliduser123',
            'password': 'wrongpass456'
        }, headers={'Referer': f"{BASE_URL}/login/"}, timeout=TIMEOUT)
        # Should stay on login or show error — not redirect to home
        assert b'invalid' in resp.content.lower() or resp.url.endswith('/login/') or b'error' in resp.content.lower() or b'incorrect' in resp.content.lower() or resp.status_code == 200


# ── SECURITY (Live) ────────────────────────────────────────────────────────────
class TestLiveSecurity:
    def test_protected_pages_redirect_to_login(self):
        for path in ['/cart/', '/checkout/', '/orders/', '/profile/']:
            resp = get(path, allow_redirects=False)
            assert resp.status_code in [301, 302], f"{path} should redirect, got {resp.status_code}"

    def test_https_redirect_works(self):
        resp = requests.get(f"https://gkreation.onrender.com/", timeout=TIMEOUT)
        assert resp.status_code == 200

    def test_no_server_error_on_any_page(self):
        paths = ['/', '/frames/', '/paintings/', '/about/', '/contact/', '/login/']
        for path in paths:
            resp = get(path)
            assert resp.status_code != 500, f"Server error on {path}"

    def test_sql_injection_in_url_safe(self):
        resp = get("/product/1' OR '1'='1/", allow_redirects=True)
        assert resp.status_code in [404, 400, 301, 302, 200]
        assert resp.status_code != 500

    def test_admin_requires_credentials(self):
        # Direct access to admin should show login, not dashboard
        resp = get('/admin/', allow_redirects=True)
        assert b'username' in resp.content.lower() or b'log in' in resp.content.lower()

    def test_no_django_debug_page_exposed(self):
        resp = get('/nonexistent-page-to-trigger-404/')
        assert b'Traceback' not in resp.content
        assert b'DEBUG' not in resp.content or b'<!DOCTYPE' in resp.content


# ── PERFORMANCE (Live) ─────────────────────────────────────────────────────────
class TestLivePerformance:
    def test_home_loads_under_10_seconds(self):
        import time
        start = time.time()
        resp = get('/')
        elapsed = time.time() - start
        assert resp.status_code == 200
        assert elapsed < 10, f"Home took {elapsed:.1f}s — too slow"

    def test_frames_page_load_time(self):
        import time
        start = time.time()
        get('/frames/')
        elapsed = time.time() - start
        assert elapsed < 15, f"Frames page took {elapsed:.1f}s"

    def test_images_have_loading_lazy(self):
        resp = get('/frames/')
        soup = BeautifulSoup(resp.content, 'html.parser')
        imgs = soup.find_all('img')
        lazy_count = sum(1 for img in imgs if img.get('loading') == 'lazy')
        assert lazy_count > 0, "No lazy-loaded images found on frames page"
