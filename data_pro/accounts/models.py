from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('SUPERADMIN', 'Super Admin'),
        ('CLIENT_ADMIN', 'Client Admin'),
        ('CUSTOMER', 'Customer'),
    )
    
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    client = models.ForeignKey('Client', on_delete=models.CASCADE, null=True, blank=True)
    phone = models.CharField(max_length=20)
    is_visible = models.BooleanField(default=True)
    
    # Custom related_names to avoid clash with auth.User
    groups = models.ManyToManyField(
        Group,
        verbose_name=_('groups'),
        blank=True,
        help_text=_('The groups this user belongs to.'),
        related_name='data_pro_user_groups',
        related_query_name='data_pro_user',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name='data_pro_user_permissions',
        related_query_name='data_pro_user',
    )
    
    def save(self, *args, **kwargs):
        if self.user_type == 'SUPERADMIN':
            self.is_visible = False
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'data_pro_users'  # Custom table name to avoid conflict

class Client(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    contact_email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name