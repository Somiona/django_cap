from django import template
from django.utils.safestring import mark_safe

from django_cap.django_app_settings import WIDGET_URL  # type: ignore

register = template.Library()


@register.simple_tag
def cap_widget_script():
    """
    Include the CAP widget script in the page head.
    Usage: {% cap_widget_script %}
    """
    return mark_safe(f'<script src="{WIDGET_URL}" async></script>')


@register.simple_tag
def cap_widget(
    widget_id="cap",
    api_endpoint="/cap/v1/",
    handler_function=None,
    hidden_field_name="cap-token",
):
    """
    Render a CAP widget with optional custom handler.

    Usage:
        {% cap_widget %}
        {% cap_widget widget_id="my-cap" %}
        {% cap_widget handler_function="myHandler" %}
        {% cap_widget hidden_field_name="cap_token" %}
    """
    onsolve_attr = ""
    if handler_function:
        onsolve_attr = f' onsolve="{handler_function}"'

    widget_html = f'<cap-widget id="{widget_id}" data-cap-api-endpoint="{api_endpoint}" data-cap-hidden-field-name="{hidden_field_name}"{onsolve_attr}></cap-widget>'

    return mark_safe(widget_html)


@register.filter
def cap_form_errors(form):
    """
    Extract CAP-specific error messages from form errors.
    Usage: {{ form|cap_form_errors }}
    """
    if not hasattr(form, "errors"):
        return []

    return [
        error
        for field_name, errors in form.errors.items()
        if "cap" in field_name.lower()
        for error in errors
    ]
