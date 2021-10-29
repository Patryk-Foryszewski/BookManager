from django.urls import path

import bookmanager.core.views as views

urlpatterns = [
    path("400", views.handle_400, name="handle-400"),
    path("404", views.handle_404, name="handle-404"),
]
