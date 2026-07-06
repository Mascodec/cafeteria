from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")


class OrderQuantityForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, initial=1)
    payment_method = forms.ChoiceField(
        choices=[("Cash", "Cash"), ("Mpesa", "M-Pesa")],
        widget=forms.RadioSelect,
        initial="Cash",
    )
