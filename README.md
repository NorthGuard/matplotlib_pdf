# matplotlib_pdf
`matplotlib_pdf` can maintain a PDF-file with Matplotlib figures as pages.  
The container is initialized with a Path to a destination for putting the PDF-file with the figures.  
`container.add_figure_page()` is called to add current figure to PDF.

## Example
```python
# Make a container
container = PDFFigureContainer(Path(output_dir, "container.pdf"))

#
# Make a figure
#

# Add figure to pdf
container.add_figure_page()
```

## Additional Control
Additional options and uses are:
* The container can buffer many pages by calling `container.add_figure_page(commit=False)`, and them comiting them all to 
the file using `container.update_file()` (to avoid constantly updating the file). 
* You can specify figure with `add_figure_page(figure=fig)`. 

#### Experimental
* By running `container.set_timestamp()` before adding pages to a container, the container will add a time-stamp to 
each page, allowing reader to see what each page has last been updated 
(check documentation of method for options to `set_timestamp()`).
* By running `container.set_enumeration()` before adding pages to a container, the container will add an enumeration to
the pages (ex. `2 / 3`) (check documentation of method for options to `set_enumeration()`).

## Test-script
Running the `__main__.py`-script will make three figures and pass them all to a PDF-file. It then overwrites the second
page with a different figure. The end result is something like:  
![PDF-file example.][pdf_example]

[pdf_example]: https://github.com/NorthGuard/matplotlib_pdf/blob/master/matplotlib_pdf/pdf_container_example.PNG "PDF-file example."
