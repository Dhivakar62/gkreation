import razorpay
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.http import HttpResponseBadRequest
from decimal import Decimal

from .models import (
    Product, Cart, CartItem, Order, OrderItem,
    Customization, PortraitOrder, WeddingEventOrder, UserProfile
)
from .forms import (
    RegisterForm, LoginForm, ProfileUpdateForm,
    CustomizationForm, PortraitOrderForm, WeddingEventForm, CheckoutForm
)


def get_razorpay_client():
    return razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    )


# ─── Auth ──────────────────────────────────────────────────────────────────────

def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            login(request, user)
            messages.success(request, f"Welcome to GK Creations, {user.first_name}! 🎨")
            return redirect('home')
        messages.error(request, "Please correct the errors below.")
    else:
        form = RegisterForm()
    return render(request, 'core/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
            )
            if user:
                login(request, user)
                messages.success(request, f"Welcome back, {user.first_name or user.username}!")
                return redirect(request.GET.get('next', 'home'))
            messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()
    return render(request, 'core/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')


# ─── Home & Products ───────────────────────────────────────────────────────────

def home_view(request):
    frames = Product.objects.filter(category='frames', is_active=True)
    paintings = Product.objects.filter(category='paintings', is_active=True)
    return render(request, 'core/home.html', {'frames': frames, 'paintings': paintings})


def product_detail_view(request, pk):
    product = get_object_or_404(Product, pk=pk, is_active=True)
    return render(request, 'core/product_detail.html', {'product': product})


def frames_view(request):
    products = Product.objects.filter(category='frames', is_active=True)
    return render(request, 'core/product_list.html', {
        'products': products, 'title': 'Frames', 'category': 'frames'
    })


def paintings_view(request):
    products = Product.objects.filter(category='paintings', is_active=True)
    return render(request, 'core/product_list.html', {
        'products': products, 'title': 'Paintings', 'category': 'paintings'
    })


# ─── Cart ──────────────────────────────────────────────────────────────────────

