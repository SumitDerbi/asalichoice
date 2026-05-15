"""URL routes for the auth endpoints (mounted under ``/api/v1/auth/``)."""

from __future__ import annotations

from django.urls import path

from .views import LoginView, LogoutView, MeView, RefreshView

app_name = "users"

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("refresh/", RefreshView.as_view(), name="refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("me/", MeView.as_view(), name="me"),
]
