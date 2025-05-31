# data_pro/forms/customers.py
from django import forms
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.apps import apps
from django.core.exceptions import ValidationError
from data_pro.models.customers import *
from data_pro.models.clients import *


User = get_user_model()

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['first_name', 'last_name', 'email', 'phone', 'client']
        
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        
        # Limit client choices for non-superusers
        if self.request and not self.request.user.is_superuser:
            if hasattr(self.request.user, 'profile') and self.request.user.profile.client:
                self.fields['client'].queryset = Customer.objects.filter(id=self.request.user.profile.client.id)
                self.fields['client'].initial = self.request.user.profile.client
                self.fields['client'].disabled = True

    @classmethod
    def _get_meta_class(cls):
        # Create Meta class dynamically after models are loaded
        class Meta:
            fields = ['first_name', 'last_name', 'email', 'phone', 'status', 'client', 'office']
            widgets = {
                'status': forms.Select(attrs={'class': 'form-select'}),
                'client': forms.Select(attrs={
                    'class': 'form-select',
                    'data-create-org-url': reverse_lazy('data_pro:client-quick-create')
                }),
                'office': forms.Select(attrs={'class': 'form-select'}),
                'user': forms.Select(attrs={'class': 'form-select'}),
            }
        return Meta

    def clean(self):
        cleaned_data = super().clean()
        errors = {}
        
        create_new = cleaned_data.get('create_new_organization')
        new_name = cleaned_data.get('new_organization_name')
        client = cleaned_data.get('client')


        # Validate organization selection/creation
        if not client and not create_new:
            errors['client'] = _("Please select an existing organization or choose to create a new one.")
        
        if create_new and not new_name:
            errors['new_organization_name'] = _("Organization name is required when creating new organization")
        
        # Validate office is selected
        if not office:
            errors['office'] = _("Please select an office for this customer")
        
        if errors:
            raise ValidationError(errors)

        return cleaned_data

    def save(self, commit=True):
        # Get models using apps registry
        Client = apps.get_model('data_pro', 'Client')
        
        customer = super().save(commit=False)
        create_new = self.cleaned_data.get('create_new_organization')
        new_name = self.cleaned_data.get('new_organization_name')
        office = self.cleaned_data.get('office')

        # Create new organization if requested
        if create_new and new_name and office:
            client = Client.objects.create(
                company_name=new_name,
                contact_person=f"{self.cleaned_data['first_name']} {self.cleaned_data['last_name']}",
                email=self.cleaned_data['email'],
                phone=self.cleaned_data['phone'],
                status='active',
                office=office  # Assign the selected office to new client
            )
            customer.client = client

        if commit:
            customer.save()
            self.save_m2m()
          
        return customer

# Set the model after the class is defined
CustomerForm.model = apps.get_model('data_pro', 'Customer')
CustomerForm.Meta = CustomerForm._get_meta_class()