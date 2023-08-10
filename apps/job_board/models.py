from django.db import models
from django.urls import reverse

from apps.auth_app.models import JobSeekerProfile, EmployerProfile, User
from apps.services import ImagePathsGenerator


class CompanyOwnership(models.Model):
    owner = models.ForeignKey(EmployerProfile, on_delete=models.CASCADE)
    company = models.ForeignKey("Company", on_delete=models.CASCADE)
    is_creator = models.BooleanField(default=False)


class Company(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    logo = models.ImageField(
        max_length=255,
        null=True,
        blank=True,
        upload_to=ImagePathsGenerator.get_company_logo
    )
    owners = models.ManyToManyField(EmployerProfile, through=CompanyOwnership, related_name="companies")

    def get_absolute_url(self):
        return reverse("company_details", kwargs={"pk": self.pk})

    def __str__(self):
        return self.name


class PositionType(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Vacancy(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    position = models.ForeignKey(PositionType, on_delete=models.PROTECT, related_name="position_vacancies")
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="vacancies")
    is_closed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse("vacancy_details", kwargs={"pk": self.pk})

    class Meta:
        ordering = ["-created_at"]


class VacancyResponse(models.Model):
    class ResponseStatus(models.TextChoices):
        PENDING = ("PENDING", "Pending")
        ACCEPTED = ("ACCEPTED", "Accepted")
        REJECTED = ("REJECTED", "Rejected")

    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE, related_name="users_responded")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="left_responses")
    status = models.CharField(max_length=10, choices=ResponseStatus.choices, default=ResponseStatus.PENDING)


class OwningRequest(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="employers_requested")
    employer = models.ForeignKey(EmployerProfile, on_delete=models.CASCADE, related_name="left_requests")
    text = models.TextField(default=None, null=True, blank=True)
    is_accepted = models.BooleanField(default=False)
    is_read = models.BooleanField(default=False)
    is_hidden = models.BooleanField(default=False)
