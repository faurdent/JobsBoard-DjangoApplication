from django.db import models

from apps.auth_app.models.base_user import User
from apps.auth_app.models.managers import JobSeekerManager, EmployerManager


class JobSeeker(User):
    objects = JobSeekerManager()
    base_type = User.Types.JOBSEEKER

    class Meta:
        proxy = True


class Employer(User):
    objects = EmployerManager()
    base_type = User.Types.EMPLOYER

    class Meta:
        proxy = True


class JobSeekerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="jobseeker_profile")
    jobseeker_id = models.IntegerField(null=True, blank=True)


class EmployerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="employer_profile")
    owner_id = models.IntegerField(null=True, blank=True)
