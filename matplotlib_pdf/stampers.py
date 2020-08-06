from .utility import add_datetime_to_page, annotate_pdf_page
from PyPDF2.pdf import PageObject


class PDFStamper:
    def __init__(self, font_size, h_offset, v_offset, position, char_w_factor, line_h_factor):
        """
        Object for stamping PDF-pages (putting some text on them).
        :param int font_size: Self-explanatory.
        :param int h_offset: Offset in the horizontal direction from page edge.
            Used to put enumeration nicely on page.
        :param int v_offset: Offset in the vertical direction from page edge.
            Used to put enumeration nicely on page.
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
        self.char_w_factor = char_w_factor
        self.line_h_factor = line_h_factor
        self.font_size = font_size
        self.h_offset = h_offset
        self.v_offset = v_offset
        self.position = position

    def _options_dict(self):
        """
        Returns options stored in stamper.
        :return: dict
        """
        return dict(
            font_size=self.font_size,
            h_offset=self.h_offset,
            v_offset=self.v_offset,
            position=self.position,
            char_w_factor=self.char_w_factor,
            line_h_factor=self.line_h_factor
        )

    def do_stamp(self, page, **kwargs):
        """
        Method for putting stamp on page.
        :param PageObject page: Page for stamp.
        :param kwargs:
        """
        raise NotImplementedError


class TimeStamper(PDFStamper):
    def __init__(self, font_size=12, h_offset=2, v_offset=2,
                 header=None, include_date=False, include_micro=False,
                 datetime_formatter=None, position="sw",
                 char_w_factor=0.5, line_h_factor=1.4):
        """
        Stamper which puts a time-stamp on pages.
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
        super().__init__(font_size=font_size, h_offset=h_offset, v_offset=v_offset, position=position,
                         char_w_factor=char_w_factor, line_h_factor=line_h_factor)

        self.include_date = include_date
        self.include_micro = include_micro
        self.header = header
        self.datetime_formatter = datetime_formatter

    def do_stamp(self, page, **kwargs):
        """
        Put stamp on page.
        :param PageObject page: Page for stamp.
        :param kwargs:
        """
        add_datetime_to_page(pdf_page=page,
                             header=self.header,
                             include_date=self.include_date,
                             include_micro=self.include_micro,
                             datetime_formatter=self.datetime_formatter,
                             **self._options_dict()
                             )


class Enumerator(PDFStamper):
    def __init__(self, font_size=12, h_offset=2, v_offset=2,
                 n_pages=None, header=None, position="se",
                 char_w_factor=0.5, line_h_factor=1.35):
        """
        Stamper which puts enumeration on pages.
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
        super().__init__(font_size=font_size, h_offset=h_offset, v_offset=v_offset, position=position,
                         char_w_factor=char_w_factor, line_h_factor=line_h_factor)

        self.header = header
        self.n_pages = n_pages
        self.nr = 0

    def reset(self, value=0):
        self.nr = value

    def do_stamp(self, page, page_nr=None, **kwargs):
        """
        Put stamp on page.
        :param PageObject page: Page for stamp.
        :param kwargs:
        """
        if page_nr is None:
            page_nr = self.nr
            self.nr += 1

        text = "" if self.header is None else (self.header + "\n")
        text += f"{page_nr+1}" if self.n_pages is None else f"{page_nr+1} / {self.n_pages}"

        annotate_pdf_page(pdf_page=page,
                          text=text,
                          **self._options_dict()
                          )