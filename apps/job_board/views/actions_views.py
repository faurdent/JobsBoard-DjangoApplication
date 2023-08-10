from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import Group
from django.core.handlers.wsgi import WSGIRequest
from django.db import transaction
from django.shortcuts import redirect
from django.views import View

from apps.auth_app.models import User
from apps.auth_app.models.models import EmployeeProfile, Employee
from apps.job_board.models import VacancyResponse, Vacancy, PositionType, Company, OwningRequest


class VacancyResponseView(LoginRequiredMixin, View):
    def post(self, request: WSGIRequest, *args, **kwargs):
        vacancy = Vacancy.objects.filter(pk=self.kwargs["pk"]).first()
        if not vacancy:
            return redirect("not_found")
        if existing_response := VacancyResponse.objects.filter(
                user=request.user, vacancy=vacancy
        ).first():
            existing_response.delete()
        else:
            vacancy_response = VacancyResponse.objects.create(user=request.user, vacancy=vacancy)
            vacancy.users_responded.add(vacancy_response)
        return redirect("vacancy_details", pk=vacancy.pk)


class AcceptJobSeeker(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "auth_app.add_employeeprofile"

    def post(self, request: WSGIRequest, *args, **kwargs):
        vacancy_response: VacancyResponse = VacancyResponse.objects.filter(
            user_id=self.kwargs["user_pk"], vacancy_id=self.kwargs["vacancy_pk"]
        ).first()
        if not vacancy_response:
            return redirect("not_found")

        with transaction.atomic():
            employee_profile = EmployeeProfile(
                user=vacancy_response.user,
                company=vacancy_response.vacancy.company,
                position=vacancy_response.vacancy.position
            )
            employee_profile.save()
            self._update_related_data(vacancy_response)
            hr_position_type = PositionType.objects.get(name="HR")
            if employee_profile.position == hr_position_type:
                employee_profile.user.groups.add(Group.objects.get(name="HR"))
        return redirect("company_employees", pk=vacancy_response.vacancy.company.pk)

    def _update_related_data(self, vacancy_response: VacancyResponse):
        vacancy_response.status = VacancyResponse.ResponseStatus.ACCEPTED
        vacancy_response.vacancy.is_closed = True
        vacancy_response.user.account_type = User.Types.EMPLOYEE
        vacancy_response.save()
        vacancy_response.vacancy.save()
        vacancy_response.user.save()


class RejectJobSeeker(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "job_board.add_employeeprofile"

    def post(self, request: WSGIRequest, *args, **kwargs):
        vacancy_response: VacancyResponse = VacancyResponse.objects.filter(
            user_id=self.kwargs["user_pk"], vacancy_id=self.kwargs["vacancy_pk"]
        ).first()
        if not vacancy_response:
            return redirect("not_found")
        vacancy_response.status = VacancyResponse.ResponseStatus.REJECTED
        vacancy_response.save()
        return redirect("view_responses", pk=self.kwargs["vacancy_pk"])


class FireEmployeeView(LoginRequiredMixin, View):
    def post(self, request: WSGIRequest, *args, **kwargs):
        employee = Employee.objects.filter(pk=self.kwargs["user_pk"]).first()
        if not employee:
            return redirect("not_found")
        employee.account_type = User.Types.JOBSEEKER
        employee.employee_profile.delete()
        employee.save()
        return redirect("company_employees", pk=self.kwargs["company_pk"])


class RequestCompanyOwnership(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "job_board.add_owningrequest"

    def post(self, request: WSGIRequest, *args, **kwargs):
        company: Company = Company.objects.filter(pk=self.kwargs["company_pk"])
        if not company:
            return redirect("not_found")
        employer_profile = request.user.employer_profile
        if existing_request := OwningRequest.objects.filter(
                employer=employer_profile, company=company
        ):
            existing_request.delete()
        else:
            new_request = OwningRequest.objects.create(employer=employer_profile)
            company.employers_requested.add(new_request)
        return redirect("company_details")
