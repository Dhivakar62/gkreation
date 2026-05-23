"""
Fix image paths for GK-NEW products to use static/images/ paths
served by WhiteNoise — permanent across Render redeploys.
"""
from django.db import migrations

def fix_paths(apps, schema_editor):
    Product = apps.get_model('core', 'Product')
    frame_paths = {f'GK-FR-NEW-{i:02d}': f'images/frames/frame_{i:02d}.jpg' for i in range(1, 14)}
    paint_paths = {f'GK-PT-NEW-{i:02d}': f'images/paintings/painting_{i:02d}.jpg' for i in range(1, 11)}
    fixed = 0
    for mn, path in {**frame_paths, **paint_paths}.items():
        fixed += Product.objects.filter(model_number=mn).update(image=path)
    print(f'  Fixed image paths for {fixed} products → static/images/...')

def reverse_fix(apps, schema_editor):
    Product = apps.get_model('core', 'Product')
    for i in range(1, 14):
        Product.objects.filter(model_number=f'GK-FR-NEW-{i:02d}').update(image='')
    for i in range(1, 11):
        Product.objects.filter(model_number=f'GK-PT-NEW-{i:02d}').update(image='')

class Migration(migrations.Migration):
    dependencies = [('core', '0006_seed_all_products')]
    operations = [migrations.RunPython(fix_paths, reverse_fix)]
