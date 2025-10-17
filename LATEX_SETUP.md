# LaTeX Setup Guide for CV PDF Generation

## What Changed

The CV PDF generation has been updated to use **LaTeX templates** instead of the Python `reportlab` library. This allows for much more professional and customizable PDF output that matches your desired design template.

## Installation Required

You need to install LaTeX on your system for PDF generation to work.

### Ubuntu/Debian Installation

Run the following commands in your terminal:

```bash
sudo apt-get update
sudo apt-get install -y texlive-latex-base texlive-latex-extra texlive-fonts-recommended texlive-latex-recommended
```

This will install:
- `texlive-latex-base` - Core LaTeX functionality
- `texlive-latex-extra` - Additional LaTeX packages
- `texlive-fonts-recommended` - Recommended fonts
- `texlive-latex-recommended` - Recommended LaTeX packages

### Verification

After installation, verify that LaTeX is installed:

```bash
which pdflatex
pdflatex --version
```

You should see the path to pdflatex and version information.

## How It Works

1. When a user requests to download their CV, the system renders the `cv/templates/cv.tex` template with the user's data
2. The rendered LaTeX content is saved to a temporary file
3. `pdflatex` is called twice to compile the `.tex` file into a PDF (twice ensures proper page numbering and references)
4. The generated PDF is moved to the `media/pdfs/` directory
5. The URL to the PDF is returned to the user

## Template Location

The LaTeX template is located at:
```
CV-Book-for-Cooperative-Department/cv/templates/cv.tex
```

You can edit this template to customize the CV design. The template uses Django template syntax for variable substitution and includes a custom `escape_latex` filter to safely escape special LaTeX characters in user input.

## Custom Template Filter

A custom Django template filter has been added to escape LaTeX special characters:
- Location: `cv/templatetags/latex_filters.py`
- Filter name: `escape_latex`
- Usage in template: `{{ variable|escape_latex }}`

This filter escapes characters like `&`, `%`, `$`, `#`, `_`, `{`, `}`, etc., which have special meaning in LaTeX.

## Troubleshooting

### Error: "pdflatex is not installed"

Install LaTeX as described above in the Installation section.

### Error: "LaTeX compilation failed"

1. Check the Django logs for detailed LaTeX error messages
2. Verify that the `.tex` template syntax is correct
3. Ensure all user input is properly escaped using the `|escape_latex` filter
4. Test the LaTeX template manually by copying the generated `.tex` file and running `pdflatex filename.tex`

### PDF not updating with new design

1. Delete existing PDFs in `media/pdfs/`
2. Clear any caching
3. Restart the Django development server:
   ```bash
   python manage.py runserver 127.0.0.1:8001
   ```

## Restart the Server

After installing LaTeX, restart your Django development server:

```bash
cd /home/user/UCA/CV-Book-for-Cooperative-Department
source venv/bin/activate
python manage.py runserver 127.0.0.1:8001
```

Now when you download a CV, it will use the beautifully designed LaTeX template!














