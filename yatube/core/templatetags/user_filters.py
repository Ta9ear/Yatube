from django import template

register = template.Library()


@register.filter
def addclass(field, css):
    """
    Defines class in the input tag
    """
    return field.as_widget(attrs={'class': css})
