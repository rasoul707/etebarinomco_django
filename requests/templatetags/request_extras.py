from django import template
from django.contrib.humanize.templatetags.humanize import intcomma
from num2words import num2words

register = template.Library()

@register.filter(name='to_fawords')
def to_farsi_words(number):
    """
    این فیلتر، عدد را به حروف فارسی تبدیل می‌کند.
    """
    if number is None:
        return ""
    try:
        return num2words(int(number), lang='fa')
    except (ValueError, TypeError):
        return ""

@register.filter
def format_with_comma(number):
    """
    این فیلتر، به عدد کاما اضافه می‌کند.
    """
    if number is None:
        return ""
    return intcomma(number)
