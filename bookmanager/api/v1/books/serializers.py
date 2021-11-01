from rest_framework import serializers

from bookmanager.books.models import Book


class BookSerializer(serializers.ModelSerializer):
    """Book serializer for all fields."""

    class Meta:
        model = Book
        fields = [
            "id",
            "title",
            "author",
            "published_date",
            "isbn_10",
            "isbn_13",
            "pages",
            "cover_uri",
            "language",
        ]
