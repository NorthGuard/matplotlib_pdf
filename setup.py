from setuptools import setup

setup(
    # Main
    name='matplotlib_pdf',
    version='0.1',
    license='MIT License',
    packages=["matplotlib_pdf"],

    # Requirements
    install_requires=["matplotlib", "PyPDF2", "reportlab"],

    # Display on PyPI
    author='Jeppe Nørregaard',
    description='Maintain a PDF-file with Matplotlib figures as pages.',
    keywords="matplotlib pdf figure",
    url='https://github.com/NorthGuard/pdf_pages',

    classifiers=[
        'Programming Language :: Python :: 3+',
    ],
)
