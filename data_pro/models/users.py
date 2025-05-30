# data_pro/models/users.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    class UserType(models.TextChoices):
        ADMIN = 'admin', _('Admin')
        MANAGER = 'manager', _('Manager')
        STAFF = 'staff', _('Staff')
        CLIENT_ADMIN = 'client_admin', _('Client Admin')
        CUSTOMER = 'customer', _('Customer')
    
    user_type = models.CharField(
        max_length=20,
        choices=UserType.choices,
        default=UserType.STAFF
    )
    phone = models.CharField(_('Phone'), max_length=20, blank=True)
    
    # Add custom related_name to avoid clashes
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name=_('groups'),
        blank=True,
        help_text=_('The groups this user belongs to.'),
        related_name="data_pro_user_set",
        related_query_name="data_pro_user",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name="data_pro_user_set",
        related_query_name="data_pro_user",
    )

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
    
    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_user_type_display()})"