import datetime
from unittest import mock

from django.test import TestCase
from django.urls import reverse
from factory.fuzzy import FuzzyDate as Fake_Date

from bookmanager.books.models import Book
from bookmanager.books.views import (
    BookCreateView,
    BookSearchListView,
    BookUpdateView,
    ImportList,
)

from ..utils import request_factory
from .factories import BookFactory
from .utils import GOOGLE_API_JSON_RESPONSES_MOCK, RequestResponseMock

VALID_ISBN10 = "9788362020867"
VALID_ISBN13 = "978-83-948712-2-2"
VALID_LANGUAGE = "en"
INVALID_LANGUAGE = "enb"


class BookListTest(TestCase):
    """Test for BookListView."""

    def test_book_list_get(self):
        response = self.client.get(reverse("books:list"))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "books/list.html")


class BookUpdateTest(TestCase):
    """Test for BookUpdateView."""

    @classmethod
    def setUpTestData(cls) -> None:
        cls.book = Book.objects.create(
            title="Camera Work 1",
            author="Alfred Stieglitz",
            published_date="2008-10-15",
            isbn_10=VALID_ISBN10,
            isbn_13=VALID_ISBN13,
            cover_uri="image.jpg",
            language=VALID_LANGUAGE,
        )
        cls.required_fields = ["title", "author"]
        cls.required_context = ["object", "book", "form", "view", "action", "create"]

    def test_update_book(self):
        """Create book object and updates fields with correct data."""

        data = {
            "title": "The Catcher in the Rye",
            "author": "J.D. Salinger",
            "published_date": "2008-10-15",
            "isbn_10": VALID_ISBN10,
            "isbn_13": VALID_ISBN13,
            "cover_uri": "image.jpg",
            "language": "en",
        }

        request = request_factory.post("/", data=data)
        BookUpdateView.as_view()(request, pk=self.book.pk)
        self.book.refresh_from_db()
        self.assertEqual(self.book.title, "The Catcher in the Rye")
        self.assertEqual(self.book.author, "J.D. Salinger")
        self.assertEqual(str(self.book.published_date), "2008-10-15")

    def test_response_context(self):
        """Checks if context consists of required keys."""

        request = request_factory.get("/")
        response = BookUpdateView.as_view()(request, pk=self.book.pk)

        for key in self.required_context:
            self.assertTrue(key in response.context_data.keys())


class BookCreateTest(TestCase):
    """Test for BookCreateView."""

    def test_book_create_template(self):
        response = self.client.get(reverse("books:add-form"))
        self.assertTemplateUsed(response, "books/add_edit_form.html")

    def test_book_create_post_method(self):
        title = "Test"
        author = "Author"
        data = {
            "title": title,
            "author": author,
            "language": "en",
            "published_date": "2020-11-11",
        }

        request = request_factory.post("/", data=data)
        response = BookCreateView.as_view()(request)
        book = Book.objects.first()
        self.assertEquals(response.status_code, 302)
        self.assertEqual(book.title, title)
        self.assertEqual(book.author, author)


class TestBookSearchListView(TestCase):
    """Test BookSearchListView."""

    @classmethod
    def setUpTestData(cls) -> None:
        cls.url = reverse("books:search")
        cls.date_from = datetime.date(1970, 1, 1)
        cls.date_between_1 = datetime.date(1985, 1, 1)
        cls.date_between_2 = datetime.date(1995, 1, 1)
        cls.date_to = datetime.date(2021, 1, 1)
        BookFactory(published_date=cls.date_from)
        BookFactory(title="camera", published_date=cls.date_to)
        BookFactory.create_batch(
            2, published_date=Fake_Date(cls.date_from, cls.date_between_1)
        )
        BookFactory.create_batch(
            2, published_date=Fake_Date(cls.date_between_1, cls.date_between_2)
        )
        BookFactory.create_batch(
            2, published_date=Fake_Date(cls.date_between_2, cls.date_to)
        )

    def response_factory(self, data):
        request = request_factory.get(self.url, data=data)
        return BookSearchListView.as_view()(request)

    def test_search_existing_book(self):
        """Test whether searching for title that exists returns book."""
        response = self.response_factory(data={"title": "camera"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context_data["object_list"]), 1)
        book = response.context_data["object_list"][0]
        self.assertTrue(book.title == "camera")

    def test_search_through_date_from(self):
        """Test if query return only book newer than given date."""

        response = self.response_factory(data={"date_from": self.date_from})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context_data["object_list"]), 8)

        for book in response.context_data["object_list"]:
            self.assertTrue(book.published_date >= self.date_from)

    def test_search_through_date_range(self):
        """Test if query return only books within given date range."""

        response = self.response_factory(
            data={"date_from": self.date_between_1, "date_to": self.date_between_2}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context_data["object_list"]), 2)

        for book in response.context_data["object_list"]:
            self.assertTrue(
                self.date_between_1 <= book.published_date <= self.date_between_2
            )

    def test_search_through_date_to(self):
        """Test if query return only book older than given date."""

        response = self.response_factory(data={"date_to": self.date_between_1})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context_data["object_list"]), 3)

        for book in response.context_data["object_list"]:
            self.assertTrue(book.published_date <= self.date_between_1)

    def test_search_date_equal(self):
        """Test if query return only book equal to given date."""

        response = self.response_factory(
            data={"date_from": self.date_from, "date_to": self.date_from}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context_data["object_list"]), 1)

        book = response.context_data["object_list"][0]
        self.assertTrue(book.published_date == self.date_from)


