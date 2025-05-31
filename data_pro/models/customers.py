# data_pro/models/customers.py
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model


class Customer(models.Model):
    client = models.ForeignKey('Client', on_delete=models.CASCADE)
    STATUS_CHOICES = (
        ('active', _('Active')),
        ('inactive', _('Inactive')),
        ('pending', _('Pending')),
    )
    
    client = models.ForeignKey(
        'data_pro.Client',  # Changed from 'clients.Client'
        on_delete=models.CASCADE,
        related_name='customers'
    )


    first_name = models.CharField(_('First Name'), max_length=50)
    last_name = models.CharField(_('Last Name'), max_length=50)
    email = models.EmailField(_('Email'))
    phone = models.CharField(_('Phone'), max_length=20)
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
        if not self.client_id:
            errors['client'] = _('Customer must be associated with a client')
        if not self.office_id:
            errors['office'] = _('Customer must be associated with an office')
        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = _('Customer')
        verbose_name_plural = _('Customers')
        ordering = ['-created_at']