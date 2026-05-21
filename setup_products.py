"""
setup_products.py  —  Run this ONE file to create all images + products
Place this file inside your GKCREATIONS folder (same level as manage.py)
Then run:  python setup_products.py
"""

import os, sys, io, random, math
import django

# ── 1. Django bootstrap ───────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GKCREATIONS.settings')
django.setup()

from django.core.files.base import ContentFile
from core.models import Product

# ── 2. Check Pillow ───────────────────────────────────────────────────────────
try:
    from PIL import Image, ImageDraw, ImageFilter
except ImportError:
    print("Installing Pillow...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow", "--break-system-packages", "-q"])
    from PIL import Image, ImageDraw, ImageFilter

# ── 3. Image generators ───────────────────────────────────────────────────────

def img_to_bytes(img):
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=93)
    return buf.getvalue()

def make_frame(border_rgb, inner_rgb, accent_rgb, label):
    W, H = 600, 500
    img = Image.new('RGB', (W, H), (245, 240, 235))
    d = ImageDraw.Draw(img)

    # Outer border layers
    for i in range(28):
        t = i / 28
        r = int(border_rgb[0]*(1-t) + inner_rgb[0]*t)
        g = int(border_rgb[1]*(1-t) + inner_rgb[1]*t)
        b = int(border_rgb[2]*(1-t) + inner_rgb[2]*t)
        d.rectangle([i, i, W-1-i, H-1-i], outline=(r,g,b))

    # Mat
    d.rectangle([45, 45, W-46, H-46], fill=(252,248,243), outline=accent_rgb, width=3)

    # Corner ornaments
    for cx, cy in [(65,65),(W-66,65),(65,H-66),(W-66,H-66)]:
        d.ellipse([cx-14,cy-14,cx+14,cy+14], fill=accent_rgb)
        d.ellipse([cx-7, cy-7, cx+7, cy+7],  fill=border_rgb)

    # Inner canvas
    d.rectangle([90, 90, W-91, H-91], fill=(235,228,218))

    # Simple landscape inside frame
    sky = (135, 185, 220)
    d.rectangle([90,90,W-91,310], fill=sky)
    # mountains
    d.polygon([(90,310),(190,160),(310,240),(420,140),(W-91,310)], fill=(100,130,90))
    d.polygon([(90,310),(220,200),(360,280),(W-91,310)],           fill=(80,110,70))
    # ground
    d.rectangle([90,310,W-91,H-91], fill=(120,160,90))
    # sun
    d.ellipse([430,110,480,160], fill=(255,225,80))
    for angle in range(0,360,30):
        sx = 455 + int(35*math.cos(math.radians(angle)))
        sy = 135 + int(35*math.sin(math.radians(angle)))
        ex = 455 + int(48*math.cos(math.radians(angle)))
        ey = 135 + int(48*math.sin(math.radians(angle)))
        d.line([sx,sy,ex,ey], fill=(255,225,80), width=2)

    # Label bar
    d.rectangle([90, H-90, W-91, H-46], fill=border_rgb)
    d.text((W//2, H-68), label, fill=(255,255,255), anchor='mm')
    return img_to_bytes(img)


def make_painting_landscape(sky_top, sky_bot, mtn1, mtn2, ground, sun_col, label):
    W, H = 600, 500
    img = Image.new('RGB', (W, H), (240,235,228))
    d = ImageDraw.Draw(img)
    # Canvas border
    d.rectangle([0,0,W-1,H-1], outline=(180,160,130), width=6)
    # Sky gradient
    for y in range(10, 330):
        t = (y-10)/320
        r = int(sky_top[0]*(1-t)+sky_bot[0]*t)
        g = int(sky_top[1]*(1-t)+sky_bot[1]*t)
        b = int(sky_top[2]*(1-t)+sky_bot[2]*t)
        d.line([10,y,W-11,y], fill=(r,g,b))
    # Mountains back
    d.polygon([(10,330),(130,140),(260,220),(390,110),(W-11,330)], fill=mtn1)
    # Mountains front
    d.polygon([(10,330),(180,200),(330,270),(W-11,330)], fill=mtn2)
    # Ground
    d.rectangle([10,330,W-11,H-10], fill=ground)
    # Sun/moon
    d.ellipse([450,60,510,120], fill=sun_col)
    # Clouds
    for cx,cy in [(150,90),(320,70),(200,120)]:
        for ox in [-20,0,20]:
            d.ellipse([cx+ox-25,cy-18,cx+ox+25,cy+18], fill=(255,255,255))
    # Trees
    for tx in [50,100,480,530]:
        d.rectangle([tx-5,310,tx+5,390], fill=(70,45,15))
        d.ellipse([tx-22,265,tx+22,325],  fill=(40,90,40))
    # River
    d.ellipse([220,370,380,420], fill=(100,160,210))
    # Label
    d.rectangle([10,H-45,W-11,H-10], fill=(30,30,30))
    d.text((W//2, H-27), label, fill=(220,200,150), anchor='mm')
    return img_to_bytes(img)


def make_painting_abstract(colors, label):
    W, H = 600, 500
    img = Image.new('RGB', (W, H), (250,248,245))
    d = ImageDraw.Draw(img)
    rng = random.Random(sum(ord(c) for c in label))
    # Background wash
    bg = colors[0]
    d.rectangle([10,10,W-11,H-11], fill=(
        min(255,bg[0]+120), min(255,bg[1]+120), min(255,bg[2]+120)))
    # Paint blobs
    for _ in range(60):
        x = rng.randint(20,W-20)
        y = rng.randint(20,H-20)
        r = rng.randint(15,90)
        c = colors[rng.randint(0,len(colors)-1)]
        d.ellipse([x-r,y-r,x+r,y+r], fill=c)
    # Strokes
    for _ in range(30):
        x1,y1 = rng.randint(20,W-20), rng.randint(20,H-20)
        x2,y2 = x1+rng.randint(-120,120), y1+rng.randint(-80,80)
        c = colors[rng.randint(0,len(colors)-1)]
        d.line([x1,y1,x2,y2], fill=c, width=rng.randint(4,16))
    img = img.filter(ImageFilter.SMOOTH)
    d = ImageDraw.Draw(img)
    # Border
    d.rectangle([5,5,W-6,H-6], outline=(50,50,50), width=5)
    # Label
    d.rectangle([10,H-45,W-11,H-10], fill=(30,30,30))
    d.text((W//2, H-27), label, fill=(220,200,150), anchor='mm')
    return img_to_bytes(img)


def make_painting_floral(bg, petal_colors, label):
    W, H = 600, 500
    img = Image.new('RGB', (W, H), bg)
    d = ImageDraw.Draw(img)
    rng = random.Random(sum(ord(c) for c in label))
    # Stem lines
    for cx,cy in [(120,380),(240,360),(360,370),(480,350),(180,290),(420,280)]:
        d.line([cx,cy,cx+rng.randint(-20,20),cy-80], fill=(40,100,40), width=4)
    # Flowers
    for cx,cy in [(120,300),(240,280),(360,290),(480,270),(180,210),(420,200)]:
        for a in range(0,360,45):
            px = cx+int(38*math.cos(math.radians(a)))
            py = cy+int(38*math.sin(math.radians(a)))
            c = petal_colors[rng.randint(0,len(petal_colors)-1)]
            d.ellipse([px-16,py-16,px+16,py+16], fill=c)
        d.ellipse([cx-18,cy-18,cx+18,cy+18], fill=(255,230,50))
        d.ellipse([cx-9, cy-9, cx+9, cy+9],  fill=(200,180,30))
    # Leaves
    for lx,ly in [(80,340),(200,320),(340,330),(500,310)]:
        d.ellipse([lx-15,ly-30,lx+15,ly+10], fill=(50,120,50))
    # Border
    d.rectangle([5,5,W-6,H-6], outline=(80,50,20), width=5)
    # Label
    d.rectangle([10,H-45,W-11,H-10], fill=(80,40,10))
    d.text((W//2, H-27), label, fill=(255,240,200), anchor='mm')
    return img_to_bytes(img)


def make_painting_portrait(bg, skin, cloth, label):
    W, H = 600, 500
    img = Image.new('RGB', (W, H), bg)
    d = ImageDraw.Draw(img)
    # BG gradient
    for y in range(10, H-10):
        t = y/(H-20)
        r = int(bg[0]*(1-t)+max(0,bg[0]-40)*t)
        g = int(bg[1]*(1-t)+max(0,bg[1]-40)*t)
        b = int(bg[2]*(1-t)+max(0,bg[2]-40)*t)
        d.line([10,y,W-11,y], fill=(r,g,b))
    # Shoulders/body
    d.ellipse([180,310,420,500], fill=cloth)
    # Neck
    d.rectangle([270,280,330,340], fill=skin)
    # Head
    d.ellipse([190,110,410,320], fill=skin)
    # Hair
    d.ellipse([190,110,410,210], fill=(60,35,15))
    d.ellipse([170,160,220,270], fill=(60,35,15))
    d.ellipse([380,160,430,270], fill=(60,35,15))
    # Eyes
    for ex in [255,345]:
        d.ellipse([ex-18,195,ex+18,225], fill=(255,255,255))
        d.ellipse([ex-10,200,ex+10,220], fill=(60,40,20))
        d.ellipse([ex-5, 203,ex+5, 213], fill=(20,10,5))
        d.ellipse([ex+4, 203,ex+9, 208], fill=(255,255,255))
    # Eyebrows
    d.arc([237,178,293,198], 200,340, fill=(60,35,15), width=4)
    d.arc([307,178,363,198], 200,340, fill=(60,35,15), width=4)
    # Nose
    d.arc([285,235,315,265], 30,150, fill=(skin[0]-30,skin[1]-30,skin[2]-30), width=3)
    # Lips
    d.arc([270,270,330,296],   0,180, fill=(180,80,80), width=4)
    d.arc([270,265,330,285], 180,360, fill=(200,100,100), width=3)
    # Border
    d.rectangle([5,5,W-6,H-6], outline=(120,90,40), width=6)
    # Label
    d.rectangle([10,H-45,W-11,H-10], fill=(30,20,10))
    d.text((W//2, H-27), label, fill=(220,200,150), anchor='mm')
    return img_to_bytes(img)


# ── 4. Product definitions ────────────────────────────────────────────────────

FRAMES = [
    dict(name='Vintage Oak Frame',       price=1299, size='12×16 inch', material='Oak Wood',              model='FR-001',
         desc='Handcrafted vintage oak wood frame with a warm classic finish. Natural grain adds timeless character to any portrait or artwork.',
         img=lambda: make_frame((139,90,43),(101,67,33),(200,150,70),'Vintage Oak Frame')),
    dict(name='Modern Black Frame',      price=799,  size='8×10 inch',  material='MDF + Matte Laminate',  model='FR-002',
         desc='Sleek matte-black frame for contemporary art and photography. Clean lines suit any modern interior.',
         img=lambda: make_frame((30,30,30),(15,15,15),(200,170,80),'Modern Black Frame')),
    dict(name='Gold Ornate Frame',       price=2499, size='18×24 inch', material='Resin + Gold Finish',   model='FR-003',
         desc='Luxurious gold ornate frame with intricate detailing. Transforms walls into gallery spaces.',
         img=lambda: make_frame((180,145,40),(140,105,20),(230,200,90),'Gold Ornate Frame')),
    dict(name='Rustic Barn Frame',       price=1599, size='10×14 inch', material='Reclaimed Wood',        model='FR-004',
         desc='Authentic reclaimed barn-wood frame — each piece unique. Perfect for farmhouse and boho interiors.',
         img=lambda: make_frame((110,72,38),(80,52,25),(165,115,60),'Rustic Barn Frame')),
    dict(name='White Minimalist Frame',  price=699,  size='6×8 inch',   material='Solid Wood + White Paint',model='FR-005',
         desc='Crisp white frame for Scandinavian and minimalist décor. Brightens any room instantly.',
         img=lambda: make_frame((220,220,215),(200,200,195),(150,150,140),'White Minimalist')),
    dict(name='Antique Silver Frame',    price=1899, size='14×18 inch', material='Zinc Alloy + Silver Plating',model='FR-006',
         desc='Classic European-style antique silver frame. Complements both monochrome and colourful artwork.',
         img=lambda: make_frame((160,165,170),(120,125,130),(210,215,220),'Antique Silver Frame')),
    dict(name='Cherry Wood Frame',       price=1799, size='11×14 inch', material='Cherry Wood',            model='FR-007',
         desc='Rich reddish-brown cherry wood frame that matures beautifully. Ideal for portraits and diplomas.',
         img=lambda: make_frame((160,55,30),(120,38,18),(210,105,65),'Cherry Wood Frame')),
    dict(name='Walnut Luxury Frame',     price=2999, size='16×20 inch', material='American Black Walnut',  model='FR-008',
         desc='Premium black walnut frame radiating sophistication. Dark chocolate tones elevate any living space.',
         img=lambda: make_frame((75,48,20),(55,32,8),(150,100,48),'Walnut Luxury Frame')),
    dict(name='Teak Art Frame',          price=2199, size='13×19 inch', material='Teak Wood',              model='FR-009',
         desc='Sturdy teak frame with natural oil finish. Resistant to warping — built to last generations.',
         img=lambda: make_frame((115,78,35),(88,57,22),(175,133,68),'Teak Art Frame')),
    dict(name='Bamboo Eco Frame',        price=899,  size='8×12 inch',  material='Sustainable Bamboo',     model='FR-010',
         desc='Eco-friendly bamboo frame — stronger than hardwood, grows fast. Style meets sustainability.',
         img=lambda: make_frame((118,132,58),(90,104,38),(172,185,80),'Bamboo Eco Frame')),
]

PAINTINGS = [
    dict(name='Sunset Over Mountains',  price=4999, size='24×36 inch', material='Acrylic on Canvas',  model='PT-001',
         desc='Breathtaking golden-hour over misty peaks. Hand-painted with premium acrylics — a statement piece for any living room.',
         img=lambda: make_painting_landscape((255,140,60),(255,200,100),(90,115,75),(65,95,55),(90,140,70),(255,220,60),'Sunset Over Mountains')),
    dict(name='Ocean Serenity',         price=3799, size='20×30 inch', material='Oil on Canvas',      model='PT-002',
         desc='Tranquil seascape at dusk painted in rich oils. Brings the soothing energy of the sea into your home.',
         img=lambda: make_painting_landscape((30,100,190),(80,160,220),(40,80,130),(30,60,110),(40,120,60),(240,230,200),'Ocean Serenity')),
    dict(name='Abstract Bloom',         price=2999, size='16×20 inch', material='Watercolour on Paper',model='PT-003',
         desc='Free-flowing abstract floral in vibrant watercolours. Dynamic and joyful — perfect for modern interiors.',
         img=lambda: make_painting_abstract([(220,70,110),(255,150,30),(80,150,210),(180,50,180),(255,200,50)],'Abstract Bloom')),
    dict(name='Village Life',           price=5499, size='30×40 inch', material='Oil on Canvas',      model='PT-004',
         desc='Warmly rendered rural village scene in earthy tones. A heartfelt celebration of country living.',
         img=lambda: make_painting_landscape((180,210,240),(220,235,210),(95,130,60),(70,110,45),(110,155,75),(255,240,180),'Village Life')),
    dict(name='Golden Harvest',         price=3299, size='18×24 inch', material='Acrylic on Canvas',  model='PT-005',
         desc='Sun-drenched wheat fields under a glowing sky. Rich amber palette — stunning in dining rooms.',
         img=lambda: make_painting_landscape((255,200,80),(255,230,140),(180,150,40),(150,120,25),(160,180,60),(255,255,100),'Golden Harvest')),
    dict(name='Mystic Forest',          price=4299, size='22×32 inch', material='Oil on Canvas',      model='PT-006',
         desc='Enchanting forest at twilight — light pierces ancient canopy. Deep greens evoke wonder and calm.',
         img=lambda: make_painting_landscape((20,60,30),(40,100,50),(30,80,35),(20,65,28),(35,90,40),(200,200,180),'Mystic Forest')),
    dict(name='Floral Symphony',        price=2599, size='14×18 inch', material='Acrylic on Canvas',  model='PT-007',
         desc='Joyful celebration of roses, lotuses and wildflowers in vivid pinks and oranges. Brings life to any wall.',
         img=lambda: make_painting_floral((240,235,220),[(220,60,90),(255,120,30),(200,40,150),(255,200,50)],'Floral Symphony')),
    dict(name='Riverside Calm',         price=3599, size='20×28 inch', material='Watercolour on Canvas',model='PT-008',
         desc='Peaceful river through lush valleys in delicate watercolour washes. Evokes quietude and harmony.',
         img=lambda: make_painting_landscape((100,170,230),(150,210,240),(55,110,65),(40,90,50),(60,130,70),(255,255,220),'Riverside Calm')),
    dict(name='Abstract Emotions',      price=3999, size='24×24 inch', material='Mixed Media on Canvas',model='PT-009',
         desc='Bold abstract channelling raw emotion through colour and texture. Speaks differently to every viewer.',
         img=lambda: make_painting_abstract([(100,30,180),(40,150,200),(200,30,90),(255,150,0),(30,180,120)],'Abstract Emotions')),
    dict(name='Portrait of Grace',      price=6999, size='20×28 inch', material='Oil on Canvas',      model='PT-010',
         desc='Timeless classical portrait with luminous skin tones. A collector\'s piece and future family heirloom.',
         img=lambda: make_painting_portrait((180,200,220),(255,215,175),(70,90,160),'Portrait of Grace')),
]

# ── 5. Run ────────────────────────────────────────────────────────────────────

def run():
    print("=" * 55)
    print("  GKreation's — Product Setup")
    print("=" * 55)

    count_before = Product.objects.count()
    Product.objects.all().delete()
    print(f"\n🗑  Removed {count_before} existing product(s).\n")

    ok, fail = 0, 0

    print("🖼  Creating Frames...")
    for p in FRAMES:
        try:
            prod = Product(
                name=p['name'], category='frames', price=p['price'],
                size=p['size'], material=p['material'],
                model_number=p['model'], description=p['desc'],
                stock=15, is_active=True,
            )
            img_bytes = p['img']()
            prod.image.save(f"{p['name'].replace(' ','_')}.jpg",
                            ContentFile(img_bytes), save=True)
            print(f"  ✓  {p['name']}  —  ₹{p['price']}")
            ok += 1
        except Exception as e:
            print(f"  ✗  {p['name']}: {e}")
            fail += 1

    print("\n🎨 Creating Paintings...")
    for p in PAINTINGS:
        try:
            prod = Product(
                name=p['name'], category='paintings', price=p['price'],
                size=p['size'], material=p['material'],
                model_number=p['model'], description=p['desc'],
                stock=10, is_active=True,
            )
            img_bytes = p['img']()
            prod.image.save(f"{p['name'].replace(' ','_')}.jpg",
                            ContentFile(img_bytes), save=True)
            print(f"  ✓  {p['name']}  —  ₹{p['price']}")
            ok += 1
        except Exception as e:
            print(f"  ✗  {p['name']}: {e}")
            fail += 1

    print("\n" + "=" * 55)
    print(f"  ✅  Products created : {ok}")
    if fail:
        print(f"  ❌  Failed          : {fail}")
    print(f"  📦  Total in DB      : {Product.objects.count()}")
    print("=" * 55)
    print("\n  👉  Open http://127.0.0.1:8000 to see your products!")

if __name__ == '__main__':
    run()
