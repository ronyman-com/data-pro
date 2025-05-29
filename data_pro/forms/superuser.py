from django import forms
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class SuperUserCreationForm(forms.ModelForm):
    """Form for superadmins to create new users with all privileges"""
    password1 = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        strip=False,
    )
    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        strip=False,
    )

    class Meta:
        model = User
        fields = [
            'username', 'email', 'user_type', 'client', 
            'first_name', 'last_name', 'phone', 'is_active'
        ]
        widgets = {
            'user_type': forms.Select(attrs={'class': 'form-select'}),
            'client': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError(_("Passwords don't match"))
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class SuperUserEditForm(UserChangeForm):
    """Form for superadmins to edit any user with all fields"""
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'user_type', 'client',
            'first_name', 'last_name', 'phone', 'is_active',
            'is_staff', 'is_superuser', 'groups', 'user_permissions'
        ]
        widgets = {
            'user_type': forms.Select(attrs={'class': 'form-select'}),
            'client': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove password field from the form
        self.fields.pop('password', None)

class ClientAdminCreationForm(forms.ModelForm):
    """Form for creating client admin users with limited privileges"""
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'client', 
            'first_name', 'last_name', 'phone'
        ]
        widgets = {
            'client': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set user_type to CLIENT_ADMIN by default
        self.initial['user_type'] = 'CLIENT_ADMIN'
        self.fields['user_type'] = forms.CharField(
            widget=forms.HiddenInput(),
            initial='CLIENT_ADMIN'
        )

class SystemSettingsForm(forms.Form):
    """Form for system-wide configuration"""
    site_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    maintenance_mode = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    session_timeout = forms.IntegerField(
        min_value=5,
        max_value=1440,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        help_text=_("Session timeout in minutes (5-1440)")
    )

class BulkUserImportForm(forms.Form):
    """Form for bulk user import"""
    csv_file = forms.FileField(
        label=_("CSV File"),
        help_text=_("CSV file containing user data with headers: username,email,first_name,last_name,user_type,client")
    )
    send_welcome_email = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )