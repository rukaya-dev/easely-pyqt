import re

from PyQt6.QtCore import QSizeF
from PyQt6.QtGui import QTextDocument, QPageSize, QPageLayout
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog


def getOptionsNames(options_list):
    option_names = []
    if options_list:
        for option in options_list:
            option_names.append(option.name)
    else:
        return None

    return option_names


def zoom(html_content, zoom_type):
    pattern = r"(font-size:(\d+)pt)|(font-weight:(\d+))|(font-family:'([^']+)')"

    def adjust_font_properties(match):
        if match.group(1):
            if zoom_type == "zoom_in":
                new_size = int(match.group(2)) + 3
                return f'font-size:{new_size}pt'
            elif zoom_type == "zoom_out":
                new_size = int(match.group(2)) - 3
                return f'font-size:{new_size}pt'

        return match.group(0)

    modified_html = re.sub(pattern, adjust_font_properties, html_content)
    return modified_html


def preview_report(html_content):
    zoomed_out_html = zoom(html_content, "zoom_out")

    doc = QTextDocument()
    # doc.setDocumentMargin(20)

    # doc.setPageSize(QSizeF(753, 1080))
    doc.setHtml(zoomed_out_html)

    printer = QPrinter(QPrinter.PrinterMode.HighResolution)
    printer.setFullPage(True)
    printer.setResolution(300)
    printer.setOutputFormat(QPrinter.OutputFormat.NativeFormat)

    printer.setPaperSource(QPrinter.PaperSource.Auto)

    page_size = QPageSize(QPageSize.PageSizeId.A4)

    page_layout = QPageLayout()
    page_layout.setPageSize(page_size)
    page_layout.setOrientation(QPageLayout.Orientation.Portrait)
    page_layout.setUnits(QPageLayout.Unit.Millimeter)
    page_layout.setMode(QPageLayout.Mode.StandardMode)

    printer.setPageLayout(page_layout)

    print_dialog = QPrintDialog(printer)
    if print_dialog.exec() == QPrintDialog.DialogCode.Accepted:
        doc.print(printer)


def blockSignals(objects, b):
    for o in objects:
        o.blockSignals(b)
