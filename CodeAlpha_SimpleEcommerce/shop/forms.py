from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth.models import User

from .models import ContactMessage, Order, ProductReview, UserProfile


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(
        required=True,
        max_length=30,
        widget=forms.TextInput(attrs={"placeholder": "Phone number"}),
    )

    class Meta:
        model = User
        fields = ("first_name", "last_name", "username", "email", "phone", "password1", "password2")
        widgets = {
            "first_name": forms.TextInput(attrs={"placeholder": "First name"}),
            "last_name": forms.TextInput(attrs={"placeholder": "Last name"}),
            "username": forms.TextInput(attrs={"placeholder": "Username"}),
            "email": forms.EmailInput(attrs={"placeholder": "Email address", "data-register-email": ""}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].widget.attrs.update({"placeholder": "Password", "data-register-password": ""})
        self.fields["password2"].widget.attrs.update({"placeholder": "Confirm password", "data-register-confirm": ""})


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")


class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ("phone", "address", "city")


class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ("full_name", "email", "phone", "country", "city", "address", "payment_method")
        widgets = {"address": forms.Textarea(attrs={"rows": 3})}


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ("name", "email", "subject", "message")
        widgets = {"message": forms.Textarea(attrs={"rows": 5})}


class ReviewForm(forms.ModelForm):
    class Meta:
        model = ProductReview
        fields = ("rating", "comment")
        widgets = {
            "rating": forms.Select(choices=[(value, f"{value} star{'s' if value > 1 else ''}") for value in range(1, 6)]),
            "comment": forms.Textarea(attrs={"rows": 4, "placeholder": "Share your experience with this product"}),
        }
