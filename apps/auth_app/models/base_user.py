from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Types(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        JOBSEEKER = "JOBSEEKER", "Job seeker"
        EMPLOYER = "EMPLOYER", "Owner"

    base_type = Types.ADMIN
    account_type = models.CharField(max_length=20, choices=Types.choices)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.type = self.base_type
            return super().save(*args, **kwargs)
