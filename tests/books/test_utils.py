from math import ceil
from unittest import mock

from django.conf import settings
from django.core.paginator import Paginator
from django.test import TestCase
from django.urls import reverse

from bookmanager.books.utils import (
    create_paginator,
    get_google_api_books,
    get_paginator_page,
    google_api_query,
    google_book_parser,
    identifiers_finder,
)

from .utils import GOOGLE_API_JSON_RESPONSES_MOCK, RequestResponseMock


class TestGoogleParser(TestCase):
    def test_bad_data(self):
        parsed = google_book_parser({"wrong_key": "wrong_value"})
        pattern = GOOGLE_API_JSON_RESPONSES_MOCK["empty"]
        self.assertDictEqual(parsed, pattern)


class TestIdentifiersFinder(TestCase):
    def test_correct_identifiers(self):

        parsed = identifiers_finder(
            [
                {"type": "ISBN_10", "identifier": "8365970392"},
                {"type": "ISBN_13", "identifier": "9788365970398"},
            ]
        )
        pattern = {"isbn_10": "8365970392", "isbn_13": "9788365970398"}
        self.assertDictEqual(parsed, pattern)

    def test_uncorrect_identifiers(self):

        parsed = identifiers_finder(
            [
                {"type": "OTHER", "identifier": ""},
            ]
        )
        pattern = {"isbn_10": "", "isbn_13": ""}
        self.assertDictEqual(parsed, pattern)


class GoogleApiHomeTest(TestCase):
    """Test for Google Api import page."""

    url = reverse("books:import-list")

    def test_get(self):
        """Tests get book detail."""
        books = self.client.get(self.url)
        self.assertEqual(books.status_code, 200)

    def test_post(self):
        """Tests unallowed POST method."""
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 405)  # Method not allowed

    def test_put(self):
        """Tests unallowed PUT method."""
        response = self.client.put(self.url)
        self.assertEqual(response.status_code, 405)  # Method not allowed

    def test_patch(self):
        """Tests unallowed PATCH method."""
        response = self.client.patch(self.url)
        self.assertEqual(response.status_code, 405)  # Method not allowed

    def test_delete(self):
        """Tests unallowed DELETE method."""
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 405)  # Method not allowed


class GoogleApiQuery(TestCase):
    """Test for google_api_query function."""

    def test_parsing(self):
        pattern = "q=string+intitle:title+inauthor:author"
        kwargs = {"intitle": "title", "inauthor": "author", "search": "string"}
        query = google_api_query(kwargs)

        self.assertEqual(pattern, query)

    def test_parsing_without_q(self):
        kwargs = {"intitle": "title", "inauthor": "author"}
        pattern = "q=+intitle:title+inauthor:author"
        query = google_api_query(kwargs)

        self.assertEqual(pattern, query)


class CreatePaginatorTest(TestCase):
    total = 200
    items = ["#" for _ in range(settings.PAGINATE_BY)]

    @classmethod
    def setUpTestData(cls) -> None:
        """Create paginator with utils.create_paginator."""
        cls.paginator = create_paginator(items=cls.items, total=cls.total)

    def test_returned_object(self):
        """Check if returned object is paginator."""
        self.assertIsInstance(self.paginator, Paginator)

    def test_num_pages(self):
        """Check returned number of paginator pages."""
        self.assertEqual(
            ceil(self.total / settings.PAGINATE_BY), self.paginator.num_pages
        )

    def test_pagination_when_len_items_is_less_than_paginate_by(self):

        total = 100
        items = ["#" for _ in range(16)]
        paginator = create_paginator(items=items, total=total)
        self.assertIsInstance(paginator, Paginator)
        self.assertEqual(paginator.num_pages, ceil(total / settings.PAGINATE_BY))

    def test_not_full_page(self):
        """Check paginator for one page."""
        paginator = create_paginator(items=self.items[:10], total=10)
        self.assertIsInstance(paginator, Paginator)
        self.assertEqual(1, paginator.num_pages)

    def test_empty_query(self):
        """Check paginator for zero items."""
        paginator = create_paginator(items=[], total=0)
        self.assertIsInstance(paginator, Paginator)
        self.assertEqual(1, paginator.num_pages)


class GetPaginatorPage(TestCase):
    """Check paginator pages."""

    @classmethod
    def setUpTestData(cls) -> None:
        cls.total = 200
        cls.items = ["#" for _ in range(settings.PAGINATE_BY)]

    def test_get_paginator_pages(self):
        for page in range(1, ceil(self.total / settings.PAGINATE_BY) + 1):
            paginator = create_paginator(items=self.items, total=self.total, page=page)

            _from = (page - 1) * settings.PAGINATE_BY
            to = page * settings.PAGINATE_BY
            for i, _ in enumerate(paginator.object_list[:_from]):
                self.assertEqual("", paginator.object_list[i])

            for i, _ in enumerate(paginator.object_list[_from:to]):
                self.assertEqual("#", paginator.object_list[i + _from])

            for i, _ in enumerate(paginator.object_list[to + 1 : -1]):
                self.assertEqual("", paginator.object_list[to + i])

    def test_paginator_empty_page(self):
        """Test if returned paginator page have correct items.

        Check if paginator returns page with items when
        requested page is out of range.
        """

        page = 2
        paginator = create_paginator(items=self.items, total=self.total, page=page)
        content = get_paginator_page(paginator, 6)
        self.assertEqual(content.number, page)


def google_correct_json_response(
    _status: int = 200, _json: dict = None, *_
) -> RequestResponseMock:
    if not _json:
        _json = {"totalItems": 1, "items": [GOOGLE_API_JSON_RESPONSES_MOCK["correct"]]}
    return RequestResponseMock(json_data=_json, status_code=_status)


def google_uncorrect_json_response(*_) -> RequestResponseMock:
    return RequestResponseMock(status_code=400)


class GoogleApisBooks(TestCase):
    """Test for get_google_api_books."""

    @classmethod
    def setUpTestData(cls) -> None:
        cls.endpoint = "import-list/search"

    @mock.patch(
        "bookmanager.books.utils.requests.get",
        return_value=google_correct_json_response(),
    )
    def test_get_google_books_with_correct_query(self, google_api_mock):
        """Test if api returns items for correct query."""
        query = {"q": "harry", "inauthor": "Rowling"}

        results = get_google_api_books(query_dict=query)
        self.assertIsInstance(results, tuple)
        self.assertIsInstance(results[0], list)
        self.assertIsInstance(results[1], int)
        self.assertEqual(results[2], 200)  # OK

    @mock.patch(
        "bookmanager.books.utils.requests.get",
        return_value=google_uncorrect_json_response(),
    )
    def test_get_google_books_with_uncorrect_query(self, google_api_mock):
        """Test response for uncorrect query."""
        results = get_google_api_books(
            query_dict={}, params={"startIndex": 0, "maxResults": 40}
        )
        self.assertIn(
            mock.call(
                "https://www.googleapis.com/books/v1/volumes?",
                params={"startIndex": 0, "maxResults": 40},
            ),
            google_api_mock.call_args_list,
        )
        self.assertIsInstance(results, tuple)
        self.assertEqual(0, len(results[0]))
        self.assertEqual(0, results[1])
        self.assertEqual(results[2], 400)  # BAD REQUEST
