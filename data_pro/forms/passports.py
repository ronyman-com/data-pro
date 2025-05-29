from django import forms
from django.contrib.auth import get_user_model
from data_pro.models.passports import *
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class PassportForm(forms.ModelForm):
    class Meta:
        model = Passport
        fields = [
            'customer',
            'passport_number',
            'issuing_country',
            'issue_date',
            'expiry_date',
            'status',
            'scanned_copy',
            'notes'
        ]
        widgets = {
            'issue_date': forms.DateInput(attrs={'type': 'date'}),
            'expiry_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        
        if not (self.request.user.is_superuser or self.request.user.user_type == 'SUPERADMIN'):
            self.fields['customer'].queryset = self.fields['customer'].queryset.filter(
                client=self.request.user.client
            )

    def clean_expiry_date(self):
        expiry_date = self.cleaned_data['expiry_date']
        if expiry_date <= timezone.now().date():
            raise ValidationError(_("Expiry date must be in the future"))
        return expiry_date

    def clean_passport_number(self):
        passport_number = self.cleaned_data['passport_number']
        if Passport.objects.filter(passport_number=passport_number).exists():
            if not self.instance or self.instance.passport_number != passport_number:
                raise ValidationError(_("Passport number already exists"))
        return passport_number


class PassportExtensionForm(forms.ModelForm):
    class Meta:
        model = PassportExtension
        fields = [
            'passport',
            'duration',
            'cost',
            'apply_date',
            'released_date',
            'picked_by',
            'handed_by',
            'notes'
        ]
        widgets = {
            'apply_date': forms.DateInput(attrs={'type': 'date'}),
            'released_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        
        if self.request:
            # Limit passport choices to valid passports for the client
            if not (self.request.user.is_superuser or self.request.user.user_type == 'SUPERADMIN'):
                self.fields['passport'].queryset = Passport.objects.filter(
                    customer__client=self.request.user.client,
                    status__in=['valid', 'expired']
                )
                self.fields['handed_by'].queryset = User.objects.filter(
                    client=self.request.user.client,
                    user_type='CLIENT_ADMIN'
                )
            else:
                self.fields['handed_by'].queryset = User.objects.filter(
                    user_type__in=['CLIENT_ADMIN', 'SUPERADMIN']
                )

    def clean(self):
        cleaned_data = super().clean()
        apply_date = cleaned_data.get('apply_date')
        released_date = cleaned_data.get('released_date')
        
        if released_date and apply_date and released_date < apply_date:
            raise ValidationError(_("Released date cannot be before apply date"))
        
        return cleaned_data