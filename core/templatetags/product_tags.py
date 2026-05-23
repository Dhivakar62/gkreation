"""
Custom template tag: product_image_url
Returns the correct URL for a product image.
- If image path starts with 'images/' or 'videos/' → served from WhiteNoise static
- Otherwise falls back to product.image.url (media/)
"""
from django import template
from django.templatetags.static import static

register = template.Library()

@register.simple_tag
def product_image_url(product):
    """Return correct URL for a product image, preferring static/ for committed assets."""
    if not product.image:
        return ''
    image_name = str(product.image)
    # Images committed to git → serve via WhiteNoise static
    if image_name.startswith('images/'):
        return static(image_name)
    # Uploaded via admin → serve via media URL
    try:
        return product.image.url
    except Exception:
        return ''
