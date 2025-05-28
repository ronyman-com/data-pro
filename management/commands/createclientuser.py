# data_pro/management/commands/createclientuser.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from data_pro.models import Client

class Command(BaseCommand):
    help = 'Creates a new client admin user'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str)
        parser.add_argument('email', type=str)
        parser.add_argument('password', type=str)
        parser.add_argument('--client', type=int, help='Client ID')

    def handle(self, *args, **options):
        User = get_user_model()
        
        user = User.objects.create_user(
            username=options['username'],
            email=options['email'],
            password=options['password'],
            user_type='CLIENT_ADMIN'
        )
        
        if options['client']:
            try:
                client = Client.objects.get(pk=options['client'])
                user.client = client
                user.save()
            except Client.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"Client with ID {options['client']} not found"))
        
        self.stdout.write(self.style.SUCCESS(f"Created client admin user {user.username}"))