"""
Update frame product image paths from media/products/ to static-served paths.
Since Render's filesystem is ephemeral, we use static/images/frames/ instead,
served reliably by WhiteNoise from git.
"""
from django.db import migrations


FRAME_STATIC_PATHS = {
    "Classic Multi-Photo Wall Set":      "images/frames/frame_01.jpg",
    "Family Portrait Wall Collage":       "images/frames/frame_02.jpg",
    "Baby Portrait Premium Frame":        "images/frames/frame_03.jpg",
    "Royal Gold Ornate Frame":            "images/frames/frame_04.jpg",
    "Classic Black Baroque Frame":        "images/frames/frame_05.jpg",
    "Black & Gold Luxury Frame Duo":      "images/frames/frame_06.jpg",
    "Handcrafted Wooden Carved Frame":    "images/frames/frame_07.jpg",
    "Mini Square Personal Frame":         "images/frames/frame_08.jpg",
    "Couple's Elegant Black Frame":       "images/frames/frame_09.jpg",
    "Gold Aluminium Slim Frame":          "images/frames/frame_10.jpg",
    "7-Photo Creative Wall Collage":      "images/frames/frame_11.jpg",
    "Black & White Memory Shadow Box":    "images/frames/frame_12.jpg",
    "7-Piece Family Heritage Frame Set":  "images/frames/frame_13.jpg",
}


def update_paths(apps, schema_editor):
    Product = apps.get_model('core', 'Product')
    for name, path in FRAME_STATIC_PATHS.items():
        Product.objects.filter(name=name).update(image=path)
    print(f"  Updated image paths for {len(FRAME_STATIC_PATHS)} frame products.")


def reverse_paths(apps, schema_editor):
    Product = apps.get_model('core', 'Product')
    for i, name in enumerate(FRAME_STATIC_PATHS.keys(), 1):
        Product.objects.filter(name=name).update(image=f"products/frame_{i:02d}.jpg")


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_seed_frame_products'),
    ]

    operations = [
        migrations.RunPython(update_paths, reverse_paths),
    ]
