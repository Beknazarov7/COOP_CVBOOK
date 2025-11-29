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
    # Define replacements - ORDER MATTERS!
    # We must replace backslash first to avoid escaping backslashes introduced by other replacements
    replacements = [
        ('\\', r'\textbackslash{}'),
        ('&', r'\&'),
        ('%', r'\%'),
        ('$', r'\$'),
        ('#', r'\#'),
        ('_', r'\_'),
        ('{', r'\{'),
        ('}', r'\}'),
        ('~', r'\textasciitilde{}'),
        ('^', r'\textasciicircum{}'),
    ]
    
    # Replace each special character
    for char, escaped in replacements:
        value = value.replace(char, escaped)
    
    return value




























