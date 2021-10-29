from django.template.response import TemplateResponse


def handle_400(request, exception=None):
    return TemplateResponse(request, "400.html", status=400)


def handle_404(request, exception=None):
    return TemplateResponse(request, "404.html", status=404)
