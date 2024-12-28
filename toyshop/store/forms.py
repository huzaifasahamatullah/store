from django import forms
from .models import Order

class PlaceOrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['user_name', 'user_email', 'user_address', 'user_phone']
        widgets = {
            'user_address': forms.Textarea(attrs={'rows': 3}),
        }
