from pathlib import Path

import matplotlib.pyplot as plt

from matplotlib_pdf import PDFFigureContainer, _package_dir


def _make_figure(the_title):
    plt.figure()
    ax = plt.gca()  # type: plt.Axes
    ax.scatter([0.5], [0.35])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.text(0.5, 0.5, the_title, ha="center")


def test_w_pdf():
    n_standard_figure = 3
    n_late_commit_figures = 3
    n_pages_create_separately = 3
    n_stamped_figures = 3

    nr_replace = 1
    nr_replaced_w_stamp = 7

    correct_answers = []

    # Directory for PDF-file
    output_dir = Path(Path(_package_dir).parent, "tests", "results")
    output_dir.mkdir(exist_ok=True)
    for file in output_dir.glob("*"):
        file.unlink()
        
    # Path to file
    file_path = Path(output_dir, "test_file.pdf")
    
    # Create PDF to truncate
    init_pdf = PDFFigureContainer(file_path=file_path)
    _make_figure("Should not be shown")
    init_pdf.add_figure_page()
    assert len(init_pdf) == 1
    del init_pdf

    # Test reload
    init_pdf_reload = PDFFigureContainer(file_path=file_path, empty_file=False)
    assert len(init_pdf_reload) == 1
    del init_pdf_reload
    
    # Create PDF-figures container
    pdf = PDFFigureContainer(file_path=file_path)
    n_total = 0
    assert len(pdf) == n_total

    # Create some figures
    for nr in range(len(pdf) + 1, len(pdf) + 1 + n_standard_figure):
        title = f"Axes {nr}"
        correct_answers.append(title)
        _make_figure(title)
        pdf.add_figure_page()
        plt.close()

    n_total += n_standard_figure
    assert len(pdf) == n_total

    # Replace a figure
    title = f"Axes {nr_replace + 1} replaced"
    correct_answers[nr_replace] = title
    _make_figure(title)
    del title
    pdf.add_figure_page(page_nr=nr_replace)
    plt.close()

    assert len(pdf) == n_total

    # Add multiple, with later commit
    for nr in range(len(pdf) + 1, len(pdf) + 1 + n_late_commit_figures):
        title = f"Axes {nr}, made with postponed commit"
        correct_answers.append(title)
        _make_figure(title)
        pdf.add_figure_page(commit=False)
        plt.close()

    # noinspection PyProtectedMember
    assert pdf._writer.getNumPages() == n_total
    n_total += n_late_commit_figures
    pdf.commit()
    assert len(pdf) == n_total

    # Create pages first then add
    pages = []
    for nr in range(len(pdf) + 1, len(pdf) + 1 + n_pages_create_separately):
        title = f"Axes {nr} made as separate pages"
        correct_answers.append(title)
        _make_figure(title)
        pages.append(PDFFigureContainer.figure2page())
        plt.close()

    assert len(pdf) == n_total
    n_total += n_pages_create_separately
    for page in pages:
        pdf.add_page(page)
    assert len(pdf) == n_total

    # Enable time-stamping and page numbers
    pdf.set_timestamp(font_size=9)  # Put timestamp in corner
    pdf.set_enumeration(font_size=9)  # Put page number in corner

    for nr in range(len(pdf) + 1, len(pdf) + 1 + n_stamped_figures):
        title = f"Axes {nr}, with stamps [check the stamps]"
        correct_answers.append(title)
        _make_figure(title)
        pdf.add_figure_page()
        plt.close()

    n_total += n_standard_figure
    assert len(pdf) == n_total

    # Replace a figure with stampe
    title = f"Axes {nr_replaced_w_stamp + 1} replaced with stamps [check the stamps]"
    correct_answers[nr_replaced_w_stamp] = title
    _make_figure(title)
    del title
    pdf.add_figure_page(page_nr=nr_replaced_w_stamp)
    plt.close()

    assert len(pdf) == n_total
    del pdf

    # Test adding page with new object
    pdf_reload = PDFFigureContainer(file_path=file_path, empty_file=False)
    assert len(pdf_reload) == n_total
    title = "Appended page"
    correct_answers.append(title)
    _make_figure(title)
    pdf_reload.add_figure_page()
    n_total += 1
    assert len(pdf_reload) == n_total
    del title, pdf_reload

    # Print
    print("\n\nContainer at '{}' updated.".format(file_path))
    print("\nCheck that the pages have the following titles (and check information in []-brackets):")
    for title in correct_answers:
        print(f"\t{title}")

    # Ask tester for confirmation
    tester_answer = input("\nDoes all pages in PDF have the correct labels and stamps? y/[N]")
    assert tester_answer.lower() == "y"
    print("\nTests successful.\n")
