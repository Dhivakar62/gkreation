"""
Reset superuser with verified correct password hash.
Deletes and recreates to ensure clean state regardless of previous migrations.
Password: Admin13579
"""
from django.db import migrations


def reset_superuser(apps, schema_editor):
    from django.contrib.auth.models import User
    # Delete any existing admin user and recreate cleanly
    User.objects.filter(username='admin').delete()
    User.objects.create(
        username='admin',
        email='admin@gkreations.com',
        first_name='Admin',
        last_name='GKreations',
        is_staff=True,
        is_superuser=True,
        is_active=True,
        password='pbkdf2_sha256$600000$215ZC71ZDlgjd28hGdDmT1$HzZNbiLd1XXyzs3pkm9IipKVS8wMtcczmVGR68ALVf4=',
    )


def reverse_migration(apps, schema_editor):
    from django.contrib.auth.models import User
    User.objects.filter(username='admin').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(reset_superuser, reverse_migration),
    ]
