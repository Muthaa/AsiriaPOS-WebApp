from django import template

register = template.Library()

@register.filter
def field_css(form, field_name):
    if form.errors.get(field_name):
        return 'form-control is-invalid'
    return 'form-control' 