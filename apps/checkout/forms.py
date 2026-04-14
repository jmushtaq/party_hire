from django import forms
from apps.bookings.models import Booking

class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['customer_name', 'customer_email', 'customer_phone', 'customer_address', 'notes']
        widgets = {
            'customer_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
            'customer_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}),
            'customer_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'customer_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Delivery Address'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Special Requests (Optional)'}),
        }