class GoogleBookImport(TestCase):
    """Test views for list books from google api."""

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse("books:import-list")
        cls.search = "harry inauthor:Rowling"
        cls.page = 1
        cls.correct_query = f"q={cls.search}&page={cls.page}"

    def test_google_import_list_page_without_query(self):
        """Test if request returns keys required for rendering."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("books/list.html")
        self.assertTrue(response.context["import"])

    @mock.patch(
        "bookmanager.books.views.get_google_api_books", return_value=[[], 0, 200]
    )
    def test_import_response_and_context(self, google_api_mock):
        required_context = [
            "books",
            "page_obj",
            "search",
            "is_paginated",
            "import",
        ]
        request = request_factory.get(
            "/", data={"search": self.search, "page": self.page}
        )
        response = ImportList.as_view()(request)

        self.assertEqual(google_api_mock.call_count, 1)
        self.assertIn(
            mock.call(query_dict=request.GET, page=1),
            google_api_mock.call_args_list,
        )
        for key in required_context:
            self.assertTrue(key in response.context_data.keys())
        self.assertEqual(response.status_code, 200)

    def test_bad_query_response(self):
        response = self.client.get(
            reverse("books:import-list"), data={"z": "-", "page": "e"}
        )
        self.assertEqual(response.status_code, 400)


def google_response_200(*_):
    return RequestResponseMock(
        json_data=GOOGLE_API_JSON_RESPONSES_MOCK["correct"], status_code=200
    )


def google_response_404(*_, **kwargs):
    return RequestResponseMock(status_code=404)


class ImportBookView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.required_context = ["form", "action", "create"]

    @mock.patch(
        "bookmanager.books.views.google_book_parser",
        return_value=GOOGLE_API_JSON_RESPONSES_MOCK["correct"],
    )
    @mock.patch("bookmanager.books.views.requests.get", side_effect=google_response_200)
    def test_import_book_view_with_200_response_from_google(self, *_):
        rev = reverse("books:import-book")
        uri = f"{rev}?id=correct_id"
        response = self.client.get(uri)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "books/add_edit_form.html")
        for key in self.required_context:
            self.assertTrue(key in response.context.keys())

    @mock.patch("bookmanager.books.views.requests.get", side_effect=google_response_404)
    def test_import_book_view_with_404_response_from_google(self, *_):
        rev = reverse("books:import-book")
        uri = f"{rev}?id=correct_id"
        response = self.client.get(uri, follow=True)
        self.assertContains(response, "Could not fetch book data")
        self.assertRedirects(response, reverse("books:import-list"))


class DeleteView(TestCase):
    """Test DeleteView view from .views."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Create book object in database and path to delete that book."""
        book = BookFactory()
        cls.book = book
        cls.reverse_path = reverse("books:delete", kwargs={"pk": book.pk})

    def test_if_get_response_contains_required_question_and_template(self):

        response = self.client.get(self.reverse_path, follow=True)
        self.assertContains(response, "Are you sure you want to delete")
        self.assertTemplateUsed(response, "books/book_confirm_delete.html")

    def test_template_name_and_redirect_path_after_book_delete(self):
        """Test if post request returns correct template and path."""

        response = self.client.post(self.reverse_path, follow=True)
        self.assertTemplateUsed(response, "books/list.html")
        self.assertRedirects(response, reverse("books:list"), status_code=302)

    def test_if_book_is_deleted(self):
        """Test if book was deleted after delete request."""

        self.client.delete(self.reverse_path)
        self.assertTrue(len(Book.objects.all()) == 0)
