from django.db import models

from apps.auth_app.models.base_user import User
from apps.auth_app.models.managers import JobSeekerManager, EmployerManager, EmployeeManager


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


class Employee(User):
    objects = EmployeeManager
    base_type = User.Types.EMPLOYEE

    class Meta:
        proxy = True


class JobSeekerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="jobseeker_profile")
    cv = models.FileField(upload_to="cv", blank=True, null=True, default=None)
    jobseeker_id = models.IntegerField(null=True, blank=True)
    skills = models.ManyToManyField("job_board.PositionType")
    company = models.ForeignKey("job_board.Company", on_delete=models.PROTECT, related_name="workers")


class EmployerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="employer_profile")
    has_company = models.BooleanField(default=False)
    owner_id = models.IntegerField(null=True, blank=True)


class EmployeeProfile(models.Model):
    position = models.ForeignKey("job_board.PositionType", on_delete=models.PROTECT)
    company = models.ForeignKey("job_board.Company", on_delete=models.PROTECT)
    user = models.OneToOneField(User, on_delete=models.PROTECT)
