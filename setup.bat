@echo off
REM ============================================================
REM  GK Creations — Windows Setup Script
REM  Run this from inside the GKCREATIONS folder
REM  Double-click or run:  setup.bat
REM ============================================================

echo.
echo ============================================================
echo   GK Creations — Full Setup (Windows)
echo ============================================================

REM 1. Create virtual environment
echo.
echo [1/5] Creating virtual environment...
python -m venv env
call env\Scripts\activate

REM 2. Install dependencies
echo.
echo [2/5] Installing dependencies...
pip install -r requirements.txt --quiet

REM 3. Migrations
echo.
echo [3/5] Running migrations...
python manage.py migrate

REM 4. Create superuser silently
echo.
echo [4/5] Creating admin user...
python -c "from django.contrib.auth.models import User; import django; import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE','GKCREATIONS.settings'); django.setup(); User.objects.create_superuser('admin','admin@gkcreations.com','admin123') if not User.objects.filter(username='admin').exists() else print('Admin already exists')" 2>nul || python manage.py shell -c "from django.contrib.auth.models import User; User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin','admin@gkcreations.com','admin123')"

REM 5. Sample products
echo.
echo [5/5] Creating sample products with images...
python setup_products.py

echo.
echo ============================================================
echo   SETUP COMPLETE!
echo ============================================================
echo.
echo   IMPORTANT: Add your Razorpay API keys first!
echo   Open: GKCREATIONS\settings.py
echo   Set:  RAZORPAY_KEY_ID     = 'rzp_test_...'
echo         RAZORPAY_KEY_SECRET = 'your_secret'
echo.
echo   Get keys from: https://dashboard.razorpay.com
echo   Settings ^> API Keys ^> Generate Test Key
echo.
echo   Admin login: admin / admin123
echo   Site:  http://127.0.0.1:8000
echo   Admin: http://127.0.0.1:8000/admin
echo.
echo   To start: python manage.py runserver
echo ============================================================
pause
