from django.db.models.signals import post_save, pre_save, post_delete, pre_delete
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from data_pro.models.customers import  *
from data_pro.models.visas import  *
from data_pro.models.passports import  *
from data_pro.models.invoices import  *
from data_pro.models.vehicles import  *
from data_pro.models.transports import  *
from data_pro.models.user import *
from django.contrib.auth import get_user_model
User = get_user_model()  # Use Django


# User Signals
@receiver(post_save, sender=CustomUser)
def user_post_save(sender, instance, created, **kwargs):
    """
    Signal for post-save actions on User model.
    - Send welcome email to new users
    - Create related profile if needed
    """
    if created:
        # Send welcome email
        subject = 'Welcome to DataPro'
        message = render_to_string('emails/welcome_email.txt', {
            'user': instance,
        })
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [instance.email],
            fail_silently=True,
        )

        # Log user creation
        print(f"New user created: {instance.username}")

@receiver(pre_save, sender=CustomUser)
def user_pre_save(sender, instance, **kwargs):
    """
    Signal for pre-save actions on User model.
    - Normalize email
    - Set default values
    """
    if not instance.user_type:
        instance.user_type = 'USER'
    instance.email = instance.email.lower()

# Client Signals
@receiver(post_save, sender=Client)
def client_post_save(sender, instance, created, **kwargs):
    """
    Signal for post-save actions on Client model.
    - Create default admin user for new clients
    - Send notification emails
    """
    if created:
        # Create client admin user
        admin_username = f"{instance.company_name.lower().replace(' ', '_')}_admin"
        admin_email = f"admin@{instance.company_name.lower().replace(' ', '')}.com"
        
        admin_user = CustomUser.objects.create_user(
            username=admin_username,
            email=admin_email,
            password=CustomUser.objects.make_random_password(),
            user_type='CLIENT_ADMIN'
        )
        instance.user = admin_user
        instance.save()

@receiver(pre_delete, sender=Client)
def client_pre_delete(sender, instance, **kwargs):
    """
    Signal for pre-delete actions on Client model.
    - Clean up related users
    """
    if instance.user:
        instance.user.delete()

# Customer Signals
@receiver(post_save, sender=Customer)
def customer_post_save(sender, instance, created, **kwargs):
    """
    Signal for post-save actions on Customer model.
    - Send welcome email
    - Create initial records
    """
    if created and instance.email:
        subject = 'Welcome to Our Service'
        message = render_to_string('emails/customer_welcome.txt', {
            'customer': instance,
        })
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [instance.email],
            fail_silently=True,
        )

# Invoice Signals
@receiver(post_save, sender=Invoice)
def invoice_post_save(sender, instance, created, **kwargs):
    """
    Signal for post-save actions on Invoice model.
    - Send invoice email when created
    - Update client balances
    """
    if created and instance.status == 'sent':
        subject = f'New Invoice: {instance.invoice_number}'
        message = render_to_string('emails/new_invoice.txt', {
            'invoice': instance,
        })
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [instance.customer.email],
            fail_silently=True,
        )

@receiver(pre_save, sender=Invoice)
def invoice_pre_save(sender, instance, **kwargs):
    """
    Signal for pre-save actions on Invoice model.
    - Calculate totals
    - Set default values
    """
    if not instance.total_amount:
        instance.total_amount = instance.amount + instance.tax - instance.discount

# Transport Signals
@receiver(post_save, sender=Transport)
def transport_post_save(sender, instance, created, **kwargs):
    """
    Signal for post-save actions on Transport model.
    - Update vehicle status
    - Send notifications
    """
    if created:
        instance.vehicle.status = 'in_use'
        instance.vehicle.save()

@receiver(post_delete, sender=Transport)
def transport_post_delete(sender, instance, **kwargs):
    """
    Signal for post-delete actions on Transport model.
    - Update vehicle status
    """
    instance.vehicle.status = 'available'
    instance.vehicle.save()

# Vehicle Signals
@receiver(pre_save, sender=Vehicle)
def vehicle_pre_save(sender, instance, **kwargs):
    """
    Signal for pre-save actions on Vehicle model.
    - Validate license plate format
    """
    instance.license_plate = instance.license_plate.upper().replace(' ', '')

# Visa Signals
@receiver(post_save, sender=Visa)
def visa_post_save(sender, instance, created, **kwargs):
    """
    Signal for post-save actions on Visa model.
    - Send status update emails
    """
    if instance.status in ['approved', 'rejected'] and instance.customer.email:
        subject = f'Visa Application Update: {instance.get_status_display()}'
        message = render_to_string('emails/visa_status_update.txt', {
            'visa': instance,
        })
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [instance.customer.email],
            fail_silently=True,
        )