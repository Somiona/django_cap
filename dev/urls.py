"""
URL configuration for core project.
"""

from django.conf import settings
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("cap/", include("django_cap.urls")),
    path("admin/", admin.site.urls),
    path("cap/examples/", include("django_cap.example.urls")),
]

if settings.DEBUG and not settings.TESTING:
    from debug_toolbar.toolbar import debug_toolbar_urls

    urlpatterns += debug_toolbar_urls()
