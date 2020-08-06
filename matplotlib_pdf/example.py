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
container.set_timestamp(font_size=stamp_size)  # Put timestamp in corner
container.set_enumeration(n_pages=3, font_size=stamp_size)  # Put page number in corner

# Create some figures and add to container

# Figure 1
plt.scatter([1, 2, 3, 4, 5, 6, 7, 8, 9], [1, 9, 2, 8, 3, 7, 4, 6, 5])
container.add_figure_page()

# Figure 2
plt.figure()
plt.plot([1, 2, 3, 4, 5, 6, 5, 4, 3, 2, 1], [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])
container.add_figure_page()

# Figure 2 3
plt.figure()
plt.scatter([1, 1, 1, 2, 3, 3, 3, 4, 5], [1, 2, 3, 3, 3, 2, 1, 1, 1])
container.add_figure_page()
plt.close("all")

# Print
print("Container at '{}' updated.".format(container.file_path))
