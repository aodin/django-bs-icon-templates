from django import template
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe


register = template.Library()


@register.simple_tag
def bs_icon(name: str, height: int = 16) -> str:
    """
    Render a Bootstrap Icon SVG inline.

    Usage::

        {% load bs_icons %}
        {% bs_icon "alarm" %}
        {% bs_icon "alarm" height=24 %}
    """
    template_name = f"bs_icon/{name}.svg"
    return mark_safe(render_to_string(template_name, {"height": height}))
