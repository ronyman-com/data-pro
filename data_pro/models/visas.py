from django.db import models
from django.utils.translation import gettext_lazy as _
from .customers import Customer
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.conf import settings



class Visa(models.Model):
    class VisaType(models.TextChoices):
        TOURIST = 'tourist', _('Tourist')
        BUSINESS = 'business', _('Business')
        STUDENT = 'student', _('Student')
        WORK = 'work', _('Work')
        TRANSIT = 'transit', _('Transit')
        DIPLOMATIC = 'diplomatic', _('Diplomatic')

    class Status(models.TextChoices):
        PROCESSING = 'processing', _('Processing')
        APPROVED = 'approved', _('Approved')
        REJECTED = 'rejected', _('Rejected')
        ISSUED = 'issued', _('Issued')
        EXPIRED = 'expired', _('Expired')
        RELEASED = 'released', _('Released')

    customer = models.ForeignKey(
        Customer, 
        on_delete=models.CASCADE, 
        related_name='visas',
        verbose_name=_('Customer')
    )
    visa_number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_('Visa Number')
    )
    visa_type = models.CharField(
        max_length=20,
        choices=VisaType.choices,
        default=VisaType.TOURIST,
        verbose_name=_('Visa Type')
    )
    issuing_country = models.CharField(
        max_length=100,
        verbose_name=_('Issuing Country')
    )
    issue_date = models.DateField(
        verbose_name=_('Issue Date')
    )
    expiry_date = models.DateField(
        verbose_name=_('Expiry Date')
    )
    duration_days = models.PositiveIntegerField(
        verbose_name=_('Duration (Days)')
    )
    entry_type = models.CharField(
        max_length=20,
        choices=[
            ('single', _('Single Entry')),
            ('multiple', _('Multiple Entry'))
        ],
        default='single',
        verbose_name=_('Entry Type')
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PROCESSING,
        verbose_name=_('Status')
    )
    unit_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name=_('Unit Cost (USD)')
    )
    service_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        default=0,
        verbose_name=_('Service Fee (USD)')
    )
    total_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name=_('Total Cost (USD)')
    )
    released_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Released Date')
    )
    handed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='handed_visas',
        verbose_name=_('Handed By')
    )

    def save(self, *args, **kwargs):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Auto-set handed_by if not set and we have request in kwargs
        request = kwargs.pop('request', None)
        if request and not self.handed_by and request.user.is_authenticated:
            if request.user.is_staff or request.user.is_superuser:
                self.handed_by = request.user
                
        super().save(*args, **kwargs)

    picked_by = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('Picked By')
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Notes')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created At')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Updated At')
    )

    def __str__(self):
        return f"{self.visa_number} - {self.get_visa_type_display()} ({self.issuing_country})"

    def save(self, *args, **kwargs):
        # Calculate total cost before saving
        self.total_cost = self.unit_cost + self.service_fee
        
        # Update status based on dates
        if self.expiry_date and self.expiry_date < timezone.now().date():
            self.status = self.Status.EXPIRED
        elif self.released_date and self.status != self.Status.RELEASED:
            self.status = self.Status.RELEASED
            
        super().save(*args, **kwargs)

    @property
    def is_valid(self):
        return self.status in [self.Status.ISSUED, self.Status.RELEASED] and \
               self.expiry_date >= timezone.now().date()

    @property
    def days_remaining(self):
        if self.expiry_date:
            return (self.expiry_date - timezone.now().date()).days
        return None

    class Meta:
        verbose_name = _('Visa')
        verbose_name_plural = _('Visas')
        ordering = ['-issue_date']
        indexes = [
            models.Index(fields=['visa_number']),
            models.Index(fields=['customer']),
            models.Index(fields=['status']),
            models.Index(fields=['expiry_date']),
        ]