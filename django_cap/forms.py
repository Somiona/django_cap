"""
This module provides a simple way to add CAP (Proof of Work) verification
to any Django form.
"""

import asyncio
from typing import Any

from django import forms
from django.core.exceptions import ValidationError
from django.template import Context, Template

from django_cap.django_adapter import django_cap
from django_cap.django_app_settings import WIDGET_URL  # type: ignore


class CapWidget(forms.Widget):
    """
    Custom widget that renders the CAP widget using the cap_widget template tag.
    This serves as a reference for how to use the {% cap_widget %} tag programmatically.
    """

    def __init__(self, attrs=None, api_endpoint="/cap/v1/"):
        super().__init__(attrs)
        self.api_endpoint = api_endpoint

    class Media:
        js = (WIDGET_URL,)

    def render(self, name, value, attrs=None, renderer=None):
        """
        Render the CAP widget using the cap_widget template tag.
        This demonstrates how to use {% cap_widget %} programmatically.
        """
        widget_attrs = self.build_attrs(attrs or {})
        widget_id = widget_attrs.get("id", f"cap-widget-{name}")

        # Use the cap_widget template tag - this is the recommended approach
        template_str = """
        {% load django_cap %}
        {% cap_widget widget_id=widget_id api_endpoint=api_endpoint hidden_field_name=hidden_field_name %}
        """

        template = Template(template_str)
        context = Context(
            {
                "widget_id": widget_id,
                "api_endpoint": self.api_endpoint,
                "hidden_field_name": name,
            }
        )

        return template.render(context)


class CapField(forms.CharField):
    """
    CAP verification field that can be added to any Django form.

    Usage:
        class MyForm(forms.Form):
            name = forms.CharField(max_length=100)
            email = forms.EmailField()
            cap_token = CapField()  # Add CAP verification

    The field automatically:
    - Renders the CAP widget using the cap_widget template tag
    - Validates the proof-of-work token
    - Provides appropriate error messages
    - Creates its own hidden input via the CAP widget

    Just render it in templates like any other field:
        {{ form.cap_token }}
    """

    widget = CapWidget
    default_error_messages = {
        "required": "CAP verification is required.",
        "invalid_token": "CAP verification failed. Please try again.",
        "validation_error": "CAP verification error. Please try again.",
    }

    def __init__(self, *args, **kwargs):
        # Extract CAP-specific options
        self.keep_token = kwargs.pop("keep_token", False)
        self.api_endpoint = kwargs.pop("api_endpoint", "/cap/v1/")

        # Set widget with custom endpoint
        if "widget" not in kwargs:
            kwargs["widget"] = CapWidget(api_endpoint=self.api_endpoint)

        # Default values for CAP field
        kwargs.setdefault("required", True)
        kwargs.setdefault("label", "Verification")
        kwargs.setdefault("help_text", "Please try verification challenge again")

        super().__init__(*args, **kwargs)

    def validate(self, value):
        """Validate the CAP token."""
        super().validate(value)

        if value in self.empty_values:
            return

        # Use centralized validation
        result = self._validate_token_sync(value, self.keep_token)

        if not result.get("success", False):
            raise ValidationError(
                self.error_messages["invalid_token"],
                code="invalid_token",
            )

    def _validate_token_sync(
        self, token: str, keep_token: bool = False
    ) -> dict[str, Any]:
        """
        Synchronous wrapper for async token validation.
        """
        try:
            result = asyncio.run(
                django_cap.validate_token(token, keep_token=keep_token)
            )
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}
