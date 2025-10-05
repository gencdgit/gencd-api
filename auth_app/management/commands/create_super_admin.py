import time
import getpass
from django.core.management.base import BaseCommand
from auth_app.models import User, Role
from django.utils import timezone



class Command(BaseCommand):
    help = 'Creates the first Super Admin role and user interactively'

    def handle(self, *args, **options):
        # 1️⃣ Ask for email
        while True:
            email = input("Enter email for the Super Admin user: ").strip()
            if email:
                break
            self.stdout.write(self.style.ERROR("Email cannot be empty!"))

        # 2️⃣ Ask for password (hidden)
        while True:
            password = getpass.getpass("Enter password for Super Admin: ").strip()
            if password:
                break
            self.stdout.write(self.style.ERROR("Password cannot be empty!"))

        # 3️⃣ First & Last name
        first_name = input("Enter first name [Default: Super]: ").strip() or "Super"
        last_name = input("Enter last name [Default: Admin]: ").strip() or "Admin"

        self.stdout.write(self.style.WARNING("Creating Super Admin role..."))

        # 4️⃣ Create role with just **one permission object**
        super_admin_role, role_created = Role.objects.get_or_create(
            name="Super Admin",
            defaults={
                "description": "System role with all permissions",
                "permissions": [
                      {
                        "slug": "system.all",
                        "name": "System Role - All Permissions",
                        "description": "This role has all permissions and can perform any action in the system.",
                        "category": "system",
                        "request_method": "*"
                    },

                ],
                "is_system": True,
                "is_super_admin": True,
                "created_at": timezone.now(),
                "updated_at": timezone.now()
            }
        )

        # 5️⃣ Simple progress bar
        for i in range(0, 101, 20):
            self.stdout.write(f"\rProgress: [{'=' * (i // 5)}{' ' * (20 - i // 5)}] {i}%", ending="\r")
            time.sleep(0.2)
        self.stdout.write("\n")

        if role_created:
            self.stdout.write(self.style.SUCCESS("✅ Super Admin role created successfully!"))
        else:
            self.stdout.write(self.style.WARNING("⚠️ Super Admin role already exists."))

        # 6️⃣ Create Super Admin user
        if not User.objects.filter(email=email).exists():
            User.objects.create_superuser(
                email=email,
                first_name=first_name,
                last_name=last_name,
                role=super_admin_role,
                password=password,
            )
            self.stdout.write(self.style.SUCCESS(f"✅ Super Admin user created with email: {email}"))
        else:
            self.stdout.write(self.style.WARNING(f"⚠️ Super Admin user with email {email} already exists"))
