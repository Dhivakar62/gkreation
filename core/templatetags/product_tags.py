"""
product_image_url — resolves any product image to a correct URL.

Routing logic:
  images/frames/...    → {% static %} via WhiteNoise  (committed, permanent)
  images/paintings/... → {% static %} via WhiteNoise  (committed, permanent)
  images/products/...  → {% static %} via WhiteNoise  (committed, permanent)
  products/...         → static('images/products/...') — remapped to static copy
  anything else        → product.image.url (media/, admin uploads)
"""
from django import template
from django.templatetags.static import static

register = template.Library()


@register.simple_tag
def product_image_url(product):
    if not product or not product.image:
        return ''
    path = str(product.image).strip()
    if not path:
        return ''

    # Already in static/images/ — serve via WhiteNoise
    if path.startswith('images/'):
        return static(path)

    # Old-format products/filename.jpg — remap to static copy
    if path.startswith('products/'):
        filename = path.split('/', 1)[-1]
        static_path = f'images/products/{filename}'
        return static(static_path)

    # Fallback: admin-uploaded media
    try:
        return product.image.url
    except Exception:
        return ''
