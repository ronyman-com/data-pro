from django import forms
from data_pro.models.customers import Customer

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['first_name', 'last_name', 'email', 'phone', 'address', 'status']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }