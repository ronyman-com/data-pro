from django import forms
from django.utils.translation import gettext_lazy as _
from data_pro.models.visas import *
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth import get_user_model


User = get_user_model()

class VisaForm(forms.ModelForm):
    handed_by = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=False,
        label=_('Handed By'),
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Visa
        fields = [
            'customer',
            'visa_number',
            'visa_type',
            'issuing_country',
            'issue_date',
            'expiry_date',
            'duration_days',
            'entry_type',
            'status',
            'unit_cost',
            'service_fee',
            'released_date',
            'handed_by',
            'picked_by',
            'notes'
        ]
        widgets = {
            'issue_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'expiry_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'released_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'notes': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control'
            }),
            'customer': forms.Select(attrs={
                'class': 'form-select'
            }),
            'visa_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'entry_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'handed_by': forms.Select(attrs={
                'class': 'form-select',
                'disabled': 'disabled'  # Make field read-only
            }),
            'visa_number': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'issuing_country': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'duration_days': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1
            }),
            'unit_cost': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'service_fee': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'picked_by': forms.TextInput(attrs={
                'class': 'form-control'
            })
        }
        labels = {
            'visa_number': _('Visa Number'),
            'issuing_country': _('Issuing Country'),
            'issue_date': _('Issue Date'),
            'expiry_date': _('Expiry Date'),
            'duration_days': _('Duration (Days)'),
            'unit_cost': _('Unit Cost (USD)'),
            'service_fee': _('Service Fee (USD)'),
            'released_date': _('Released Date'),
            'handed_by': _('Handed By'),
            'picked_by': _('Picked By')
        }


        

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user = kwargs.pop('user', None)  # Get the current user from kwargs
        # Filter handed_by choices to staff users only
        self.fields['handed_by'].queryset = User.objects.filter(is_staff=True)
        
        # Set initial handed_by to current user if creating new visa
        if user and not self.instance.pk and 'handed_by' not in self.data:
            self.fields['handed_by'].initial = user
        
        # Set required fields
        self.fields['visa_number'].required = True
        self.fields['issuing_country'].required = True
        self.fields['issue_date'].required = True
        self.fields['expiry_date'].required = True
        self.fields['duration_days'].required = True
        self.fields['unit_cost'].required = True
        
        # Set initial values if creating new
        if not self.instance.pk:
            self.fields['status'].initial = 'processing'
            self.fields['service_fee'].initial = 0.00

    def clean(self):
        cleaned_data = super().clean()
        issue_date = cleaned_data.get('issue_date')
        expiry_date = cleaned_data.get('expiry_date')
        released_date = cleaned_data.get('released_date')
        status = cleaned_data.get('status')
        duration_days = cleaned_data.get('duration_days')

        # Validate date consistency
        if issue_date and expiry_date:
            if issue_date > expiry_date:
                raise ValidationError(_('Expiry date must be after issue date'))
            
            calculated_duration = (expiry_date - issue_date).days
            if duration_days and duration_days != calculated_duration:
                raise ValidationError(
                    _('Duration days (%(duration)s) does not match date range (%(calc_duration)s days)'),
                    params={
                        'duration': duration_days,
                        'calc_duration': calculated_duration
                    }
                )

        # Validate released date
        if released_date:
            if status == 'processing':
                raise ValidationError(_('Cannot set released date when status is "Processing"'))
            if issue_date and released_date < issue_date:
                raise ValidationError(_('Released date cannot be before issue date'))

        return cleaned_data

    def clean_visa_number(self):
        visa_number = self.cleaned_data['visa_number']
        if Visa.objects.filter(visa_number=visa_number).exclude(pk=self.instance.pk).exists():
            raise ValidationError(_('A visa with this number already exists'))
        return visa_number

    def clean_unit_cost(self):
        unit_cost = self.cleaned_data['unit_cost']
        if unit_cost < 0:
            raise ValidationError(_('Unit cost cannot be negative'))
        return unit_cost

    def clean_service_fee(self):
        service_fee = self.cleaned_data['service_fee']
        if service_fee < 0:
            raise ValidationError(_('Service fee cannot be negative'))
        return service_fee