"""URL routes for the ``apps.core`` app."""

from django.urls import path

from .views import HealthView

app_name = "core"

urlpatterns = [
    path("health/", HealthView.as_view(), name="health"),
]
