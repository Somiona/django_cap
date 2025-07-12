"""
Simple example views showing easy CAP integration.
"""

from django import forms
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.urls import path, reverse_lazy
from django.views.generic import FormView

from django_cap.forms import CapField


class ContactForm(forms.Form):
    """Example contact form with CAP verification."""

    name = forms.CharField(
        max_length=100, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    email = forms.EmailField(widget=forms.EmailInput(attrs={"class": "form-control"}))
    subject = forms.CharField(
        max_length=200, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 5}),
        max_length=1000,
    )
    # Just add CapField - that's it!
    cap_token = CapField(label="", help_text="Please retry the verification challenge.")


class ContactView(FormView):
    """Contact form view with CAP verification."""

    template_name = "cap/examples/contact.html"
    form_class = ContactForm
    success_url = reverse_lazy("cap_contact_success")

    def get_success_message(self, cleaned_data):
        """Personalized success message for contact form."""
        name = cleaned_data.get("name", "")
        subject = cleaned_data.get("subject", "your message")
        return f'Thank you {name}! Your message "{subject}" has been sent successfully.'

    def form_valid(self, form):
        """Handle successful form submission."""
        success_message = self.get_success_message(form.cleaned_data)
        messages.success(self.request, success_message)

        # In a real application, you would:
        # - Send email notification
        # - Save to database
        # - Integrate with CRM
        # - Send auto-reply

        # For now, we'll just log the submission
        self._log_contact_submission(form.cleaned_data)

        return super().form_valid(form)

    def form_invalid(self, form):
        """Handle form validation errors with better CAP error messaging."""
        # Check for CAP-specific errors
        if "cap_token" in form.errors:
            messages.error(
                self.request,
                "Please complete the verification challenge to submit your form.",
            )
        else:
            messages.error(
                self.request,
                "Please correct the errors below and try again.",
            )
        return super().form_invalid(form)

    def _log_contact_submission(self, cleaned_data):
        """Log contact form submission (replace with actual processing)."""
        # This would typically involve:
        # - Sending email via Django's email backend
        # - Saving to a ContactSubmission model
        # - Triggering webhooks or API calls
        pass


def index_page(request: HttpRequest) -> HttpResponse:
    """Demo page showing different CAP integrations."""
    return render(request, "cap/examples/index.html")


def success_page(request: HttpRequest) -> HttpResponse:
    """Generic success page for form submissions."""
    return render(request, "cap/examples/success.html")


def contact_form_view(request: HttpRequest) -> HttpResponse:
    """Contact form with CAP verification."""
    return ContactView.as_view()(request)


urls = [
    # Example views demonstrating CAP form integration
    path("", index_page, name="cap_examles_index"),
    path("contact/", ContactView.as_view(), name="cap_contact"),
    path(
        "contact/success/",
        success_page,
        name="cap_contact_success",
    ),
]
