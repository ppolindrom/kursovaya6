import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from django.core.management import BaseCommand
from users.models import User


class Command(BaseCommand):
    """Команда для создания суперюзера"""
    def handle(self, *args, **options):
        user = User.objects.create(
            email="admin@mail.ru",
            first_name="admin",
            last_name="admin",
            is_superuser=True,
            is_staff=True,
            is_active=True
            )

        user.set_password("1005")
        print(user)
        user.save()


# if __name__ == '__main__':
#     u = Command.handle()