@login_required
def cart_view(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    return render(request, 'core/cart.html', {'cart': cart})


@login_required
@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    cart, _ = Cart.objects.get_or_create(user=request.user)
    item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        item.quantity += 1
        item.save()
    messages.success(request, f"'{product.name}' added to cart!")
    return redirect(request.META.get('HTTP_REFERER', 'cart'))


@login_required
@require_POST
def update_cart(request, item_id):
    item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
    quantity = int(request.POST.get('quantity', 1))
    if quantity < 1:
        item.delete()
        messages.info(request, "Item removed from cart.")
    else:
        item.quantity = quantity
        item.save()
    return redirect('cart')


@login_required
@require_POST
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
    item.delete()
    messages.info(request, "Item removed from cart.")
    return redirect('cart')


# ─── Buy Now ───────────────────────────────────────────────────────────────────

@login_required
def buy_now(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart.items.all().delete()
    CartItem.objects.create(cart=cart, product=product, quantity=1)
    messages.info(request, f"Buying '{product.name}' — complete your order below.")
    return redirect('checkout')


# ─── Checkout ──────────────────────────────────────────────────────────────────

@login_required
def checkout_view(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    if not cart.items.exists():
        messages.warning(request, "Your cart is empty.")
        return redirect('cart')

    profile = getattr(request.user, 'profile', None)
    initial = {}
    if profile:
        initial = {
            'address_line1': profile.address_line1,
            'address_line2': profile.address_line2,
            'city': profile.city,
            'state': profile.state,
            'pincode': profile.pincode,
            'phone': profile.phone,
        }

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            total = cart.get_total()
            advance = total * Decimal('0.5')
            payment_method = form.cleaned_data['payment_method']

            with transaction.atomic():
                # Create order with pending status
                order = Order.objects.create(
                    user=request.user,
                    total_amount=total,
                    advance_paid=advance,
                    payment_method=payment_method,
                    payment_status='pending',
                    status='pending',
                    address_line1=form.cleaned_data['address_line1'],
                    address_line2=form.cleaned_data.get('address_line2', ''),
                    city=form.cleaned_data['city'],
                    state=form.cleaned_data['state'],
                    pincode=form.cleaned_data['pincode'],
                    phone=form.cleaned_data['phone'],
                )
                for item in cart.items.all():
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        price=item.product.price,
                    )
                cart.items.all().delete()

            if payment_method == 'razorpay':
                # Create a Razorpay order for the advance amount
                client = get_razorpay_client()
                amount_paise = int(advance * 100)   # Razorpay uses paise
                rzp_order = client.order.create({
                    'amount': amount_paise,
                    'currency': 'INR',
                    'receipt': f'order_{order.pk}',
                    'payment_capture': 1,           # auto-capture
                    'notes': {
                        'order_id': str(order.pk),
                        'user': request.user.username,
                    }
                })
                # Save Razorpay order ID on our order
                order.razorpay_order_id = rzp_order['id']
                order.save()
                return redirect('razorpay_payment', pk=order.pk)

            else:  # COD
                order.status = 'confirmed'
                order.payment_status = 'pending'
                order.save()
                messages.success(
                    request,
                    f"Order #{order.pk} placed! Pay ₹{advance:.2f} cash on delivery."
                )
                return redirect('order_detail', pk=order.pk)

        messages.error(request, "Please fill all required fields correctly.")

    else:
        form = CheckoutForm(initial=initial)

    return render(request, 'core/checkout.html', {'form': form, 'cart': cart})


# ─── Razorpay Payment Page ─────────────────────────────────────────────────────

@login_required
def razorpay_payment_view(request, pk):
    """Show the Razorpay checkout page."""
    order = get_object_or_404(Order, pk=pk, user=request.user)

    if order.payment_status == 'paid':
        messages.info(request, "This order is already paid.")
        return redirect('order_detail', pk=order.pk)

    advance = order.total_amount * Decimal('0.5')
    amount_paise = int(advance * 100)

    context = {
        'order': order,
        'advance': advance,
        'amount_paise': amount_paise,
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'razorpay_order_id': order.razorpay_order_id,
        'user_name': request.user.get_full_name() or request.user.username,
        'user_email': request.user.email,
        'user_phone': getattr(order, 'phone', ''),
    }
    return render(request, 'core/razorpay_payment.html', context)


# ─── Razorpay Callback (called after payment) ──────────────────────────────────

@csrf_exempt
def razorpay_callback(request):
    """
    Razorpay redirects here after payment.
    We verify the payment signature server-side before confirming the order.
    """
    if request.method != 'POST':
        return redirect('home')

    rzp_order_id  = request.POST.get('razorpay_order_id', '')
    rzp_payment_id = request.POST.get('razorpay_payment_id', '')
    rzp_signature  = request.POST.get('razorpay_signature', '')

    # Find the matching order
    try:
        order = Order.objects.get(razorpay_order_id=rzp_order_id)
    except Order.DoesNotExist:
        messages.error(request, "Order not found. Contact support.")
        return redirect('home')

    client = get_razorpay_client()
    params = {
        'razorpay_order_id': rzp_order_id,
        'razorpay_payment_id': rzp_payment_id,
        'razorpay_signature': rzp_signature,
    }

    try:
        # Verify signature — raises SignatureVerificationError if invalid
        client.utility.verify_payment_signature(params)

        # Signature valid → payment confirmed
        order.razorpay_payment_id = rzp_payment_id
        order.razorpay_signature  = rzp_signature
        order.payment_status = 'paid'
        order.status = 'confirmed'
        order.save()

        messages.success(
            request,
            f"✅ Payment of ₹{order.advance_paid:.2f} received! "
            f"Order #{order.pk} is now confirmed."
        )
        return redirect('order_detail', pk=order.pk)

    except razorpay.errors.SignatureVerificationError:
        # Signature mismatch — possible tampering
        order.payment_status = 'failed'
        order.save()
        messages.error(
            request,
            "⚠️ Payment verification failed. If money was deducted, "
            "please contact us with your payment ID."
        )
        return redirect('order_detail', pk=order.pk)

    except Exception as e:
        order.payment_status = 'failed'
        order.save()
        messages.error(request, f"Payment error: {str(e)}. Please contact support.")
        return redirect('order_detail', pk=order.pk)


# ─── Orders ────────────────────────────────────────────────────────────────────

@login_required
def order_list_view(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'core/order_list.html', {'orders': orders})


@login_required
def order_detail_view(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    return render(request, 'core/order_detail.html', {'order': order})


@login_required
@require_POST
def cancel_order(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    if order.can_cancel():
        order.status = 'cancelled'
        order.save()
        messages.warning(
            request,
            f"Order #{order.pk} cancelled. "
            "Note: Advance payment is non-refundable."
        )
    else:
        messages.error(request, "Cancellation period has expired (3 days).")
    return redirect('order_detail', pk=pk)


# ─── Customization ─────────────────────────────────────────────────────────────

@login_required
def customize_view(request, product_id=None):
    product = None
    if product_id:
        product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        form = CustomizationForm(request.POST, request.FILES)
        if form.is_valid():
            custom = form.save(commit=False)
            custom.user = request.user
            custom.product = product
            custom.save()
            messages.success(request, "Customization request submitted! We'll contact you shortly.")
            return redirect('home')
    else:
        form = CustomizationForm()
    return render(request, 'core/customize.html', {'form': form, 'product': product})


# ─── Services ──────────────────────────────────────────────────────────────────

def service_paintings_view(request):
    paintings = Product.objects.filter(category='paintings', is_active=True)
    return render(request, 'core/service_paintings.html', {'paintings': paintings})


@login_required
def portrait_view(request):
    if request.method == 'POST':
        form = PortraitOrderForm(request.POST, request.FILES)
        if form.is_valid():
            portrait = form.save(commit=False)
            portrait.user = request.user
            portrait.save()
            messages.success(request, f"Portrait order placed! Price: ₹{portrait.price}. We'll begin soon!")
            return redirect('profile')
    else:
        form = PortraitOrderForm()
    return render(request, 'core/portrait.html', {'form': form})


@login_required
def wedding_event_view(request):
    if request.method == 'POST':
        form = WeddingEventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.user = request.user
            event.save()
            messages.success(request, "Wedding event booking submitted! We'll confirm shortly.")
            return redirect('profile')
    else:
        form = WeddingEventForm()
    return render(request, 'core/wedding_event.html', {'form': form})


# ─── Profile ───────────────────────────────────────────────────────────────────

@login_required
def profile_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    portrait_orders = PortraitOrder.objects.filter(user=request.user).order_by('-created_at')
    wedding_orders = WeddingEventOrder.objects.filter(user=request.user).order_by('-created_at')
    customizations = Customization.objects.filter(user=request.user).order_by('-created_at')

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            request.user.first_name = form.cleaned_data.get('first_name', request.user.first_name)
            request.user.last_name  = form.cleaned_data.get('last_name',  request.user.last_name)
            request.user.email      = form.cleaned_data.get('email',       request.user.email)
            request.user.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=profile, initial={
            'first_name': request.user.first_name,
            'last_name':  request.user.last_name,
            'email':      request.user.email,
        })

    return render(request, 'core/profile.html', {
        'form': form, 'profile': profile, 'orders': orders,
        'portrait_orders': portrait_orders,
        'wedding_orders': wedding_orders,
        'customizations': customizations,
    })


# ─── Static Pages ──────────────────────────────────────────────────────────────

def about_view(request):
    return render(request, 'core/about.html')


def contact_view(request):
    if request.method == 'POST':
        messages.success(request, "Thank you! We'll get back to you shortly.")
    return render(request, 'core/contact.html')
