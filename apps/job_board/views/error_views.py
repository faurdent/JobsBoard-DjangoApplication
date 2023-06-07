from django.views.generic import TemplateView


class EntityNotFoundView(TemplateView):
    template_name = "job_board/error_template.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"error": "Page not found", "error_message": "You don't have such record."})
        return context
