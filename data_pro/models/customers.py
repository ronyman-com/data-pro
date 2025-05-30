# data_pro/models/customers.py
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from .clients import Client

class Customer(models.Model):
    STATUS_CHOICES = (
        ('active', _('Active')),
        ('inactive', _('Inactive')),
        ('pending', _('Pending')),
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='customer_accounts',
        verbose_name=_('System User')
    )
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='customers',
        verbose_name=_('Client Organization')
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

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = _('Customer')
        verbose_name_plural = _('Customers')
        ordering = ['-created_at']