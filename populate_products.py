"""
populate_products.py
Run this from inside your GKCREATIONS project folder:
    python populate_products.py

This will:
  1. Delete existing products
  2. Create 10 Frames + 10 Paintings with images
"""

import os
import sys
import django

# ── Django setup ──────────────────────────────────────────────────────────────
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GKCREATIONS.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.core.files import File
from core.models import Product

MEDIA_DIR = os.path.join(os.path.dirname(__file__), 'media', 'products')

# ── Product data ──────────────────────────────────────────────────────────────

FRAMES = [
    {
        'name': 'Vintage Oak Frame',
        'price': 1299,
        'size': '12×16 inch',
        'material': 'Oak Wood',
        'model_number': 'FR-001',
        'description': 'A beautiful vintage oak wood frame with a classic warm finish. Handcrafted with precision, this frame brings timeless elegance to any portrait or artwork. The natural grain of oak adds character and warmth to your treasured memories.',
        'image': 'frame_1.jpg',
    },
    {
        'name': 'Modern Black Frame',
        'price': 799,
        'size': '8×10 inch',
        'material': 'MDF + Matte Laminate',
        'model_number': 'FR-002',
        'description': 'Sleek and minimal, this modern matte black frame is perfect for contemporary art, photography, and certificates. Clean lines and a smooth finish make it a versatile choice for any interior style.',
        'image': 'frame_2.jpg',
    },
    {
        'name': 'Gold Ornate Frame',
        'price': 2499,
        'size': '18×24 inch',
        'material': 'Resin + Gold Finish',
        'model_number': 'FR-003',
        'description': 'Luxurious gold ornate frame with intricate detailing that adds grandeur and elegance to any masterpiece. Crafted from premium resin with a radiant gold finish, this frame transforms walls into gallery spaces.',
        'image': 'frame_3.jpg',
    },
    {
        'name': 'Rustic Barn Frame',
        'price': 1599,
        'size': '10×14 inch',
        'material': 'Reclaimed Wood',
        'model_number': 'FR-004',
        'description': 'Charming rustic frame made from authentic reclaimed barn wood. Each piece carries its own unique story, with natural imperfections that make it truly one-of-a-kind. Perfect for farmhouse and boho interiors.',
        'image': 'frame_4.jpg',
    },
    {
        'name': 'White Minimalist Frame',
        'price': 699,
        'size': '6×8 inch',
        'material': 'Solid Wood + White Paint',
        'model_number': 'FR-005',
        'description': 'Clean, crisp white frame that lets your artwork speak for itself. Ideal for Scandinavian and minimalist décor. The smooth white finish brightens any room and gives a gallery-wall feel to your space.',
        'image': 'frame_5.jpg',
    },
    {
        'name': 'Antique Silver Frame',
        'price': 1899,
        'size': '14×18 inch',
        'material': 'Zinc Alloy + Silver Plating',
        'model_number': 'FR-006',
        'description': 'Elegant antique silver frame with subtle distressing that evokes classic European craftsmanship. Its soft silver tones complement both black-and-white photography and colourful paintings beautifully.',
        'image': 'frame_6.jpg',
    },
    {
        'name': 'Cherry Wood Frame',
        'price': 1799,
        'size': '11×14 inch',
        'material': 'Cherry Wood',
        'model_number': 'FR-007',
        'description': 'Rich, warm cherry wood frame with a deep reddish-brown hue that matures beautifully over time. A classic choice for formal portraits, diplomas, and fine art. Comes with UV-protective glass.',
        'image': 'frame_7.jpg',
    },
    {
        'name': 'Walnut Luxury Frame',
        'price': 2999,
        'size': '16×20 inch',
        'material': 'American Black Walnut',
        'model_number': 'FR-008',
        'description': 'Premium American black walnut frame radiating sophistication and natural beauty. The dark, chocolatey tones with fine grain make it ideal for upscale home offices, living rooms, and galleries.',
        'image': 'frame_8.jpg',
    },
    {
        'name': 'Teak Art Frame',
        'price': 2199,
        'size': '13×19 inch',
        'material': 'Teak Wood',
        'model_number': 'FR-009',
        'description': 'Sturdy and stylish teak wood frame with a natural oil finish that enhances its golden-brown grain. Teak\'s natural oils make it resistant to warping, ensuring your frame lasts generations.',
        'image': 'frame_9.jpg',
    },
    {
        'name': 'Bamboo Eco Frame',
        'price': 899,
        'size': '8×12 inch',
        'material': 'Sustainable Bamboo',
        'model_number': 'FR-010',
        'description': 'Eco-friendly bamboo frame with a light, natural finish. Bamboo is stronger than most hardwoods and grows rapidly, making this frame a sustainable choice without compromising on style or durability.',
        'image': 'frame_10.jpg',
    },
]

