# GKreation's – Production Deployment Report
Generated: May 2026 | Target: Render.com

---

## ✅ Issues Fixed

| # | Issue | Fix Applied |
|---|-------|-------------|
| 1 | `SECRET_KEY` hardcoded in settings.py | Moved to `.env` via `python-decouple` |
| 2 | `RAZORPAY_KEY_ID/SECRET` hardcoded | Moved to `.env` / Render env vars |
| 3 | `DEBUG=True` in production | `DEBUG=False` via env var |
| 4 | No WhiteNoise for static files | Added `whitenoise.middleware.WhiteNoiseMiddleware` |
| 5 | No `gunicorn` (dev server only) | Added `gunicorn==26.0.0` |
| 6 | `STATIC_ROOT` not collected | `collectstatic` now runs in `build.sh` |
| 7 | No production security headers | HSTS, SSL redirect, CSRF/session secure cookies |
| 8 | No Procfile / build script | Created `Procfile` and `build.sh` |
| 9 | No `.gitignore` | Created with env, venv, staticfiles, db exclusions |
| 10 | No database flexibility | `dj-database-url` supports SQLite → PostgreSQL |
| 11 | No `render.yaml` | Created with full service config |
| 12 | No `runtime.txt` | `python-3.12.3` specified |
| 13 | Static dir was empty | Added `static/css/custom.css`, `static/js/custom.js` |
| 14 | `check --deploy` issues | All 0 issues after fixes |

---

## 📁 Updated Files

```
gkcreations_prod/
├── .env                    ← LOCAL ONLY (never commit!)
├── .env.example            ← Safe template to commit
├── .gitignore              ← NEW: excludes secrets, venv, staticfiles
├── GKCREATIONS/
│   ├── settings.py         ← REWRITTEN: decouple, WhiteNoise, security
│   ├── urls.py             ← UPDATED: cleaner media handling
│   └── wsgi.py             ← unchanged
├── Procfile                ← NEW: gunicorn start command
├── build.sh                ← NEW: Render build script
├── render.yaml             ← NEW: Render IaC config
├── requirements.txt        ← UPDATED: gunicorn, whitenoise, decouple, psycopg2
├── runtime.txt             ← NEW: python-3.12.3
└── static/
    ├── css/custom.css      ← NEW
    └── js/custom.js        ← NEW
```

---

## 🚀 Step-by-Step: Push to GitHub

```bash
# 1. Create a new repository on github.com (name: gkcreations)
#    Do NOT initialize with README

# 2. Add remote and push
git remote add origin https://github.com/YOUR_USERNAME/gkcreations.git
git push -u origin main
```

---

## 🌐 Deploy on Render

### Option A — Auto Deploy via render.yaml (recommended)
1. Go to https://dashboard.render.com → **New → Blueprint**
2. Connect your GitHub repo
3. Render reads `render.yaml` automatically
4. Fill in the 2 secret env vars (Razorpay keys) in the dashboard

### Option B — Manual Web Service
1. Go to https://dashboard.render.com → **New → Web Service**
2. Connect GitHub repo
3. Fill in:

| Field | Value |
|-------|-------|
| **Runtime** | Python 3 |
| **Build Command** | `./build.sh` |
| **Start Command** | `gunicorn GKCREATIONS.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120` |
| **Plan** | Free |

---

## 🔐 Environment Variables (set in Render Dashboard)

| Variable | Value | Notes |
|----------|-------|-------|
| `SECRET_KEY` | *(auto-generate or paste a 50-char random string)* | Critical – never share |
| `DEBUG` | `False` | Must be False in production |
| `ALLOWED_HOSTS` | `.onrender.com` | Render subdomain wildcard |
| `RAZORPAY_KEY_ID` | `rzp_test_SmkYXw3c83elpF` | Replace with live key for prod |
| `RAZORPAY_KEY_SECRET` | `5Tm4kflcilM1Op0sjyoMmAEu` | Replace with live key for prod |
| `PYTHON_VERSION` | `3.12.3` | Optional but explicit |

> ⚠️ **For live payments**, switch `rzp_test_*` keys to `rzp_live_*` keys from your Razorpay dashboard.

---

## 💳 Razorpay in Production — Checklist

- [ ] Activate your Razorpay account (KYC complete)
- [ ] Get live keys from: https://dashboard.razorpay.com → Settings → API Keys
- [ ] Set `RAZORPAY_KEY_ID` and `RAZORPAY_KEY_SECRET` to live keys in Render
- [ ] Set your Render domain in Razorpay Webhooks (optional but recommended):
      `https://your-app.onrender.com/razorpay/callback/`
- [ ] Test a full payment flow after deployment

---

## 🖼️ Media Files Warning (Important!)

Render's **free tier uses an ephemeral filesystem** — uploaded files (product images) 
are deleted on every redeploy.

**For production with persistent media, add Cloudinary:**

```bash
pip install cloudinary dj3-cloudinary-storage
```

Add to `requirements.txt`:
```
cloudinary==1.42.1
dj3-cloudinary-storage==0.0.6
```

Add to `.env`:
```
CLOUDINARY_URL=cloudinary://api_key:api_secret@cloud_name
```

Update `settings.py`:
```python
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
```

For now, run `python manage.py shell` → execute `populate_products.py` 
after first deploy to re-seed product images.

---

## 🧪 Post-Deploy Verification

```bash
# After deploy completes, test these URLs:
curl https://your-app.onrender.com/           # Home page
curl https://your-app.onrender.com/frames/    # Products
curl https://your-app.onrender.com/admin/     # Admin (create superuser first)

# Create superuser on Render shell:
python manage.py createsuperuser
```

---

## ⚙️ Django Checks Summary

```
python manage.py check          → System check identified no issues (0 silenced)
python manage.py check --deploy → System check identified no issues (0 silenced)
python manage.py makemigrations → No changes detected
python manage.py migrate        → No migrations to apply
python manage.py collectstatic  → 127 static files copied, 379 post-processed
```

---

## 📋 Remaining Manual Steps

1. **GitHub**: Create repo + `git remote add origin` + `git push`
2. **Render**: Connect repo, set env vars (especially Razorpay keys)
3. **Post-deploy**: Run `python manage.py createsuperuser` via Render shell
4. **Post-deploy**: Run `populate_products.py` to seed product images
5. **Razorpay Live**: Switch to live keys when going live
6. **Media (optional)**: Set up Cloudinary for persistent image storage
