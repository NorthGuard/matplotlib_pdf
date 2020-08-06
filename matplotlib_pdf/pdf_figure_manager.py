from io import BytesIO
from pathlib import Path
from time import sleep

import matplotlib.pyplot as plt
from PyPDF2 import PdfFileWriter, PdfFileReader
from PyPDF2.pdf import PageObject
from PyPDF2.utils import PdfReadError

from .stampers import TimeStamper, Enumerator


class PDFFigureContainer:
    def __init__(self, file_path, empty_file=True):
        """
        Can maintain a PDF-file with Matplotlib figures in.
        Can update specific pages while maintaining the rest.
        Can be set to stamp pages with page-numbers and write-times.
        :param Path file_path: Path to put PDF-file with figures.
        :param bool empty_file: Empty file at start. Otherwise keep pages.
        """
        # Time-stamping
        self._time_stamp_pages = False
        self._time_stamper = None  # type: TimeStamper

        # Number-stamping
        self._enumerate_pages = False
        self._enumerator = None  # type: Enumerator

        # Path to PDF-file
        self._file_path = file_path

        # Make writer
        self._writer = PdfFileWriter()
        if not empty_file and file_path.is_file():
            try:
                reader = PdfFileReader(str(file_path))
                for page in reader.pages:
                    self._writer.addPage(page)

            except (OSError, PdfReadError):
                print("Unable to read PDF-file! Overwriting.")
                self._writer = PdfFileWriter()

    def __str__(self):
        return f"PDFFigureContainer({self._file_path})"

    def __repr__(self):
        return str(self)

    @property
    def file_path(self):
        return self._file_path

    def set_enumeration(self, enumerate_pages=True,
                        font_size=12, h_offset=2, v_offset=2,
                        n_pages=None, header=None, position="se",
                        char_w_factor=0.5, line_h_factor=1.35):
        """
        Set automatic enumeration of pages.
        :param bool enumerate_pages: Enable/disable enumeration.
        :param int font_size: Self-explanatory.
        :param int h_offset: Offset in the horizontal direction from page edge.
            Used to put enumeration nicely on page.
        :param int v_offset: Offset in the vertical direction from page edge.
            Used to put enumeration nicely on page.
        :param int n_pages: Total number of pages. None if total is not known.
        :param str header: String to print above page-number.
        :param str position: Position of enumeration on page.
            n : North edge.
            nw: North-west corner.
            w : West edge.
            sw: South-west corner.
            s : South edge.
            se: South-east corner.
            e : East edge.
            ne: North-east corner.
        :param float char_w_factor: Factor for approximating character-width from font-size.
            Used for aligning text horizontally.
        :param float line_h_factor: Factor for approximating line-height from font-size.
            Used for aligning text vertically.
        """
        self._enumerate_pages = enumerate_pages
        self._enumerator = Enumerator(
            font_size=font_size,
            h_offset=h_offset,
            v_offset=v_offset,
            n_pages=n_pages,
            header=header,
            position=position,
            char_w_factor=char_w_factor,
            line_h_factor=line_h_factor
        )

    def reset_enumeration(self, value=0):
        """
        Reset numbering for enumeration.
        :param int value: Value to set counter to.
            Defaults to zero.
        """
        if self._enumerator is None:
            self._enumerator = Enumerator()
        self._enumerator.reset(value=value)

    def set_timestamp(self, time_stamp_pages=True,
                      font_size=12, h_offset=2, v_offset=2,
                      header=None, include_date=False, include_micro=False,
                      datetime_formatter=None, position="sw",
                      char_w_factor=0.5, line_h_factor=1.6
                      ):
        """
        Set automatic time-stamping of pages.
        :param bool time_stamp_pages: Enable/disable time-stamping.
        :param int font_size: Self-explanatory.
        :param int h_offset: Offset in the horizontal direction from page edge.
            Used to put time-stamp nicely on page.
        :param int v_offset: Offset in the vertical direction from page edge.
            Used to put time-stamp nicely on page.
        :param str header: String to print above time-stamp.
        :param bool include_date: Include date in time-stamp.
        :param bool include_micro: Include microseconds in time-stamp.
        :param str datetime_formatter: Datetime formatter as specified by the datetime-package from Python.
        :param str position: Position of time-stamp on page.
            n : North edge.
            nw: North-west corner.
            w : West edge.
            sw: South-west corner.
            s : South edge.
            se: South-east corner.
            e : East edge.
            ne: North-east corner.
        :param float char_w_factor: Factor for approximating character-width from font-size.
            Used for aligning text horizontally.
        :param float line_h_factor: Factor for approximating line-height from font-size.
            Used for aligning text vertically.
        """
        self._time_stamp_pages = time_stamp_pages
        self._time_stamper = TimeStamper(
            font_size=font_size,
            h_offset=h_offset,
            v_offset=v_offset,
            header=header,
            include_date=include_date,
            include_micro=include_micro,
            datetime_formatter=datetime_formatter,
            position=position,
            char_w_factor=char_w_factor,
            line_h_factor=line_h_factor
        )

    def update_file(self, max_tries=5):
        """
        Update file with pages.
        Used if commit is set to False when adding pages, which buffers pages until update_file() is called.
        """
        try_nr = 0
        keep_trying = True
        while keep_trying:
            try:
                with self._file_path.open("wb") as output_stream:
                    self._writer.write(output_stream)
                keep_trying = False
                try_nr += 1
            except PermissionError as e:
                sleep(0.25)
                if try_nr >= max_tries:
                    raise e


    def add_figure_page(self, page_nr=None, figure=None, commit=True,
                        bbox_inches="tight", facecolor=None, pause=None):
        """
        Add a page to figures-PDF.
        :param int page_nr: Page number of page.
            None: Append page to file.
            int:  Replace specific page location with page.
        :param figure: Figure to put into PDF (defaults to plt.gcf()).
        :param bool commit: Commit page to PDF. If False then page is held in buffer until update_file() is called.
        :param str bbox_inches: Setting for making page tight. Passed onto pyplot.savefig().
        :param facecolor: Facecolor of page.
        :param pause: A floating-point for seconds to wait for matplotlib before saving page (otherwise figure may be
            saved before generated). If this is a problem, then a typical value would be 0.1.
        """
        if pause is not None:
            plt.pause(pause)

        # Default options
        options = dict(bbox_inches=bbox_inches)
        if facecolor is not None:
            options["facecolor"] = facecolor

        # Default figure-fetch
        if figure is None:
            figure = plt.gcf()

        # Save figure to buffer
        buf = BytesIO()
        figure.savefig(buf, format='pdf', **options)
        buf.seek(0)

        # Make PDF-page
        new_pdf = PdfFileReader(buf)
        page = new_pdf.getPage(0)

        # Check for time-stamping
        if self._time_stamp_pages:
            self._time_stamper.do_stamp(page=page)

        # Check for page-enumeration
        if self._enumerate_pages:
            if page_nr is None:
                page_nr = self._enumerator.nr
                self._enumerator.do_stamp(page=page)
            else:
                self._enumerator.do_stamp(page=page, page_nr=page_nr)

        # Add page
        if page_nr is not None or self._enumerate_pages:
            self._insert_page(page=page, page_nr=page_nr)
        else:
            self._writer.addPage(page)

        # Commit if needed
        if commit:
            self.update_file()

    def _insert_pages(self, pages, page_nrs):
        """
        Inserts a number of pages to file.
        :param list[PageObject] pages: Pages for file.
        :param list[int] page_nrs: Page-numbers of pages.
        """
        # Make dictionary mapping page-numbers to pages
        pages = {num: page for num, page in zip(page_nrs, pages)}

        # Write past-data from writer to reader
        reader = BytesIO()
        self._writer.write(reader)
        reader = PdfFileReader(reader)

        # Pages to scroll through
        n_pages = max(max(page_nrs) + 1, reader.getNumPages())

        # Make new writer and transfer pages
        self._writer = PdfFileWriter()
        for i in range(n_pages):
            # Replace page
            if i in pages:
                self._writer.addPage(pages[i])
            else:
                self._writer.addPage(reader.getPage(i))

    def _insert_page(self, page, page_nr):
        """
        Inserts one page into file.
        :param PageObject page: Page for file.
        :param int page_nr: Page-number of page.
        """
        self._insert_pages([page], [page_nr])
