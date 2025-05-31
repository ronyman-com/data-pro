# data_pro/models/clients.py
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError


User = get_user_model()

class Client(models.Model):
    name = models.CharField(max_length=100)
    class UserType(models.TextChoices):
        ADMIN = 'admin', _('Admin')
        MANAGER = 'manager', _('Manager')
        STAFF = 'staff', _('Staff')
        CLIENT_ADMIN = 'client_admin', _('Client Admin')
    
    class StatusChoices(models.TextChoices):
        ACTIVE = 'active', _('Active')
        INACTIVE = 'inactive', _('Inactive')
        PENDING = 'pending', _('Pending')
        SUSPENDED = 'suspended', _('Suspended')

    # Relationships

    # Company Information
    company_name = models.CharField(
        _('Company Name'),
        max_length=100,
        unique=True,
        help_text=_('Official registered company name')
    )
    company_reg_number = models.CharField(
        _('Registration Number'),
        max_length=50,
        blank=True,
        null=True
    )
    tax_id = models.CharField(
        _('Tax ID'),
        max_length=50,
        blank=True,
        null=True
    )

    # Contact Information
    contact_person = models.CharField(
        _('Contact Person'),
        max_length=100,
        help_text=_('Primary contact for this client')
    )
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message=_("Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    )
    phone = models.CharField(
        _('Phone'),
        validators=[phone_regex],
        max_length=17
    )
    alternate_phone = models.CharField(
        _('Alternate Phone'),
        validators=[phone_regex],
        max_length=17,
        blank=True,
        null=True
    )
    email = models.EmailField(
        _('Email'),
        unique=True,
        help_text=_('Primary contact email')
    )
    website = models.URLField(
        _('Website'),
        blank=True,
        null=True
    )

    # Address Information
    address_line1 = models.CharField(
        _('Address Line 1'),
        max_length=255
    )
    address_line2 = models.CharField(
        _('Address Line 2'),
        max_length=255,
        blank=True,
        null=True
    )
    city = models.CharField(
        _('City'),
        max_length=100
    )
    state = models.CharField(
        _('State/Province'),
        max_length=100
    )
    postal_code = models.CharField(
        _('Postal Code'),
        max_length=20
    )
    country = models.CharField(
        _('Country'),
        max_length=100,
        default='United States'
    )

    # Status and Metadata
    status = models.CharField(
        _('Status'),
        max_length=10,
        choices=StatusChoices.choices,
        default=StatusChoices.ACTIVE
    )
    is_verified = models.BooleanField(
        _('Verified'),
        default=False,
        help_text=_('Designates whether the client has been verified')
    )
    notes = models.TextField(
        _('Notes'),
        blank=True,
        null=True,
        help_text=_('Internal notes about this client')
    )
    created_at = models.DateTimeField(
        _('Created At'),
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        _('Updated At'),
        auto_now=True
    )

    def __str__(self):
        return self.company_name

    def clean(self):
        """Validate that the user has the correct user_type"""
        if self.user and self.user.user_type != 'client_admin':
            raise ValidationError(
                {'user': 'Associated user must be a client admin'}
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def full_address(self):
        """Return formatted address string"""
        parts = [
            self.address_line1,
            self.address_line2,
            f"{self.city}, {self.state} {self.postal_code}",
            self.country
        ]
        return ', '.join(filter(None, parts))

    class Meta:
        verbose_name = _('Client')
        verbose_name_plural = _('Clients')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['company_name']),
            models.Index(fields=['email']),
            models.Index(fields=['status']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['company_name', 'email'],
                name='unique_client_company_email'
            )
        ]