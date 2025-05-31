# data_pro/models/office.py
from django.db import models
from django.utils.translation import gettext_lazy as _

class Office(models.Model):
    name = models.CharField(_('Office Name'), max_length=100)
    address = models.TextField(_('Address'))
    phone = models.CharField(_('Phone'), max_length=20)
    email = models.EmailField(_('Email'))
    is_active = models.BooleanField(_('Active'), default=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Office')
        verbose_name_plural = _('Offices')
        ordering = ['name']