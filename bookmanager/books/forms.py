from django import forms
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


class GoogleSearchForm(forms.Form):
    search = forms.CharField(max_length=200, required=False)
    intitle = forms.CharField(max_length=200, required=False)
    inauthor = forms.CharField(max_length=200, required=False)

    def is_valid(self):
        return super().is_valid()
