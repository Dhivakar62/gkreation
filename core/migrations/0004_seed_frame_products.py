"""
Seed 13 frame products with images, descriptions, sizes, materials and prices.
Images are stored in media/products/ — committed to git for initial seeding.
Safe to re-run: skips existing products by name.
"""
from django.db import migrations


FRAMES = [
    {
        "name": "Classic Multi-Photo Wall Set",
        "price": 1499,
        "size": "Mixed (4x6, 5x7, 8x10 inch)",
        "material": "Premium MDF Wood with Black Finish",
        "model_number": "GK-FR-001",
        "description": "A stunning 10-piece wall collage set featuring mixed-size black frames. Perfect for displaying travel memories, family portraits, and precious moments. Each frame includes a white mat for a gallery-quality finish.",
        "image": "products/frame_01.jpg",
        "stock": 15,
    },
    {
        "name": "Family Portrait Wall Collage",
        "price": 1299,
        "size": "Mixed (5x7, 8x10, 10x12 inch)",
        "material": "Solid Wood with Matte Black Finish",
        "model_number": "GK-FR-002",
        "description": "A beautiful 6-piece family collage frame set designed to display your most cherished family moments. The varying sizes create a dynamic, eye-catching wall display that tells your family's story.",
        "image": "products/frame_02.jpg",
        "stock": 12,
    },
    {
        "name": "Baby Portrait Premium Frame",
        "price": 799,
        "size": "8x10 inch",
        "material": "Dark Walnut Wood with Anti-Glare Glass",
        "model_number": "GK-FR-003",
        "description": "Capture your little one's precious moments in this elegant dark-finish portrait frame. Features high-clarity anti-glare glass to protect your photo from dust and UV damage. Ideal for nursery or living room.",
        "image": "products/frame_03.jpg",
        "stock": 20,
    },
    {
        "name": "Royal Gold Ornate Frame",
        "price": 1899,
        "size": "12x16 inch",
        "material": "Resin with 24K Gold Leaf Coating",
        "model_number": "GK-FR-004",
        "description": "An exquisite royal gold ornate frame with intricate floral detailing. Perfect for wedding portraits, certificates, or artwork. The timeless gold finish adds a touch of luxury to any space.",
        "image": "products/frame_04.jpg",
        "stock": 8,
    },
    {
        "name": "Classic Black Baroque Frame",
        "price": 1599,
        "size": "12x18 inch",
        "material": "High-Density Resin with Matte Black Finish",
        "model_number": "GK-FR-005",
        "description": "A dramatic black baroque-style frame with ornamental scrollwork detailing. Makes a bold statement in any room. Perfect for black & white photography, artwork, or vintage prints.",
        "image": "products/frame_05.jpg",
        "stock": 10,
    },
    {
        "name": "Black & Gold Luxury Frame Duo",
        "price": 2199,
        "size": "5x7 inch & 8x10 inch (Set of 2)",
        "material": "Lacquered Wood with Gold Leaf Trim",
        "model_number": "GK-FR-006",
        "description": "An elegant pair of frames combining rich black lacquer with gold-leaf inner trim. Perfect as a gift set or for displaying a couple's portrait alongside a group photo. Adds sophistication to any decor.",
        "image": "products/frame_06.jpg",
        "stock": 10,
    },
    {
        "name": "Handcrafted Wooden Carved Frame",
        "price": 2499,
        "size": "14x18 inch",
        "material": "Solid Mango Wood, Hand Carved",
        "model_number": "GK-FR-007",
        "description": "A one-of-a-kind hand-carved wooden frame with intricate floral and vine patterns. Made by skilled artisans from solid mango wood. Each piece is unique — a perfect blend of traditional craftsmanship and modern display.",
        "image": "products/frame_07.jpg",
        "stock": 6,
    },
    {
        "name": "Mini Square Personal Frame",
        "price": 399,
        "size": "4x4 inch",
        "material": "Lightweight MDF with White Gloss Finish",
        "model_number": "GK-FR-008",
        "description": "A compact and charming mini square frame, perfect for gifting or personal keepsakes. Lightweight and easy to carry. Great for desk display, selfies, or friendship portraits.",
        "image": "products/frame_08.jpg",
        "stock": 30,
    },
    {
        "name": "Couple's Elegant Black Frame",
        "price": 899,
        "size": "8x10 inch",
        "material": "Solid Wood with Satin Black Finish",
        "model_number": "GK-FR-009",
        "description": "A sleek, minimal black frame perfect for couple portraits, anniversary photos, or engagement pictures. The satin finish gives a modern, refined look. Includes tabletop stand and wall-hanging hardware.",
        "image": "products/frame_09.jpg",
        "stock": 18,
    },
    {
        "name": "Gold Aluminium Slim Frame",
        "price": 699,
        "size": "5x7 inch & 4x6 inch (Set of 2)",
        "material": "Brushed Aluminium with Gold Anodised Finish",
        "model_number": "GK-FR-010",
        "description": "Sleek, modern brushed-gold aluminium frames ideal for a minimalist aesthetic. The slim profile keeps focus on your photo. Perfect for home office, gifting, or contemporary home decor.",
        "image": "products/frame_10.jpg",
        "stock": 25,
    },
    {
        "name": "7-Photo Creative Wall Collage",
        "price": 1799,
        "size": "Mixed (4x6, 6x8 inch)",
        "material": "MDF with Black Gloss Finish",
        "model_number": "GK-FR-011",
        "description": "A creative 7-frame collage set designed for an asymmetric, artistic wall arrangement. Great for wedding photos, baby milestones, or travel memories. Comes with a template guide for easy wall placement.",
        "image": "products/frame_11.jpg",
        "stock": 12,
    },
    {
        "name": "Black & White Memory Shadow Box",
        "price": 999,
        "size": "10x12 inch",
        "material": "Deep MDF Shadow Box with Black Finish",
        "model_number": "GK-FR-012",
        "description": "A modern shadow box frame perfect for creating a collage of memories — black & white photos, polaroids, and mementos. The deep profile allows layered arrangement. Ideal as a friendship or farewell gift.",
        "image": "products/frame_12.jpg",
        "stock": 15,
    },
    {
        "name": "7-Piece Family Heritage Frame Set",
        "price": 2099,
        "size": "Mixed (4x6, 5x7, 8x10 inch)",
        "material": "Solid Wood with Walnut & Cream Finish",
        "model_number": "GK-FR-013",
        "description": "A premium 7-piece family wall frame set in warm walnut and cream tones. Designed to showcase multigenerational family portraits with elegance. Includes pre-arranged template for effortless display.",
        "image": "products/frame_13.jpg",
        "stock": 8,
    },
]


def seed_frames(apps, schema_editor):
    Product = apps.get_model('core', 'Product')
    created = 0
    for data in FRAMES:
        if not Product.objects.filter(name=data['name']).exists():
            Product.objects.create(
                category='frames',
                is_active=True,
                **data
            )
            created += 1
    print(f"  Seeded {created} frame products.")


def remove_frames(apps, schema_editor):
    Product = apps.get_model('core', 'Product')
    names = [f['name'] for f in FRAMES]
    Product.objects.filter(name__in=names).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_reset_superuser'),
    ]

    operations = [
        migrations.RunPython(seed_frames, remove_frames),
    ]
