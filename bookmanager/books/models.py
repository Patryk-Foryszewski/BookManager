"""Models for books and api apps.

Models list:
-Book

"""

import uuid

from django.conf.global_settings import LANGUAGES
from django.db import models
from django.utils.text import slugify
from isbn_field import ISBNField

from .utils import DEFAULT_COVER_URI


class TimeStamps(models.Model):
    created_date = models.DateField(auto_now_add=True)
    modified_date = models.DateField(auto_now=True)
    published_date = models.DateField(
        verbose_name="Date of publication",
    )

    class Meta:
        abstract = True


class Identifiers(models.Model):
    isbn_10 = ISBNField(
        null=True,
        verbose_name="ISBN_10",
        default="",
        blank=True,
    )
    isbn_13 = ISBNField(
        null=True,
        verbose_name="ISBN_13",
        default="",
        blank=True,
    )

    class Meta:
        abstract = True


class Book(TimeStamps, Identifiers):
    """Book model.

    Fields:
    -title (required) max-length=120,
    -author (required), max-length=120,
    -published (required), - date of publication in YYYY-MM-DD format
    -isbn_10 - ISBN_10 number
    -isbn_13 - ISBN_13 number
    -cover_uri - uri to cover image,
    -language - language of publication,
    -slug - slugified version of title
    """

    id = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, primary_key=True
    )
    title = models.CharField(max_length=120)
    author = models.CharField(max_length=100)
    pages = models.CharField(max_length=4, blank=True, default="")
    language = models.CharField(max_length=56, choices=LANGUAGES, blank=True)
    cover_uri = models.CharField(max_length=400, blank=True, default="")
    slug = models.SlugField(
        max_length=120,
    )

    def __repr__(self) -> str:
        """Return object representation."""
        return (
            f"{self.title}, {self.author}, {self.published_date}, {self.isbn_10}, "
            f"{self.isbn_13}, {self.cover_uri}, {self.language}"
        )

    def __str__(self) -> str:
        """Return f"{self.title}, {self.author}, {self.published}."""
        return f"{self.title}, {self.author}, {self.published_date}"

    @classmethod
    def from_db(cls, db, field_names, values):
        book = super().from_db(db, field_names, values)
        if not book.cover_uri:
            book.cover_uri = DEFAULT_COVER_URI

        return book

    def save(self, *args, **kwargs):
        """Create slug from book title and save."""
        self.slug = slugify(self.title)
        if self.cover_uri == DEFAULT_COVER_URI:
            self.cover_uri = ""
        self.full_clean()
        return super().save(*args, **kwargs)
