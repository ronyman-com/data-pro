# data_pro/forms/customers.py
from django import forms
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.apps import apps
from django.core.exceptions import ValidationError
from data_pro.models.customers import *
from data_pro.models.clients import *
from data_pro.models.passports import *
from django_countries.fields import CountryField
from django_countries import countries



User = get_user_model()



class CustomerForm(forms.ModelForm):
    nationality = forms.ChoiceField(
        choices=countries,
        label=_('Nationality'),
        required=False
    )
    passports = forms.ModelMultipleChoiceField(
        queryset=Passport.objects.none(),
        widget=forms.SelectMultiple(attrs={'class': 'form-select'}),
        required=False,
        label=_('Associated Passports')
    )

    class Meta:
        model = Customer
        fields = [
            'customer_type', 'office', 'first_name', 'last_name',
            'organization_name', 'email', 'phone', 'nationality', 'status'
        ]
        widgets = {
            'customer_type': forms.Select(attrs={
                'class': 'form-select',
                'onchange': 'toggleCustomerFields(this.value)'
            }),
            'office': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        # Limit office choices to the client's offices
        if self.request and hasattr(self.request.user, 'client'):
            self.fields['office'].queryset = self.request.user.client.offices.all()
        
        # Set initial passports if editing existing customer
        if self.instance.pk:
            self.fields['passports'].initial = self.instance.passports.all()
        
        # Set passports queryset to client's passports
        if self.request and hasattr(self.request.user, 'client'):
            self.fields['passports'].queryset = Passport.objects.filter(
                customer__client=self.request.user.client
            )

    def save(self, commit=True):
        customer = super().save(commit=False)
        
        if commit:
            customer.save()
            self.save_m2m()
            if 'passports' in self.cleaned_data:
                customer.passports.set(self.cleaned_data['passports'])
        
        return customer