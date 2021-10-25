import django_filters

from .models import Book


class InternalBooksFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr="icontains")
    author = django_filters.CharFilter(lookup_expr="icontains")

    date_from = django_filters.DateFilter(
        required=False,
        field_name="published_date",
        lookup_expr="gte",
    )
    date_to = django_filters.DateFilter(
        required=False,
        field_name="published_date",
        lookup_expr="lte",
    )

    class Meta:
        model = Book
        fields = ["title", "author", "language", "published_date"]
