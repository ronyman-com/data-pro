from django import forms
from django.forms import ModelForm
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import Q

from data_pro.core.models import Invoice, InvoiceItem, Customer
from data_pro.models import User

class InvoiceForm(ModelForm):
    customer = forms.ModelChoiceField(
        queryset=Customer.objects.none(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True
    )
    issue_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        initial=timezone.now().date()
    )
    due_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        required=True
    )
    status = forms.ChoiceField(
        choices=Invoice.STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        initial='DRAFT'
    )
    notes = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        required=False
    )

    class Meta:
        model = Invoice
        fields = ['customer', 'invoice_number', 'issue_date', 'due_date', 'status', 'notes']
        widgets = {
            'invoice_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Auto-generated if left blank'
            }),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Set customer queryset based on user permissions
        if user:
            if user.user_type == 'CLIENT_ADMIN':
                self.fields['customer'].queryset = Customer.objects.filter(
                    created_by__client=user.client
                )
            else:
                self.fields['customer'].queryset = Customer.objects.all()
        
        # Set initial invoice number if creating new
        if not self.instance.pk:
            last_invoice = Invoice.objects.order_by('-id').first()
            new_number = f"INV-{timezone.now().strftime('%Y%m%d')}-0001"
            if last_invoice:
                try:
                    last_num = int(last_invoice.invoice_number.split('-')[-1])
                    new_number = f"INV-{timezone.now().strftime('%Y%m%d')}-{last_num + 1:04d}"
                except (IndexError, ValueError):
                    pass
            self.initial['invoice_number'] = new_number

    def clean_due_date(self):
        issue_date = self.cleaned_data.get('issue_date')
        due_date = self.cleaned_data.get('due_date')
        
        if issue_date and due_date and due_date < issue_date:
            raise ValidationError("Due date cannot be before issue date")
        return due_date

class InvoiceItemForm(ModelForm):
    description = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Item description'
        }),
        required=True
    )
    quantity = forms.DecimalField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '0.01',
            'step': '0.01'
        }),
        initial=1,
        min_value=0.01
    )
    unit_price = forms.DecimalField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '0.01',
            'step': '0.01'
        }),
        initial=0.00,
        min_value=0.00
    )
    tax_rate = forms.DecimalField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '0',
            'max': '100',
            'step': '0.01'
        }),
        initial=0.00,
        min_value=0.00,
        max_value=100.00,
        required=False
    )

    class Meta:
        model = InvoiceItem
        fields = ['description', 'quantity', 'unit_price', 'tax_rate']
        exclude = ['invoice']

    def clean(self):
        cleaned_data = super().clean()
        quantity = cleaned_data.get('quantity')
        unit_price = cleaned_data.get('unit_price')
        
        if quantity and unit_price:
            if quantity * unit_price <= 0:
                raise ValidationError("Item total must be greater than zero")
        
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.tax_rate:
            instance.tax_rate = 0.00
        
        if commit:
            instance.save()
        return instance