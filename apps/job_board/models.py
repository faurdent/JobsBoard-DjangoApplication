from django.urls import reverse

from apps.auth_app.models import JobSeekerProfile, EmployerProfile

from django.db import models


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

    def get_absolute_url(self):
        return reverse("vacancy_details", kwargs={"pk": self.pk})
