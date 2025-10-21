import os
import time
from django.core.management.base import BaseCommand
from auth_app.models import User, Role
from django.utils import timezone


class Command(BaseCommand):
    help = "Creates the Root role and Root user from environment variables"

    def handle(self, *args, **options):
        # 1️⃣ Read values from environment variables
        root_email = os.getenv("ROOT_EMAIL") or "root@gmail.com"
        root_password = os.getenv("ROOT_PASSWORD") or "1234"

        first_name = "Root"
        last_name = "User"

        self.stdout.write(self.style.WARNING("Creating Root role..."))

        # 2️⃣ Create Root Role
        root_role, role_created = Role.objects.get_or_create(
            name="Root",
            defaults={
                "description": "Root role with full system access",
                "permissions": [
                    {
                        "slug": "system.root",
                        "name": "Root Role - Full Permissions",
                        "description": "This role has unrestricted access to the system.",
                        "category": "system",
                        "request_method": "*"
                    },
                ],
                "is_system": True,
                "is_super_admin": True,
                "created_at": timezone.now(),
                "updated_at": timezone.now(),
            }
        )

        # 3️⃣ Simple progress indicator
        for i in range(0, 101, 20):
            self.stdout.write(f"\rProgress: [{'=' * (i // 5)}{' ' * (20 - i // 5)}] {i}%", ending="\r")
            time.sleep(0.2)
        self.stdout.write("\n")

        if role_created:
            self.stdout.write(self.style.SUCCESS("✅ Root role created successfully!"))
        else:
            self.stdout.write(self.style.WARNING("⚠️ Root role already exists."))

        # 4️⃣ Create Root User
        if not User.objects.filter(email=root_email).exists():
            User.objects.create_superuser(
                email=root_email,
                first_name=first_name,
                last_name=last_name,
                role=root_role,
                password=root_password,
            )
            self.stdout.write(self.style.SUCCESS(f"✅ Root user created with email: {root_email}"))
        else:
            self.stdout.write(self.style.WARNING(f"⚠️ Root user with email {root_email} already exists"))
