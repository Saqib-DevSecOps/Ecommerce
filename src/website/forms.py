from django import forms

from src.website.models import Order


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name',
                  'last_name',
                  'phone',
                  'email',
                  'address_line_1',
                  'address_line_2',
                  'country',
                  'city',
                  'state',
                  'order_note',
                  ]