from datetime import datetime
from io import BytesIO

from PyPDF2 import PdfFileReader
from PyPDF2.pdf import PageObject
from reportlab.pdfgen.canvas import Canvas


def annotate_pdf_page(pdf_page, text, font_size=12,
                      h_offset=2, v_offset=2, position="nw",
                      char_w_factor=0.5, line_h_factor=1.35):
    """
    Put annotation on PDF-page and return the new page.
    :param PageObject pdf_page: Page for annotation.
    :param str text: String to write on page.
    :param int font_size: Self-explanatory.
    :param int h_offset: Offset in the horizontal direction from page edge.
        Used to put time-stamp nicely on page.
    :param int v_offset: Offset in the vertical direction from page edge.
        Used to put time-stamp nicely on page.
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
    :return: PageObject
    """
    # PDF size
    page_size = pdf_page.mediaBox
    height = int(page_size[3])
    width = int(page_size[2])

    # Number of lines and width of string
    n_lines = text.count("\n") + 1
    str_width = max([len(val) for val in text.split("\n")])

    # Font-size width- and height-factor
    char_width = font_size * char_w_factor
    line_height = line_h_factor * font_size

    # Left, middle, right and up, center, down
    left = h_offset
    middle = width/2 - 0.5 * str_width * char_width
    right = width - str_width * char_width
    up = height - font_size + v_offset
    center = height/2 - font_size + v_offset + (n_lines - 1) * line_height
    down = v_offset + (n_lines - 1) * line_height

    # Compute position coordinates
    position = position.lower()
    x, y = dict(
        n=(middle, up),
        nw=(left, up),
        w=(left, center),
        sw=(left, down),
        s=(middle, down),
        se=(right, down),
        e=(right, center),
        ne=(right, up),
    ).get(position, (h_offset, height - font_size + v_offset))
    x = int(x)
    y = int(y)

    # Create PDF for text
    packet = BytesIO()
    canvas = Canvas(packet, pagesize=page_size)
    canvas.setFontSize(font_size)

    # Add text
    draw_string(
        canvas=canvas,
        x=x,
        y=y,
        text=text)
    canvas.save()

    # Move to beginning of BytesIO and throw packet into reader
    packet.seek(0)
    new_pdf = PdfFileReader(packet)

    # Add text by merging pages
    pdf_page.mergePage(new_pdf.getPage(0))

    return pdf_page


def add_datetime_to_page(pdf_page, font_size=12,
                         h_offset=1, v_offset=0, header=None,
                         include_date=False, include_micro=False,
                         datetime_formatter=None, position="nw",
                         char_w_factor=0.5, line_h_factor=1.35):
    """
    Put datetime-stamp on page and return the new page.
    :param PageObject pdf_page: Page for annotation.
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
    :return: PageObject
    """
    # Formatting of time-stamp
    formatter = "%H:%M:%S"
    if include_date:
        formatter = "%d/%m/%Y  " + formatter
    if include_micro:
        formatter += ":%f"
    if datetime_formatter is not None:
        formatter = datetime_formatter

    # Get time-stamp
    text = datetime.now().strftime(formatter)

    # Add header
    if header is not None:
        text = header + "\n" + text

    # Mark page
    pdf_page = annotate_pdf_page(pdf_page=pdf_page,
                                 text=text,
                                 font_size=font_size,
                                 h_offset=h_offset,
                                 v_offset=v_offset,
                                 position=position,
                                 char_w_factor=char_w_factor,
                                 line_h_factor=line_h_factor)

    return pdf_page


def draw_string(canvas, x, y, text, mode=None, char_space=0):
    """
    Draws a string onto a reportlab Canvas.
    :param Canvas canvas: Canvas used for drawing string onto PDF.
    :param int x: Horizontal position.
    :param int y: Vertical position.
    :param str text: String to put on page.
    :param str mode: Mode passed to Canvas.setTextRenderMode()
    :param int char_space: Parameter passed to Canvas.setCharSpace()
    """
    t = canvas.beginText(x, y)
    if mode is not None:
        t.setTextRenderMode(mode)
    if char_space:
        t.setCharSpace(char_space)

    # Ensure line-breaks
    if isinstance(text, str):
        text = text.split("\n")
        t.textLines(text)
    else:
        t.textLines(text)

    if char_space:
        t.setCharSpace(0)
    if mode is not None:
        t.setTextRenderMode(0)

    canvas.drawText(t)
