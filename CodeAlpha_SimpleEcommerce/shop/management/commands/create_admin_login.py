import secrets

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create or reset a secure development admin login."

    def handle(self, *args, **options):
        password = secrets.token_urlsafe(12)
        User = get_user_model()
        user, _ = User.objects.get_or_create(
            username="admin",
            defaults={"email": "admin@example.com", "is_staff": True, "is_superuser": True},
        )
        user.email = user.email or "admin@example.com"
        user.is_staff = True
        user.is_superuser = True
        user.set_password(password)
        user.save()
        self.stdout.write("ADMIN_USERNAME=admin")
        self.stdout.write(f"ADMIN_PASSWORD={password}")
