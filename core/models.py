from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=15, blank=True)
    address_line1 = models.CharField(max_length=255, blank=True)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    pincode = models.CharField(max_length=10, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def get_full_address(self):
        parts = [self.address_line1, self.address_line2, self.city, self.state, self.pincode]
        return ', '.join([p for p in parts if p])


class Category(models.Model):
    CATEGORY_CHOICES = [
        ('frames', 'Frames'),
        ('paintings', 'Paintings'),
    ]
    name = models.CharField(max_length=100, choices=CATEGORY_CHOICES)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Categories'


class Product(models.Model):
    CATEGORY_CHOICES = [
        ('frames', 'Frames'),
        ('paintings', 'Paintings'),
    ]
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    size = models.CharField(max_length=100)
    material = models.CharField(max_length=100)
    model_number = models.CharField(max_length=100, blank=True)
    description = models.TextField()
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    stock = models.IntegerField(default=10)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Cart"

    def get_total(self):
        return sum(item.get_subtotal() for item in self.items.all())

    def get_item_count(self):
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"

    def get_subtotal(self):
        return self.product.price * self.quantity


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    PAYMENT_CHOICES = [
        ('razorpay', 'Razorpay (UPI / Card / NetBanking)'),
        ('cod', 'Cash on Delivery'),
    ]
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='cod')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')

    # Razorpay fields
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=200, blank=True, null=True)

    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    advance_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Delivery address
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    phone = models.CharField(max_length=15)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    cancellation_deadline = models.DateTimeField(null=True, blank=True)
    expected_delivery = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.cancellation_deadline = timezone.now() + timedelta(days=3)
            self.expected_delivery = timezone.now() + timedelta(days=14)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order #{self.pk} by {self.user.username}"

    def can_cancel(self):
        return (
            self.cancellation_deadline and
            timezone.now() < self.cancellation_deadline and
            self.status in ['pending', 'confirmed']
        )

    def get_advance_amount(self):
        return self.total_amount * Decimal('0.5')

    def get_balance_due(self):
        return max(self.total_amount - self.advance_paid, Decimal('0.00'))


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"

    def get_subtotal(self):
        return self.price * self.quantity


class Customization(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customizations')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    image = models.ImageField(upload_to='customizations/')
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Customization by {self.user.username} - {self.created_at.date()}"


class PortraitOrder(models.Model):
    SIZE_CHOICES = [
        ('small',  'Small (8x10 inch) — ₹500'),
        ('medium', 'Medium (12x16 inch) — ₹900'),
        ('large',  'Large (18x24 inch) — ₹1500'),
    ]
    SIZE_PRICES = {'small': 500, 'medium': 900, 'large': 1500}
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='portrait_orders')
    name = models.CharField(max_length=200)
    image = models.ImageField(upload_to='portraits/')
    size = models.CharField(max_length=20, choices=SIZE_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    special_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expected_delivery = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        self.price = self.SIZE_PRICES.get(self.size, 500)
        if not self.pk:
            self.expected_delivery = timezone.now() + timedelta(days=14)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Portrait: {self.name} by {self.user.username}"


class WeddingEventOrder(models.Model):
    EVENT_CHOICES = [
        ('photoshoot',  'Photoshoot'),
        ('videography', 'Videography'),
        ('both',        'Photoshoot + Videography'),
    ]
    STATUS_CHOICES = [
        ('pending',   'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wedding_orders')
    location = models.CharField(max_length=255)
    event_type = models.CharField(max_length=20, choices=EVENT_CHOICES)
    event_date = models.DateField()
    primary_time = models.TimeField()
    optional_time = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Wedding Event: {self.user.username} - {self.event_date}"
