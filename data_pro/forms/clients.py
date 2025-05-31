# data_pro/forms/clients.py
from django import forms
from django.contrib.auth import get_user_model
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from data_pro.models.clients import Client
from data_pro.models.office import Office
from django.core.exceptions import ValidationError
from django.apps import apps


User = get_user_model()

class ClientForm(forms.ModelForm):
    # Additional non-model fields for user creation
    username = forms.CharField(
        required=True,
        label="Admin Username",
        help_text="Username for the client admin account",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=True,
        label="Admin Password",
        help_text="Password for the client admin account"
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=True,
        label="Confirm Password"
    )
    admin_email = forms.EmailField(
        required=True,
        label="Admin Email",
        help_text="Email for the client admin account",
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        
        # Get the actual model class
        Client = apps.get_model('data_pro', 'Client')
        Office = apps.get_model('data_pro', 'Office')
        
        # Set up office field
        self.fields['office'].queryset = Office.objects.filter(is_active=True)
        self.fields['office'].required = True
        
        # Set required fields
        required_fields = [
            'company_name', 'contact_person', 'email', 
            'phone', 'address_line1', 'city', 'country'
        ]
        for field in required_fields:
            self.fields[field].required = True

        # For update forms, remove the user creation fields
        if self.instance and self.instance.pk:
            for field in ['username', 'password', 'confirm_password', 'admin_email']:
                if field in self.fields:
                    del self.fields[field]

    class Meta:
        # Don't use string reference here, we'll set the model in __new__
        fields = [
            'company_name',
            'company_reg_number',
            'tax_id',
            'contact_person',
            'email',
            'phone',
            'alternate_phone',
            'website',
            'address_line1',
            'address_line2',
            'city',
            'state',
            'postal_code',
            'country',
            'status',
            'is_verified',
            'notes',
            'office'
        ]
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'is_verified': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'alternate_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'address_line1': forms.TextInput(attrs={'class': 'form-control'}),
            'address_line2': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'office': forms.Select(attrs={'class': 'form-select'}),
        }
        help_texts = {
            'company_reg_number': 'Official business registration number',
            'tax_id': 'Tax identification number',
            'alternate_phone': 'Secondary contact number',
            'office': 'Select the office this client belongs to',
        }

    def __new__(cls, *args, **kwargs):
        # Set the model class when the form is created
        cls.model = apps.get_model('data_pro', 'Client')
        return super().__new__(cls)

    def clean(self):
        cleaned_data = super().clean()
        errors = {}
        
        # Password confirmation check
        if 'password' in self.fields and 'confirm_password' in self.fields:
            if cleaned_data.get('password') != cleaned_data.get('confirm_password'):
                errors['confirm_password'] = "Passwords don't match"

        # Email validation
        if 'email' in cleaned_data and 'admin_email' in cleaned_data:
            if cleaned_data['email'] == cleaned_data['admin_email']:
                errors['admin_email'] = "Admin email should be different from company email"

        # Office validation
        if not cleaned_data.get('office'):
            errors['office'] = "Please select an office for this client"

        if errors:
            raise ValidationError(errors)

        return cleaned_data

    def save(self, commit=True):
        client = super().save(commit=False)
        
        # Only create user for new clients
        if not client.pk and all(field in self.cleaned_data for field in ['username', 'admin_email', 'password']):
            user = User.objects.create_user(
                username=self.cleaned_data['username'],
                email=self.cleaned_data['admin_email'],
                password=self.cleaned_data['password'],
                user_type='client_admin'
            )
            client.user = user

        if commit:
            client.save()
            self.save_m2m()
        
        return client