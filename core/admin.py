from django.contrib import admin
from .models import (
    UserProfile, Product, Cart, CartItem, Order, OrderItem,
    Customization, PortraitOrder, WeddingEventOrder
)

admin.site.site_header = "GKreation's Admin"
admin.site.site_title = "GKreation's"
admin.site.index_title = "Dashboard"


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'city', 'state']
    search_fields = ['user__username', 'user__email', 'phone']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'stock', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['name', 'material']
    list_editable = ['price', 'stock', 'is_active']


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'quantity', 'price']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'status', 'payment_method',
        'payment_status', 'total_amount', 'advance_paid', 'created_at'
    ]
    list_filter = ['status', 'payment_method', 'payment_status']
    search_fields = ['user__username', 'user__email', 'razorpay_order_id', 'razorpay_payment_id']
    list_editable = ['status']
    inlines = [OrderItemInline]
    readonly_fields = [
        'created_at', 'cancellation_deadline', 'expected_delivery',
        'razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature',
    ]

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            return [
                'user', 'total_amount', 'advance_paid', 'payment_method',
                'payment_status', 'address_line1', 'address_line2', 'city',
                'state', 'pincode', 'phone', 'created_at',
                'cancellation_deadline', 'expected_delivery',
                'razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature',
            ]
        return self.readonly_fields


@admin.register(Customization)
class CustomizationAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'status', 'created_at']
    list_filter = ['status']
    list_editable = ['status']


@admin.register(PortraitOrder)
class PortraitOrderAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'size', 'price', 'status', 'created_at']
    list_filter = ['status', 'size']
    list_editable = ['status']


@admin.register(WeddingEventOrder)
class WeddingEventOrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'location', 'event_type', 'event_date', 'status']
    list_filter = ['status', 'event_type']
    list_editable = ['status']
