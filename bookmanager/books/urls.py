from django.urls import path

from .views import (
    BookCreateView,
    BookDeleteView,
    BookSearchListView,
    BookUpdateView,
    ImportBook,
    ImportList,
)

urlpatterns = [
    path("", BookSearchListView.as_view(), name="list"),
    path("add", BookCreateView.as_view(), name="add-form"),
    path("<str:pk>/update", BookUpdateView.as_view(), name="update"),
    path("<str:pk>/delete", BookDeleteView.as_view(), name="delete"),
    path("search", BookSearchListView.as_view(), name="search"),
    path("import-list", ImportList.as_view(), name="import-list"),
    path("import-book", ImportBook.as_view(), name="import-book"),
]
