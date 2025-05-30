# data_pro/models/clients.py
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

class Client(models.Model):
    USER_TYPE_CHOICES = (
        ('admin', _('Admin')),
        ('manager', _('Manager')),
        ('staff', _('Staff')),
        ('client_admin', _('Client Admin')),
    )
    
    STATUS_CHOICES = (
        ('active', _('Active')),
        ('inactive', _('Inactive')),
        ('pending', _('Pending')),
    )
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='client_account'
    )
    user_type = models.CharField(
        _('User Type'),
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default='staff'
    )
    status = models.CharField(
        _('Status'),
        max_length=10,
        choices=STATUS_CHOICES,
        default='active'
    )
    company_name = models.CharField(_('Company Name'), max_length=100)
    contact_person = models.CharField(_('Contact Person'), max_length=100)
    email = models.EmailField(_('Email'))
    phone = models.CharField(_('Phone'), max_length=20)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    def __str__(self):
        return self.company_name

    class Meta:
        verbose_name = _('Client')
        verbose_name_plural = _('Clients')
        ordering = ['-created_at']