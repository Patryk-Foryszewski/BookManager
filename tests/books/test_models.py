from contextlib import contextmanager

from django.core.exceptions import ValidationError
from django.test import TestCase

from bookmanager.books.models import Book
from bookmanager.books.utils import DEFAULT_COVER_URI


class ValidationErrorTestMixin(object):
    @contextmanager
    def assert_validation_errors(self, fields):
        """Validate required fields.

        Assert that a validation error is raised, containing all the specified
        fields, and only the specified fields.
        """
        try:
            yield
            raise AssertionError("ValidationError not raised")
        except ValidationError as e:
            self.assertEqual(set(fields), set(e.message_dict.keys()))


class CreateValidBook(TestCase):
    """Create book with valid data."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Create instance of Book model to perform tests."""

        Book.objects.create(
            title="Oczy Skóry",
            author="Juhani Pallasmaa",
            published_date="2008-10-15",
            isbn_10="",
            isbn_13="9788389192868",
            cover_uri="image.jpg",
            language="en",
        )
        cls.book = Book.objects.first()

    def test_repr(self):
        _repr = (
            "Oczy Skóry, Juhani Pallasmaa, 2008-10-15, , 9788389192868, image.jpg, en"
        )
        self.assertEqual(self.book.__repr__(), _repr)

    def test_str(self):
        _str = "Oczy Skóry, Juhani Pallasmaa, 2008-10-15"
        self.assertEqual(str(self.book), _str)

    def test_slug(self):
        self.assertEqual(self.book.slug, "oczy-skory")


class CreateInvalidBook(ValidationErrorTestMixin, TestCase):
    def test_book_must_have_title_and_author(self):
        book = Book(
            title="",
            author="",
            published_date="2008-10-15",
            pages="",
            isbn_10="",
            isbn_13="9788389192868",
            cover_uri="image.jpg",
            language="en",
        )

        with self.assert_validation_errors(["title", "author", "slug"]):
            book.full_clean()


class CreateBookWithoutCoverUri(ValidationErrorTestMixin, TestCase):
    def test_if_empty_cover_uri_is_equal_to_default_cover_uri(self):
        self.book = Book.objects.create(
            title="Oczy Skóry",
            author="Juhani Pallasmaa",
            published_date="2008-10-15",
            isbn_10="",
            isbn_13="9788389192868",
            cover_uri="",
            language="en",
        )
        book = Book.objects.first()
        self.assertEqual(book.cover_uri, DEFAULT_COVER_URI)


class CreateBookWithDefaulCoverURI(ValidationErrorTestMixin, TestCase):
    def test_if_empty_cover_uri_is_equal_to_default_cover_uri(self):
        self.book = Book.objects.create(
            title="Oczy Skóry",
            author="Juhani Pallasmaa",
            published_date="2008-10-15",
            isbn_10="",
            isbn_13="9788389192868",
            cover_uri=DEFAULT_COVER_URI,
            language="en",
        )
        book = Book.objects.first()
        self.assertEqual(book.cover_uri, DEFAULT_COVER_URI)
