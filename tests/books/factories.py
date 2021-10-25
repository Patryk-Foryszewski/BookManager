from datetime import date

from factory import Faker, Sequence
from factory.django import DjangoModelFactory

from bookmanager.books.models import Book


class BookFactory(DjangoModelFactory):
    class Meta:
        model = Book

    author = Faker("name")
    title = Sequence(lambda m: f"{m}")
    published_date = date(2021, 1, 1)
