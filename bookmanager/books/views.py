import requests
from django.conf import settings
from django.conf.global_settings import LANGUAGES
from django.contrib import messages
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import (
    CreateView,
    DeleteView,
    ListView,
    TemplateView,
    UpdateView,
)
from django_filters.views import FilterView

from .filters import InternalBooksFilter
from .forms import BookAddEditForm, GoogleSearchForm
from .models import Book
from .utils import (
    API,
    create_paginator,
    get_google_api_books,
    get_paginator_page,
    google_book_parser,
)

languages = dict(LANGUAGES)

# the only way I found to satisfy mypy which can't import settings attrs
PAGINATE_BY = settings.PAGINATE_BY  # type: ignore


class BookListView(ListView):
    paginate_by = PAGINATE_BY
    model = Book
    context_object_name = "books"
    ordering = ["title"]
    template_name = "books/list.html"


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


class BookUpdateView(UpdateView):
    model = Book
    form_class = BookAddEditForm
    success_url = "/books"
    template_name = "books/add_edit_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["action"] = reverse("books:update", kwargs={"pk": context["object"].pk})
        context["create"] = False
        return context


class BookDeleteView(DeleteView):
    model = Book
    success_url = "/"


class BookSearchListView(FilterView):
    paginate_by = PAGINATE_BY
    model = Book
    context_object_name = "books"
    ordering = ["-published_date"]
    template_name = "books/list.html"
    filterset_class = InternalBooksFilter

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class ImportList(TemplateView):
    template_name = "books/list.html"
    page = None

    def get_context_data(self):
        form = GoogleSearchForm(self.request.GET)

        if self.request.GET and form.is_valid():
            books, total, status = get_google_api_books(
                query_dict=self.request.GET, page=self.page
            )
            paginator = create_paginator(books, total, self.page)
            context = {
                "books": books,
                "is_paginated": paginator.num_pages - 1,
                "page_obj": get_paginator_page(paginator, self.page),
                "search": self.request.environ["QUERY_STRING"].strip(
                    f"?page={self.page}&"
                ),
                "query_dict": self.request.GET,
                "import": True,
            }
        else:
            context = {"import": True}
        return context

    def dispatch(self, request, *args, **kwargs):
        page = request.GET.get("page", "1")
        if not page.isdecimal():
            return HttpResponseBadRequest("Improper page value", status=400)
        self.page = int(page)
        return super().dispatch(request, *args, **kwargs)


class ImportBook(TemplateView):
    """View for import and edit books from google api.

    Require google api book id.

    """

    template_name = "books/add_edit_form.html"
    form_class = BookAddEditForm
    google_id = None
    google_response = None
    context = None

    def get_google_book(self):
        self.google_response = requests.get(f"{API}/{self.google_id}")

    def get_context_data(self, **kwargs):
        self.context = super().get_context_data(**kwargs)
        self.get_google_book()
        if self.google_response.status_code == 200:
            self.context_response_status_200()
        return self.context

    def get(self, request, *args, **kwargs):
        get = super().get(request, *args, **kwargs)
        if self.google_response.status_code != 200:
            self.fetch_data_error()
            return redirect(reverse("books:import-list"))
        return get

    def context_response_status_200(self):
        book = google_book_parser(self.google_response.json())
        form = self.form_class(initial={**book})
        self.context.update(
            {
                "form": form,
                "action": reverse("books:add-form"),
                "create": True,
            }
        )

    def fetch_data_error(self):
        messages.error(
            self.request,
            message=f"Could not fetch book data error - "
            f"{self.google_response.status_code}",
        )

    def setup(self, request, *args, **kwargs):
        self.google_id = request.GET.get("id")
        return super().setup(request, *args, **kwargs)
