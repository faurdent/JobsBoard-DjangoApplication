from django.contrib.auth.models import BaseUserManager

from apps.auth_app.models.base_user import User


class JobSeekerManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        users = super().get_queryset(*args, **kwargs)
        return users.filter(account_type=User.Types.JOBSEEKER)


class EmployerManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        users = super().get_queryset(*args, **kwargs)
        return users.filter(account_type=User.Types.EMPLOYER)


class EmployeeManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        users = super().get_queryset(*args, **kwargs)
        return users.filter(account_type=User.Types.EMPLOYEE)