PAINTINGS = [
    {
        'name': 'Sunset Over Mountains',
        'price': 4999,
        'size': '24×36 inch',
        'material': 'Acrylic on Canvas',
        'model_number': 'PT-001',
        'description': 'A vibrant, breathtaking depiction of golden hour cascading over misty mountain peaks. Hand-painted with premium acrylic colors, this piece captures the awe and serenity of nature at its most magnificent. A statement piece for any living room.',
        'image': 'painting_1.jpg',
    },
    {
        'name': 'Ocean Serenity',
        'price': 3799,
        'size': '20×30 inch',
        'material': 'Oil on Canvas',
        'model_number': 'PT-002',
        'description': 'Tranquil seascape capturing the calmness of ocean waves at dusk. Painted in rich oil colours with masterful brushwork, this piece brings the soothing energy of the sea into your home. Perfect for bedrooms and meditation spaces.',
        'image': 'painting_2.jpg',
    },
    {
        'name': 'Abstract Bloom',
        'price': 2999,
        'size': '16×20 inch',
        'material': 'Watercolour on Paper',
        'model_number': 'PT-003',
        'description': 'Contemporary abstract floral composition bursting with vibrant watercolours. Free-flowing brushstrokes and bold colour choices create a dynamic, joyful energy. A perfect accent for modern and eclectic interiors.',
        'image': 'painting_3.jpg',
    },
    {
        'name': 'Village Life',
        'price': 5499,
        'size': '30×40 inch',
        'material': 'Oil on Canvas',
        'model_number': 'PT-004',
        'description': 'A nostalgic, warmly rendered portrayal of rural village life with vivid detail and earthy tones. Lush fields, cosy cottages, and village paths come alive in this heartfelt oil painting that celebrates the simplicity of country living.',
        'image': 'painting_4.jpg',
    },
    {
        'name': 'Golden Harvest',
        'price': 3299,
        'size': '18×24 inch',
        'material': 'Acrylic on Canvas',
        'model_number': 'PT-005',
        'description': 'Sun-drenched golden wheat fields stretching to the horizon under a vast, glowing sky. This piece radiates warmth, abundance, and optimism. Its rich amber and gold palette makes it a stunning focal point in dining rooms and kitchens.',
        'image': 'painting_5.jpg',
    },
    {
        'name': 'Mystic Forest',
        'price': 4299,
        'size': '22×32 inch',
        'material': 'Oil on Canvas',
        'model_number': 'PT-006',
        'description': 'An enchanting forest at twilight, where shafts of soft light pierce through a canopy of ancient trees. Deep greens and mysterious shadows create a sense of wonder and calm. Ideal for nature lovers and dreamers.',
        'image': 'painting_6.jpg',
    },
    {
        'name': 'Floral Symphony',
        'price': 2599,
        'size': '14×18 inch',
        'material': 'Acrylic on Canvas',
        'model_number': 'PT-007',
        'description': 'A joyful celebration of flowers in full bloom — roses, lotuses, and wildflowers dance across the canvas in vivid pinks, oranges, and greens. This cheerful painting brings life and colour to any space it graces.',
        'image': 'painting_7.jpg',
    },
    {
        'name': 'Riverside Calm',
        'price': 3599,
        'size': '20×28 inch',
        'material': 'Watercolour on Canvas',
        'model_number': 'PT-008',
        'description': 'A peaceful river winding through lush green valleys, reflecting the soft blues of the sky. Painted in delicate watercolour washes, this serene landscape evokes a sense of quietude and harmony with nature.',
        'image': 'painting_8.jpg',
    },
    {
        'name': 'Abstract Emotions',
        'price': 3999,
        'size': '24×24 inch',
        'material': 'Mixed Media on Canvas',
        'model_number': 'PT-009',
        'description': 'Bold, expressive abstract art that channels raw emotion through colour, texture, and form. Deep purples, electric blues, and passionate magentas collide and harmonise in a composition that speaks differently to every viewer.',
        'image': 'painting_9.jpg',
    },
    {
        'name': 'Portrait of Grace',
        'price': 6999,
        'size': '20×28 inch',
        'material': 'Oil on Canvas',
        'model_number': 'PT-010',
        'description': 'A timeless, elegant portrait painted in the classical tradition. Soft, luminous skin tones and expressive eyes make this a deeply moving work of art. A collector\'s piece that becomes a cherished heirloom for generations.',
        'image': 'painting_10.jpg',
    },
]

