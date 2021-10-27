from django import template
from django.conf import settings
from django.conf.global_settings import LANGUAGES
from django.urls import reverse

register = template.Library()


@register.simple_tag
def languages_list():
    return LANGUAGES


@register.simple_tag
def language(field):
    codes = dict(LANGUAGES)
    code = get_value(field)
    name = codes.get(code) or "Language"
    return name


@register.filter(name="book_index")
def count_book_index(page, index):
    return (page - 1) * settings.PAGINATE_BY + index


@register.simple_tag
def get_value(field):
    value = field.form.data.get(field.name.replace("_", "-"), "")
    return value


@register.inclusion_tag("../templates/books/internal_search_form.html")
def internal_search_form(_filter):
    return {"action": reverse("books:search"), "filter": _filter}


@register.inclusion_tag("../templates/books/google_search_form.html")
def google_search_form(query_dict):
    context = {}
    if isinstance(query_dict, dict):
        context = {item[0]: item[1] for item in query_dict.items()}
    return {"action": reverse("books:import-list"), **context}


@register.inclusion_tag("../templates/books/cover_frame.html")
def cover_frame(cover_uri):
    return {"cover_uri": cover_uri}


@register.inclusion_tag("../templates/pagination.html")
def pagination(page_obj, query=""):
    buttons = []
    pages = page_obj.paginator.num_pages
    current_page = page_obj.number

    # add button with "previous" text if previous page exists
    if page_obj.has_previous():
        previous = page_obj.previous_page_number()
        buttons.append(
            {"page": previous, "current": previous == current_page, "text": "previous"}
        )

    # always add button with link to first page
    first = {"page": "1", "current": 1 == current_page, "text": 1}
    buttons.append(first)

    # always add buttons with link to +-scope from current page
    scope = 2
    for i in range(2, pages):
        if current_page - scope <= i <= current_page + scope:
            buttons.append({"page": i, "current": i == current_page, "text": i})

    # add button with link to the last page if current page is not the last
    if current_page < pages:
        buttons.append({"page": pages, "current": pages == current_page, "text": pages})

    # add button with "next" text if next page exists
    if page_obj.has_next():
        _next = page_obj.next_page_number()
        buttons.append(
            {"page": _next, "current": _next == current_page, "text": "next"}
        )

    return {"query": query, "buttons": buttons}
