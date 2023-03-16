import warnings
from io import BytesIO
from pathlib import Path
from time import sleep

import matplotlib.pyplot as plt
from PyPDF2 import PdfFileWriter, PdfFileReader, PageObject
from PyPDF2.errors import PdfReadError

from .stampers import TimeStamper, Enumerator


class PDFFigureContainer:
    # noinspection PyTypeChecker
    def __init__(self, file_path, truncate_file=True, mk_dir=True):
        """
        Can maintain a PDF-file with Matplotlib figures in.
        Can update specific pages while maintaining the rest.
        Can be set to stamp pages with page-numbers and write-times.
        :param Path | str file_path: Path to put PDF-file with figures.
        :param bool truncate_file: Empty file at start. Otherwise keep pages.
        :param bool mk_dir: Make directory and parents if they don't exist.
        """
        # Temporary storage
        self._spool_storage = []

        # Time-stamping
        self._time_stamp_pages = False
        self._time_stamper = None  # type: TimeStamper

        # Number-stamping
        self._enumerate_pages = False
        self._enumerator = None  # type: Enumerator

        # Path to PDF-file
        self._file_path = Path(file_path)
        if mk_dir:
            self._file_path.parent.mkdir(parents=True, exist_ok=True)

        # Make writer
        self._writer = PdfFileWriter()
        if not truncate_file and file_path.is_file():
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

    def __len__(self):
        return self._full_length()

    def _file_length(self):
        return self._writer.getNumPages()

    def _full_length(self):
        return self._writer.getNumPages() + len(self._spool_storage)

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

    def commit(self, max_tries=5):
        """
        Update file with pages.
        Used if commit is set to False when adding pages, which buffers pages until commit() is called.
        """
        # Spool
        self._spool()

        # Write to file
        self._write_file(max_tries=max_tries)

    @staticmethod
    def figure2page(figure=None, bbox_inches="tight", facecolor=None, pause=None):
        """
        Add a page to figures-PDF.
        :param figure: Figure to put into PDF (defaults to plt.gcf()).
        :param str bbox_inches: Setting for making page tight. Passed onto pyplot.savefig().
        :param facecolor: Facecolor of page.
        :param pause: A floating-point for seconds to wait for matplotlib before saving page (otherwise figure may be
            saved before generated). If this is a problem, then a typical value would be 0.1.
        """
        if pause is not None:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
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

        return page

    def add_figure_page(self, page_nr=None, figure=None, commit=True,
                        bbox_inches="tight", facecolor=None, pause=None):
        """
        Convert matplotlib figure to page in PDF.
        :param int page_nr: Page number of page.
            None: Append page to file.
            int:  Replace specific page location with page.
        :param figure: Figure to put into PDF (defaults to plt.gcf()).
        :param bool commit: Commit page to PDF. If False then page is held in buffer until commit() is called.
        :param str bbox_inches: Setting for making page tight. Passed onto pyplot.savefig().
        :param facecolor: Facecolor of page.
        :param pause: A floating-point for seconds to wait for matplotlib before saving page (otherwise figure may be
            saved before generated). If this is a problem, then a typical value would be 0.1.
        """
        # Convert figure to page
        page = self.figure2page(figure=figure, bbox_inches=bbox_inches, facecolor=facecolor, pause=pause)

        # Add page
        return self.add_page(page=page, page_nr=page_nr, commit=commit)

    def add_page(self, page, page_nr=None, commit=True):
        """
        Add a page to PDF.
        :param PageObject page: Page
        :param int page_nr: Page number of page.
            None: Append page to file.
            int:  Replace specific page location with page.
        :param bool commit: Commit page to PDF. If False then page is held in buffer until commit() is called.
        """
        # Check for time-stamping
        if self._time_stamp_pages:
            self._time_stamper.do_stamp(page=page)

        # Ensure page number
        if page_nr is None:
            page_nr = self._full_length()

        # Check for page-enumeration
        if self._enumerate_pages:
            self._enumerator.do_stamp(page=page, page_nr=page_nr)

        # Add to spool
        self._spool_storage.append((page_nr, page))

        # Commit if needed
        if commit:
            self.commit()

        # Return page-nr for optional book-keeping
        return page_nr

    def _spool(self):
        # Single element in spool storage
        if len(self._spool_storage) == 1:
            page_nr, page = self._spool_storage[0]

            # Check for single page appended and append fast
            if page_nr == self._file_length():
                self._writer.addPage(page)

            # Otherwise insert specifically
            else:
                self._write_pages([page], [page_nr])

        # Multiple elements in spool storage
        else:
            # Split
            page_nrs = [page_nr for page_nr, _ in self._spool_storage]
            pages = [page for _, page in self._spool_storage]

            # All are appended
            temp = list(range(self._file_length(), self._full_length()))
            assert len(temp) == len(page_nrs)
            if page_nrs == temp:

                # Simply write to writer
                for _, page in self._spool_storage:
                    self._writer.addPage(page)

            # Otherwise insert specifically
            else:
                self._write_pages(pages, page_nrs)

        # Clear spool
        self._spool_storage = []

    def _write_pages(self, pages, page_nrs):
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

    def _write_file(self, max_tries):
        # Save to file - if exceptions are found, then make 5 attempts with a small time-delay
        try_nr = 0
        keep_trying = True
        while keep_trying:

            # Try to save
            try:

                # Save
                with self._file_path.open("wb") as output_stream:
                    self._writer.write(output_stream)

                # We are done
                keep_trying = False

            except PermissionError as e:
                # Check if exception should be raised
                if try_nr >= max_tries:
                    raise e

                # Sleep and update number of tries
                sleep(0.25)
                try_nr += 1
