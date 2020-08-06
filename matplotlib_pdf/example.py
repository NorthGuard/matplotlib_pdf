from pathlib import Path

import matplotlib.pyplot as plt

from matplotlib_pdf import PDFFigureContainer

plt.close("all")
plt.figure()
plt.ioff()

stamp_size = 9

# Directory for test figures
output_dir = Path(__file__).parent.parent

# Create PDF-figures container and enable time-stamping
container = PDFFigureContainer(Path(output_dir, "container.pdf"))
container.set_timestamp(font_size=stamp_size)
container.set_enumeration(n_pages=3, font_size=stamp_size)

# Create some figures and add to container
plt.scatter([1, 2, 3, 4, 5, 6, 7, 8, 9], [1, 9, 2, 8, 3, 7, 4, 6, 5])
container.add_figure_page()
plt.close("all")
plt.figure()
plt.scatter([1, 9, 2, 8, 3, 7, 4, 6, 5], [1, 2, 3, 4, 5, 6, 7, 8, 9])
container.add_figure_page()
plt.close("all")
plt.figure()
plt.scatter([1, 1, 1, 2, 3, 3, 3, 4, 5], [1, 2, 3, 3, 3, 2, 1, 1, 1])
container.add_figure_page()

# Delete container
del container

# Reopen container while keeping pages
container = PDFFigureContainer(Path(output_dir, "container.pdf"),
                               empty_file=False)
container.set_timestamp(True, header="Created:", font_size=stamp_size)
container.set_enumeration(n_pages=3, font_size=stamp_size)

# Overwrite second page
plt.close("all")
plt.figure()
plt.plot([1, 2, 3, 4, 5, 6, 5, 4, 3, 2, 1], [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])
container.add_figure_page(1)

# Print
print("Container at '{}' updated.".format(container.file_path))
