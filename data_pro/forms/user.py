from django import forms
from django.contrib.auth.forms import (
    UserCreationForm,
    UserChangeForm,
    PasswordChangeForm,
    PasswordResetForm,
    SetPasswordForm
)
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    """Form for creating new users with custom fields"""
    
    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'user_type',
            'client',
            'first_name',
            'last_name',
            'phone'
        )
        widgets = {
            'user_type': forms.Select(attrs={'class': 'form-select'}),
            'client': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make client field optional for superadmins
        if 'user_type' in self.fields and 'client' in self.fields:
            self.fields['client'].required = False

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError(_("A user with that email already exists."))
        return email

class CustomUserChangeForm(UserChangeForm):
    """Form for updating user information"""
    
    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'user_type',
            'client',
            'first_name',
            'last_name',
            'phone',
            'is_active',
            'is_staff',
            'is_superuser',
            'groups',
            'user_permissions'
        )
        widgets = {
            'user_type': forms.Select(attrs={'class': 'form-select'}),
            'client': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove password field from the form
        self.fields.pop('password', None)
        
        # Limit client choices for non-superadmins
        if not (self.instance.is_superuser or self.instance.user_type == 'SUPERADMIN'):
            self.fields['client'].queryset = User.objects.filter(
                pk=self.instance.client.pk
            ) if self.instance.client else User.objects.none()

class CustomPasswordChangeForm(PasswordChangeForm):
    """Custom password change form with Bootstrap styling"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

class CustomPasswordResetForm(PasswordResetForm):
    """Custom password reset form with email validation"""
    
    email = forms.EmailField(
        label=_("Email"),
        max_length=254,
        widget=forms.EmailInput(attrs={
            'autocomplete': 'email',
            'class': 'form-control',
            'placeholder': _('Enter your email address')
        })
    )

    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email__iexact=email, is_active=True).exists():
            raise ValidationError(_("There is no user registered with this email address."))
        return email

class CustomSetPasswordForm(SetPasswordForm):
    """Custom set password form with strength validation"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

    def clean_new_password2(self):
        password = super().clean_new_password2()
        # Add custom password validation here if needed
        if len(password) < 8:
            raise ValidationError(_("Password must be at least 8 characters long."))
        return password

class UserProfileForm(forms.ModelForm):
    """Form for users to edit their own profile"""
    
    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'email',
            'phone',
            'profile_picture'
        )
        widgets = {
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True