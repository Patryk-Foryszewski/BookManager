"""The `urlpatterns` list routes URLs to REST API views."""
from django.urls import path
from django.views.generic import RedirectView
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from .views import BooksDetail, BooksList, BooksSearch

schema_view = get_schema_view(
    openapi.Info(
        title="BookManager API",
        default_version="v1",
        description="API playground",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("", RedirectView.as_view(url="list")),
    path("list", BooksList.as_view(), name="list"),
    path("search", BooksSearch.as_view(), name="search"),
    path("detail/<str:pk>", BooksDetail.as_view(), name="detail"),
    path("docs", schema_view.with_ui(cache_timeout=0), name="docs"),
]
