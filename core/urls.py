from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('register/', views.register_view, name='register'),
    path('login/',    views.login_view,    name='login'),
    path('logout/',   views.logout_view,   name='logout'),

    # Home & Products
    path('',                    views.home_view,           name='home'),
    path('frames/',             views.frames_view,         name='frames'),
    path('paintings/',          views.paintings_view,      name='paintings'),
    path('product/<int:pk>/',   views.product_detail_view, name='product_detail'),

    # Cart
    path('cart/',                          views.cart_view,       name='cart'),
    path('cart/add/<int:product_id>/',     views.add_to_cart,     name='add_to_cart'),
    path('cart/update/<int:item_id>/',     views.update_cart,     name='update_cart'),
    path('cart/remove/<int:item_id>/',     views.remove_from_cart,name='remove_from_cart'),

    # Buy Now
    path('buy-now/<int:product_id>/', views.buy_now, name='buy_now'),

    # Checkout & Orders
    path('checkout/',                        views.checkout_view,        name='checkout'),
    path('orders/',                          views.order_list_view,      name='order_list'),
    path('orders/<int:pk>/',                 views.order_detail_view,    name='order_detail'),
    path('orders/<int:pk>/cancel/',          views.cancel_order,         name='cancel_order'),

    # Razorpay
    path('orders/<int:pk>/payment/',         views.razorpay_payment_view, name='razorpay_payment'),
    path('razorpay/callback/',               views.razorpay_callback,     name='razorpay_callback'),

    # Customization
    path('customize/',                    views.customize_view, name='customize'),
    path('customize/<int:product_id>/',   views.customize_view, name='customize_product'),

    # Services
    path('services/paintings/', views.service_paintings_view, name='service_paintings'),
    path('services/portrait/',  views.portrait_view,          name='portrait'),
    path('services/wedding/',   views.wedding_event_view,     name='wedding_event'),

    # Profile
    path('profile/', views.profile_view, name='profile'),

    # Static
    path('about/',   views.about_view,   name='about'),
    path('contact/', views.contact_view, name='contact'),
]
