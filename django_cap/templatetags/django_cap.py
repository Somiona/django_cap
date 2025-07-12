from django import template
from django.utils.safestring import mark_safe

from django_cap.django_app_settings import WIDGET_URL  # type: ignore

register = template.Library()


@register.simple_tag
def cap_widget_script():
    """
    Include this tag in the <head> section to load the CAP widget script.
    Usage: {% cap_widget_script %}
    """
    widget_url = WIDGET_URL
    return mark_safe(f'<script src="{widget_url}" async></script>')


@register.simple_tag
def cap_widget(widget_id="cap", api_endpoint="/cap/v1/", **kwargs):
    """
    Insert a CAP widget element with optional event handling.
    Usage:
        {% cap_widget %}
        {% cap_widget widget_id="my-cap" %}
        {% cap_widget api_endpoint="/custom/cap/endpoint/" %}
        {% cap_widget widget_id="cap-form" api_endpoint="/cap/v1/" with_handler=True %}
    """
    # Build the widget HTML
    widget_html = (
        f'<cap-widget id="{widget_id}" '
        f'data-cap-api-endpoint="{api_endpoint}"></cap-widget>'
    )

    # Add JavaScript event handler if requested
    if kwargs.get("with_handler", False):
        handler_script = f"""
<script>
    document.addEventListener('DOMContentLoaded', function() {{
        const widget = document.querySelector("#{widget_id}");
        if (widget) {{
            widget.addEventListener("solve", function(e) {{
                const token = e.detail.token;
                // Handle the token as needed
                console.log("CAP widget solved, token:", token);
            }});
        }}
    }});
</script>"""
        widget_html += handler_script

    return mark_safe(widget_html)


@register.simple_tag
def cap_widget_with_handler(
    widget_id="cap", api_endpoint="/cap/v1/", handler_function="handleCapSolve"
):
    """
    Insert a CAP widget with a custom JavaScript handler function.
    Usage:
        {% cap_widget_with_handler %}
        {% cap_widget_with_handler handler_function="myCustomHandler" %}
    """
    widget_html = (
        f'<cap-widget id="{widget_id}" '
        f'data-cap-api-endpoint="{api_endpoint}"></cap-widget>'
    )

    handler_script = f"""
<script>
    document.addEventListener('DOMContentLoaded', function() {{
        const widget = document.querySelector("#{widget_id}");
        if (widget) {{
            widget.addEventListener("solve", function(e) {{
                const token = e.detail.token;
                if (typeof {handler_function} === 'function') {{
                    {handler_function}(token, e);
                }} else {{
                    console.log("CAP widget solved, token:", token);
                }}
            }});
        }}
    }});
</script>"""

    widget_html += handler_script
    return mark_safe(widget_html)
