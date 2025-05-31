# data_pro/models/customers.py
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model



class Customer(models.Model):
    CUSTOMER_TYPE_CHOICES = (
        ('individual', _('Individual')),
        ('organization', _('Organization')),
    )

    STATUS_CHOICES = (
        ('active', _('Active')),
        ('inactive', _('Inactive')),
        ('pending', _('Pending')),
    )

    client = models.ForeignKey(
        'data_pro.Client',
        on_delete=models.CASCADE,
        related_name='customers',
        verbose_name=_('Client Organization')
    )
    customer_type = models.CharField(
        _('Customer Type'),
        max_length=20,
        choices=CUSTOMER_TYPE_CHOICES,
        default='individual'
    )
    office = models.ForeignKey(
        'data_pro.Office',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('Office (for organizations)')
    )
    first_name = models.CharField(_('First Name'), max_length=50, blank=True, null=True)
    last_name = models.CharField(_('Last Name'), max_length=50, blank=True, null=True)
    organization_name = models.CharField(_('Organization Name'), max_length=100, blank=True, null=True)
    email = models.EmailField(_('Email'), blank=True, null=True)
    phone = models.CharField(_('Phone'), max_length=20)
    nationality = models.CharField(_('Nationality'), max_length=100, blank=True, null=True)
    status = models.CharField(
        _('Status'),
        max_length=10,
        choices=STATUS_CHOICES,
        default='active'
    )
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    def clean(self):
        errors = {}
        
        # Validate based on customer type
        if self.customer_type == 'individual':
            if not self.first_name:
                errors['first_name'] = _('First name is required for individuals')
            if not self.last_name:
                errors['last_name'] = _('Last name is required for individuals')
        else:  # organization
            if not self.organization_name:
                errors['organization_name'] = _('Organization name is required')
            if not self.office:
                errors['office'] = _('Office is required for organizations')
        
        if errors:
            raise ValidationError(errors)

    @property
    def name(self):
        if self.customer_type == 'individual':
            return f"{self.first_name} {self.last_name}"
        return self.organization_name

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Customer')
        verbose_name_plural = _('Customers')
        ordering = ['-created_at']