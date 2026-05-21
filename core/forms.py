from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile, Customization, PortraitOrder, WeddingEventOrder


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=100, required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=100, required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}))
    email = forms.EmailField(required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm Password'})

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email


class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))


class ProfileUpdateForm(forms.ModelForm):
    first_name = forms.CharField(max_length=100, required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=100, required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control'}))

    class Meta:
        model = UserProfile
        fields = ['phone', 'address_line1', 'address_line2', 'city', 'state', 'pincode']
        widgets = {
            'phone':         forms.TextInput(attrs={'class': 'form-control'}),
            'address_line1': forms.TextInput(attrs={'class': 'form-control'}),
            'address_line2': forms.TextInput(attrs={'class': 'form-control'}),
            'city':          forms.TextInput(attrs={'class': 'form-control'}),
            'state':         forms.TextInput(attrs={'class': 'form-control'}),
            'pincode':       forms.TextInput(attrs={'class': 'form-control'}),
        }


class CustomizationForm(forms.ModelForm):
    class Meta:
        model = Customization
        fields = ['image', 'notes']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/jpeg,image/jpg'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4,
                                           'placeholder': 'Describe your customization...'}),
        }

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image and not image.name.lower().endswith(('.jpg', '.jpeg')):
            raise forms.ValidationError("Only JPG/JPEG images are allowed.")
        return image


class PortraitOrderForm(forms.ModelForm):
    class Meta:
        model = PortraitOrder
        fields = ['name', 'image', 'size', 'special_notes']
        widgets = {
            'name':          forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subject Name'}),
            'image':         forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'size':          forms.Select(attrs={'class': 'form-select', 'id': 'sizeSelect'}),
            'special_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3,
                                                   'placeholder': 'Any special requirements...'}),
        }


class WeddingEventForm(forms.ModelForm):
    class Meta:
        model = WeddingEventOrder
        fields = ['location', 'event_type', 'event_date', 'primary_time', 'optional_time', 'notes']
        widgets = {
            'location':      forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Event Location'}),
            'event_type':    forms.Select(attrs={'class': 'form-select'}),
            'event_date':    forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'primary_time':  forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'optional_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'notes':         forms.Textarea(attrs={'class': 'form-control', 'rows': 3,
                                                   'placeholder': 'Additional notes...'}),
        }


class CheckoutForm(forms.Form):
    address_line1 = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Address Line 1'}))
    address_line2 = forms.CharField(required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Address Line 2 (Optional)'}))
    city = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}))
    state = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'State'}))
    pincode = forms.CharField(max_length=10,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Pincode'}))
    phone = forms.CharField(max_length=15,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}))
    payment_method = forms.ChoiceField(
        choices=[
            ('razorpay', 'Razorpay  (UPI / Card / NetBanking / Wallet)'),
            ('cod',      'Cash on Delivery'),
        ],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        initial='razorpay',
    )
