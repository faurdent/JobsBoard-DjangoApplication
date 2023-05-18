from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from django.core.management import BaseCommand

from apps.job_board.models import Company


class Command(BaseCommand):
    def handle(self, *args, **options):
        self._create_owner_group()

    def _create_owner_group(self):
        company_content_type = ContentType.objects.get_for_model(Company)
        company_permissions = Permission.objects.filter(content_type=company_content_type)
        owner_group, created_owner = Group.objects.get_or_create(name="Owner")
        if created_owner:
            for permission in company_permissions:
                owner_group.permissions.add(permission)
            self.stdout.write("Company group created successfully.")
            return
        self.stdout.write("Company group already exists.")
