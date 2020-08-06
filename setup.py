from setuptools import setup
from matplotlib_pdf import __version__

with open("pypi_description.md", "r") as fh:
    long_description = fh.read()

setup(
    # Main
    name='matplotlib_pdf',
    version=__version__,
    license='MIT License',
    packages=["matplotlib_pdf"],

    # Requirements
    install_requires=["matplotlib", "PyPDF2", "reportlab"],

    # Display on PyPI
    author='Jeppe Nørregaard',
    author_email="northguard_serve@tutanota.com",
    description='Maintain a PDF-file with Matplotlib figures as pages.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="matplotlib pdf figure",
    url='https://github.com/NorthGuard/matplotlib_pdf',

    classifiers=[
        'Programming Language :: Python :: 3',
    ],
    python_requires='>=3.0',
)
