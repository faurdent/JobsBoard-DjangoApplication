from typing import Type

from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from django.core.management import BaseCommand
from django.db.models import Model

from apps.auth_app.models.models import Employee
from apps.job_board.models import Company, Vacancy, VacancyResponse


class Command(BaseCommand):
    def handle(self, *args, **options):
        self._create_group("Owner", [VacancyResponse, Vacancy, Company, Employee])
        self._create_group("HR", [Vacancy, Employee])

    def _create_group(self, group_name: str, models: list[Type[Model]]):
        all_permissions = []
        for model in models:
            all_permissions.extend(self.get_permissions_for_model(model, group_name))
        owner_group, created_owner = Group.objects.get_or_create(name=group_name)
        for permission in all_permissions:
            owner_group.permissions.add(permission)
        self.stdout.write(f"{group_name} group created successfully.")

    def get_permissions_for_model(self, model: Type[Model], group_name: str):
        content_type = ContentType.objects.get_for_model(model)
        permissions = Permission.objects.filter(content_type=content_type)
        self.stdout.write(f"Got permissions for {group_name} group and model {model._meta.model_name}")
        return permissions
