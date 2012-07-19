from django import template

register = template.Library()

@register.filter(name='class')
def field_type(value):
    class_ = value.field.widget.attrs.get("class")
    if class_:
        return class_
    return ""
