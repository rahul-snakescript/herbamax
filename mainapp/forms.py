from django import forms
from mainapp.models import Order


class CheckoutForm(forms.ModelForm):
    # coupon_code = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Order
        fields = ['email', 's_first_name', 's_last_name', 's_phone', 's_country', 's_address', 's_city', 's_state',
                  's_zip', 'b_first_name', 'b_last_name', 'b_phone', 'b_country', 'b_address', 'b_city',
                  'b_state', 'b_zip']
