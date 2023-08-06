from django.urls import reverse_lazy

from apps.job_board.models import Vacancy
from apps.job_board.views.modificated_views import IndexAbstractView


class IndexJobSeekerView(IndexAbstractView):
    template_name = "job_board/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"link": reverse_lazy("employer_home"), "link_redirect_name": "Employers"})
        context.update({"latest_vacancies": Vacancy.objects.filter(is_closed=False).all()[:3]})
        return context


class IndexEmployerView(IndexAbstractView):
    template_name = "job_board/index_employer.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"link": reverse_lazy("home"), "link_redirect_name": "Job seekers"})
        return context
