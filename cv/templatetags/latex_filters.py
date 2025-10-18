from django import template
import re

register = template.Library()

@register.filter(name='escape_latex')
def escape_latex(value):
    """
    Escape special LaTeX characters in a string
    """
    if value is None:
        return ''
    
    value = str(value)
    
    # Define LaTeX special characters and their escaped versions
    latex_special_chars = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\textasciicircum{}',
        '\\': r'\textbackslash{}',
    }
    
    # Replace each special character
    for char, escaped in latex_special_chars.items():
        value = value.replace(char, escaped)
    
    return value















