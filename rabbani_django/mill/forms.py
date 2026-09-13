from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .constants import CITIES
from .models import Order, ContactMessage


class RegisterForm(UserCreationForm):
    full_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Full name'}))
    phone = forms.CharField(max_length=20, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': '03XX-XXXXXXX'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control', 'placeholder': 'you@example.com'}))
    city = forms.ChoiceField(choices=[(c, c) for c in CITIES], widget=forms.Select(attrs={'class': 'form-select'}))

    class Meta:
        model = User
        fields = ['full_name', 'email', 'phone', 'city', 'username', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Choose a username'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm password'})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        full_name = self.cleaned_data['full_name'].strip()
        parts = full_name.split(' ', 1)
        user.first_name = parts[0]
        user.last_name = parts[1] if len(parts) > 1 else ''
        if commit:
            user.save()
        return user


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['product', 'weight_kg', 'destination_city', 'delivery_address', 'phone']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select'}),
            'weight_kg': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'step': '0.5'}),
            'destination_city': forms.Select(attrs={'class': 'form-select'}),
            'delivery_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'House / street details'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '03XX-XXXXXXX'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product'].queryset = self.fields['product'].queryset.filter(is_available=True)


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'phone', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full name'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone number'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'How can we help?'}),
        }
