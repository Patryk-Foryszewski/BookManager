from django.forms import DateTimeInput, ModelForm

from .models import Book


class BookAddEditForm(ModelForm):
    class Meta:
        model = Book
        fields = [
            "title",
            "author",
            "published_date",
            "isbn_10",
            "isbn_13",
            "pages",
            "cover_uri",
            "language",
        ]
        widgets = {
            "published_date": DateTimeInput(
                attrs={
                    "type": "date",
                    "class": "form-control datetimepicker-input",
                    "data-target": "#datetimepicker1",
                }
            )
        }
