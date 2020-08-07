"""
matplotlib_pdf

matplotlib_pdf can maintain a PDF-file with Matplotlib figures as pages.
The container is initialized with a Path to a destination for putting the PDF-file with the figures.
container.add_figure_page() is called to add current figure to PDF.
"""

__version__ = "0.1.5"
__author__ = 'Jeppe Nørregaard'


from .pdf_figure_manager import PDFFigureContainer
