from django.db import models
from django.urls import reverse

from apps.auth_app.models import JobSeekerProfile, EmployerProfile, User


class CompanyOwnership(models.Model):
    owner = models.ForeignKey(EmployerProfile, on_delete=models.CASCADE)
    company = models.ForeignKey("Company", on_delete=models.CASCADE)
    is_creator = models.BooleanField(default=False)


class Company(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
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

    def get_absolute_url(self):
        return reverse("vacancy_details", kwargs={"pk": self.pk})


class VacancyResponse(models.Model):
    class ResponseStatus(models.TextChoices):
        PENDING = ("PENDING", "Pending")
        ACCEPTED = ("ACCEPTED", "Accepted")
        REJECTED = ("REJECTED", "Rejected")

    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE, related_name="users_responded")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="left_responses")
    status = models.CharField(max_length=10, choices=ResponseStatus.choices, default=ResponseStatus.PENDING)
