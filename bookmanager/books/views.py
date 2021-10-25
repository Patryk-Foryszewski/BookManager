from django.urls import reverse
from django.views.generic import CreateView

from .forms import BookAddEditForm
from .models import Book


class BookCreateView(CreateView):
    model = Book
    form_class = BookAddEditForm
    template_name = "books/add_edit_form.html"
    success_url = "/"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["action"] = reverse("books:add-form")
        context["create"] = True
        return context
