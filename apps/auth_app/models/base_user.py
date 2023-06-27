from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse

from apps.services import ImagePathsGenerator


class User(AbstractUser):
    class Types(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        JOBSEEKER = "JOBSEEKER", "Job seeker"
        EMPLOYER = "EMPLOYER", "Owner"
        EMPLOYEE = "EMPLOYEE", "Employee"

    email = models.EmailField(blank=False)
    avatar = models.ImageField(
        max_length=255,
        null=True,
        blank=True,
        upload_to=ImagePathsGenerator.get_avatar_path_user,
    )
    base_type = Types.ADMIN
    account_type = models.CharField(max_length=20, choices=Types.choices)

    def get_absolute_url(self):
        return reverse("profile", kwargs={"username": self.username})

    def save(self, *args, **kwargs):
        if not self.pk:
            self.account_type = self.base_type
            return super().save(*args, **kwargs)
