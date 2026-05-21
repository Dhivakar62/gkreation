#!/usr/bin/env bash
set -o errexit

echo "==> Installing dependencies..."
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

echo "==> Patching razorpay for Python 3.11+ (replacing pkg_resources with importlib.metadata)..."
RAZORPAY_CLIENT=$(python -c "import razorpay, os; print(os.path.join(os.path.dirname(razorpay.__file__), 'client.py'))")
echo "    Found razorpay client at: $RAZORPAY_CLIENT"

python << 'PYEOF'
import os, re

razorpay_path = os.path.join(
    os.path.dirname(__import__('razorpay').__file__), 'client.py'
)

with open(razorpay_path, 'r') as f:
    content = f.read()

# Replace pkg_resources imports with importlib.metadata
content = content.replace(
    "import pkg_resources\n\nfrom pkg_resources import DistributionNotFound",
    "from importlib.metadata import version as _pkg_version, PackageNotFoundError as DistributionNotFound"
)
content = content.replace(
    "import pkg_resources\nfrom pkg_resources import DistributionNotFound",
    "from importlib.metadata import version as _pkg_version, PackageNotFoundError as DistributionNotFound"
)

# Replace the version lookup call
content = content.replace(
    "version = pkg_resources.require(\"razorpay\")[0].version",
    "version = _pkg_version(\"razorpay\")"
)

with open(razorpay_path, 'w') as f:
    f.write(content)

print(f"    Patched: {razorpay_path}")
PYEOF

echo "==> Verifying razorpay import..."
python -c "import razorpay; print('    razorpay OK:', razorpay.__file__)"

echo "==> Collecting static files..."
python manage.py collectstatic --no-input

echo "==> Running migrations..."
python manage.py migrate --no-input

echo "==> Build complete!"
