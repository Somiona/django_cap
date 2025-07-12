from django.urls import include, path

from django_cap import views
from django_cap.django_app_settings import (
    DRF_API_ENABLED,  # type: ignore
    NINJA_API_ENABLED,  # type: ignore
)

if NINJA_API_ENABLED:
    from .ninja_api.views import cap_api

    urlpatterns = [
        # Django Ninja API (with automatic documentation)
        path("v1/", cap_api.urls),  # type: ignore
    ]
elif DRF_API_ENABLED:
    from .drf_api.views import cap_api  # type: ignore

    urlpatterns = [
        path("v1/", include(cap_api)),  # type: ignore
    ]
else:
    urlpatterns = [
        # Function-based views (matching cap.js endpoints)
        path("v1/challenge/", views.create_challenge, name="cap_create_challenge"),
        path("v1/redeem/", views.redeem_challenge, name="cap_redeem_challenge"),
        path("v1/validate/", views.validate_token, name="cap_validate_token"),
    ]
