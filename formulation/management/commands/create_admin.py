from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = "Create or reset admin user"

    def handle(self, *args, **kwargs):
        username = "admin"
        password = "Admin@12345"
        email = "admin@example.com"

        user, created = User.objects.get_or_create(username=username)

        user.email = email
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.set_password(password)
        user.save()

        self.stdout.write(self.style.SUCCESS("Admin user is ready."))