# ── Populate database ─────────────────────────────────────────────────────────

def run():
    print("=" * 55)
    print("  GKreation's - Product Population Script")
    print("=" * 55)

    # Clear existing products
    deleted = Product.objects.all().delete()
    print(f"\n🗑  Cleared existing products.")

    created_frames = 0
    created_paintings = 0
    errors = []

    print("\n📦 Creating Frames...")
    for data in FRAMES:
        img_path = os.path.join(MEDIA_DIR, data['image'])
        if not os.path.exists(img_path):
            errors.append(f"  ✗ Image not found: {img_path}")
            continue
        try:
            product = Product(
                name=data['name'],
                category='frames',
                price=data['price'],
                size=data['size'],
                material=data['material'],
                model_number=data['model_number'],
                description=data['description'],
                stock=15,
                is_active=True,
            )
            with open(img_path, 'rb') as f:
                product.image.save(data['image'], File(f), save=True)
            print(f"  ✓ {data['name']} — ₹{data['price']}")
            created_frames += 1
        except Exception as e:
            errors.append(f"  ✗ {data['name']}: {e}")

    print("\n🎨 Creating Paintings...")
    for data in PAINTINGS:
        img_path = os.path.join(MEDIA_DIR, data['image'])
        if not os.path.exists(img_path):
            errors.append(f"  ✗ Image not found: {img_path}")
            continue
        try:
            product = Product(
                name=data['name'],
                category='paintings',
                price=data['price'],
                size=data['size'],
                material=data['material'],
                model_number=data['model_number'],
                description=data['description'],
                stock=10,
                is_active=True,
            )
            with open(img_path, 'rb') as f:
                product.image.save(data['image'], File(f), save=True)
            print(f"  ✓ {data['name']} — ₹{data['price']}")
            created_paintings += 1
        except Exception as e:
            errors.append(f"  ✗ {data['name']}: {e}")

    print("\n" + "=" * 55)
    print(f"  ✅ Frames created:   {created_frames}/10")
    print(f"  ✅ Paintings created: {created_paintings}/10")
    print(f"  📦 Total products:   {Product.objects.count()}")
    if errors:
        print("\n  ⚠ Errors:")
        for e in errors:
            print(e)
    print("=" * 55)
    print("\n  Visit http://127.0.0.1:8000 to see your products!")
    print("=" * 55)

if __name__ == '__main__':
    run()
