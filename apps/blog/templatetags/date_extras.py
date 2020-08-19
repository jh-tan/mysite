from django import template
import calendar

register=template.Library()

@register.filter(name='month')
def month(value):
    return calendar.month_name[value]