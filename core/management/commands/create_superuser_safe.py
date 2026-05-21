"""
Safe superuser creation via env vars.
Usage: python manage.py create_superuser_safe
Safe to run on every deploy — skips if superuser already exists.
"""
import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = 'Create superuser from ADMIN_USERNAME/EMAIL/PASSWORD env vars'

    def handle(self, *args, **kwargs):
        User = get_user_model()
        if User.objects.filter(is_superuser=True).exists():
            self.stdout.write(self.style.WARNING('Superuser already exists — skipping.'))
            return

        username = os.environ.get('ADMIN_USERNAME', 'admin')
        email    = os.environ.get('ADMIN_EMAIL', 'admin@gkreations.com')
        password = os.environ.get('ADMIN_PASSWORD', '')

        if not password:
            self.stdout.write(self.style.ERROR('Set ADMIN_PASSWORD env var to create superuser.'))
            return

        User.objects.create_superuser(username=username, email=email, password=password)
        self.stdout.write(self.style.SUCCESS(f'✅ Superuser "{username}" created.'))
