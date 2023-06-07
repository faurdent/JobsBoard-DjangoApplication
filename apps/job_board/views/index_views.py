from apps.job_board.views.modificated_views import IndexAbstractView


class IndexJobSeekerView(IndexAbstractView):
    template_name = "job_board/index.html"


class IndexEmployerView(IndexAbstractView):
    template_name = "job_board/index_employer.html"
