from django.conf import settings
from rest_framework.generics import ListAPIView, RetrieveAPIView

from bookmanager.books.filters import InternalBooksFilter
from bookmanager.books.models import Book

from .serializers import BookSerializer

PAGINATE_BY = settings.PAGINATE_BY  # type: ignore


class BookListBaseMixin(object):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    paginate_by = PAGINATE_BY
    order_by = "title"


class BooksList(BookListBaseMixin, ListAPIView):
    """Return list of books ordered by title."""


class BooksSearch(BookListBaseMixin, ListAPIView):
    """Filter books by given fields.

    Filtering can by done by following fields:

    - title
    - author
    - published_date search within given date range
    - language

    """

    filterset_class = InternalBooksFilter


class BooksDetail(RetrieveAPIView):
    """Return book details for given pk.

    Fields that values are returned:

    - id
    - title
    - author
    - published_date
    - isbn_10
    - isbn_13
    - pages
    - cover_uri
    - language

    """

    kwargs = {}
    queryset = Book.objects.all()
    serializer_class = BookSerializer
