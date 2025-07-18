from django.urls import path

from .views import ContactView, index_page, success_page

urlpatterns = [
    # Example views demonstrating CAP form integration
    path("", index_page, name="cap_examles_index"),
    path("contact/", ContactView.as_view(), name="cap_contact"),
    path(
        "contact/success/",
        success_page,
        name="cap_contact_success",
    ),
]
