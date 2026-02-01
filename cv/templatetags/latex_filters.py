from django import template
from html import unescape
import re
from datetime import datetime

register = template.Library()

@register.filter(name='escape_latex')
def escape_latex(value):
    """
    Escape special LaTeX characters in a string
    First decodes HTML entities (like &amp; -> &), then escapes LaTeX special chars
    """
    if value is None:
        return ''
    
    value = str(value)
    
    # First, decode HTML entities (e.g., &amp; -> &, &lt; -> <, &gt; -> >)
    value = unescape(value)
    
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

@register.filter(name='escape_latex_url')
def escape_latex_url(value):
    """
    Prepare text for use in LaTeX URLs (href commands)
    URLs should NOT have LaTeX escaping - only decode HTML entities
    """
    if value is None:
        return ''
    
    value = str(value)
    
    # Only decode HTML entities - don't escape LaTeX special chars in URLs
    value = unescape(value)
    
    return value

@register.filter(name='format_date_str')
def format_date_str(value):
    """
    Format a date string (YYYY-MM-DD or other formats) to 'd M Y' (e.g., 1 Jan 2025).
    If it's 'Present' or empty, handle gracefully.
    """
    if not value:
        return ''
    
    value_str = str(value).strip()
    if value_str.lower() in ['present', 'current', 'now']:
        return 'Present'
    
    # Common formats to try
    formats = [
        '%Y-%m-%d',       # 2025-12-12
        '%d %B %Y',       # 1 December 2025
        '%d %b %Y',       # 1 Dec 2025
        '%B %Y',          # December 2025
        '%Y'              # 2025
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(value_str, fmt)
            # Linux %-d removes leading zero. Fallback to %d if issue, but %-d is preferred.
            try:
                return dt.strftime('%-d %b %Y')
            except ValueError:
                return dt.strftime('%d %b %Y').lstrip('0')
        except ValueError:
            continue
    
    # If parsing fails, return original
    return value

@register.filter(name='format_year_only')
def format_year_only(value):
    """
    Extract just the year from a date string.
    Input: "2025-12-12" -> "2025"
    "1 Jan 2025" -> "2025"
    "2024" -> "2024"
    """
    if not value:
        return ''
    
    val = str(value).strip()
    # Try getting 4 digits
    match = re.search(r'\d{4}', val)
    if match:
        return match.group(0)
    return val




























