from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.urls import reverse_lazy


class User(AbstractUser):
    email = models.EmailField(blank=False)

    class Types(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        JOBSEEKER = "JOBSEEKER", "Job seeker"
        EMPLOYER = "EMPLOYER", "Owner"
        EMPLOYEE = "EMPLOYEE", "Employee"

    base_type = Types.ADMIN
    account_type = models.CharField(max_length=20, choices=Types.choices)

    def get_absolute_url(self):
        return reverse_lazy("profile", username=self.username)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.account_type = self.base_type
            return super().save(*args, **kwargs)
