from django.db import models
from django.contrib.auth import get_user_model
from .customers import Customer
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class Passport(models.Model):
    STATUS_CHOICES = (
        ('valid', 'Valid'),
        ('expired', 'Expired'),
        ('lost', 'Lost/Stolen'),
        ('in_process', 'In Process'),
    )
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='passports')
    passport_number = models.CharField(max_length=50, unique=True)
    issuing_country = models.CharField(max_length=100)
    issue_date = models.DateField()
    expiry_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='valid')
    scanned_copy = models.FileField(upload_to='passports/', blank=True, null=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_passports')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-expiry_date']
        verbose_name = _('Passport')
        verbose_name_plural = _('Passports')

    def __str__(self):
        return f"{self.passport_number} ({self.issuing_country})"

    @property
    def is_expired(self):
        from django.utils import timezone
        return self.expiry_date < timezone.now().date()


class PassportExtension(models.Model):
    DURATION_CHOICES = (
        (1, _('1 Month')),
        (3, _('3 Months')),
        (6, _('6 Months')),
        (12, _('1 Year')),
        (24, _('2 Years')),
    )

    passport = models.ForeignKey(Passport, on_delete=models.CASCADE, related_name='extensions')
    duration = models.PositiveSmallIntegerField(choices=DURATION_CHOICES, default=6)
    cost = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    apply_date = models.DateField()
    released_date = models.DateField(null=True, blank=True)
    picked_by = models.CharField(max_length=100, blank=True)
    handed_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        limit_choices_to={'user_type__in': ['CLIENT_ADMIN', 'SUPERADMIN']},
        related_name='handed_extensions'
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-apply_date']
        verbose_name = _('Passport Extension')
        verbose_name_plural = _('Passport Extensions')

    def __str__(self):
        return f"Extension for {self.passport.passport_number} ({self.get_duration_display()})"

    @property
    def is_completed(self):
        return self.released_date is not None

    def save(self, *args, **kwargs):
        if self.released_date and not self.passport.status == 'valid':
            self.passport.status = 'valid'
            self.passport.save()
        super().save(*args, **kwargs)