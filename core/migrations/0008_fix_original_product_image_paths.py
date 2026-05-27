"""
Migration 0008: Fix original product image paths.
Products seeded by populate_products.py used 'products/filename.jpg'
which maps to /media/products/ — ephemeral on Render (wiped on redeploy).

Fix: update paths to 'images/products/filename.jpg'
which maps to /static/images/products/ — committed to git, served by
WhiteNoise permanently across all deploys.

The product_image_url template tag already handles this:
  image starts with 'images/' → uses {% static %} → WhiteNoise serves it.
"""
from django.db import migrations


def fix_original_image_paths(apps, schema_editor):
    Product = apps.get_model('core', 'Product')
    updated = 0
    for product in Product.objects.filter(image__startswith='products/'):
        filename = str(product.image).replace('products/', '', 1)
        product.image = f'images/products/{filename}'
        product.save(update_fields=['image'])
        updated += 1
    print(f'  Updated {updated} product image paths: products/→images/products/')


def reverse_fix(apps, schema_editor):
    Product = apps.get_model('core', 'Product')
    for product in Product.objects.filter(image__startswith='images/products/'):
        filename = str(product.image).replace('images/products/', '', 1)
        product.image = f'products/{filename}'
        product.save(update_fields=['image'])


class Migration(migrations.Migration):
    dependencies = [('core', '0007_fix_product_image_paths')]
    operations = [migrations.RunPython(fix_original_image_paths, reverse_fix)]
