from apps.job_board.views.modificated_views import IndexView


class IndexJobSeekerView(IndexView):
    template_name = "job_board/index.html"


class IndexEmployerView(IndexView):
    template_name = "job_board/index_employer.html"
