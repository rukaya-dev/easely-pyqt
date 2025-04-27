import datetime
import os

from PyQt6.QtCore import Qt, QMarginsF, QUrl, QSizeF
from PyQt6.QtGui import QPainter, QPageLayout, QPageSize, QTextDocument, QTextImageFormat, QTextCursor, \
    QTextTableCellFormat, QTextBlockFormat, QTextLength, QColor, QTextTableFormat, QTextCharFormat
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QFrame, QSizePolicy, QSpacerItem, \
    QTextEdit

from loggers.logger_configs import set_up_logger
from utils.utlis import extract_file_extension
from views.componenets.customsComponents.circular_avatar import mask_image
from views.componenets.customsComponents.custom_scroll_area import CustomScrollArea
from views.componenets.customsComponents.table.save_and_cancel_buttons import SaveAndCancelButtonsWithLoader

logger = set_up_logger('main.views.billing.create_billing_dialog')

resource_dir = "resources/images"
placeholder_image = "placeholder.jpg"


class InvoiceDialog(QDialog):
    def __init__(self, data, parent=None):
        super().__init__(parent)

        self.parent = parent
        self.data = data

        self.form_widget = self.FormWidget(data=self.data)

        central_widget = QWidget()

        main_v_layout = QVBoxLayout(central_widget)
        main_v_layout.setContentsMargins(0, 0, 0, 0)
        main_v_layout.setSpacing(0)
        main_v_layout.addWidget(self.form_widget)

        scroll_area = CustomScrollArea(self)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setWidget(central_widget)

        self.save_and_cancel_btns = SaveAndCancelButtonsWithLoader(text="Print")
        self.save_and_cancel_btns.save_btn.clicked.connect(self.print_invoice)
        self.save_and_cancel_btns.cancel_btn.clicked.connect(self.close)

        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(10)
        controls_layout.setContentsMargins(30, 20, 30, 20)
        controls_layout.addWidget(self.save_and_cancel_btns, 1, Qt.AlignmentFlag.AlignRight)

        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(scroll_area)
        layout.addLayout(controls_layout, Qt.AlignmentFlag.AlignRight)

        self.setLayout(layout)
        self.setFixedSize(900, 700)

    def print_invoice(self):
        self.save_and_cancel_btns.save_btn.start()
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        printer.setFullPage(True)
        printer.setResolution(300)
        printer.setOutputFormat(QPrinter.OutputFormat.NativeFormat)

        printer.setPaperSource(QPrinter.PaperSource.Auto)

        page_layout = QPageLayout()
        page_layout.setMargins(QMarginsF(12, 12, 12, 12))
        page_layout.setUnits(QPageLayout.Unit.Millimeter)
        page_layout.setOrientation(QPageLayout.Orientation.Portrait)
        page_layout.setMode(QPageLayout.Mode.StandardMode)
        page_size = QPageSize(QPageSize.PageSizeId.A4)
        page_layout.setPageSize(page_size)
        printer.setPageLayout(page_layout)

        print_dialog = QPrintDialog(printer, self.form_widget)
        if print_dialog.exec() == QPrintDialog.DialogCode.Accepted:
            painter = QPainter()
            painter.begin(printer)

            painter.setRenderHints(QPainter.RenderHint.LosslessImageRendering, on=True)

            w = printer.pageRect(QPrinter.Unit.DevicePixel).width() / float(self.form_widget.width())
            h = printer.pageRect(QPrinter.Unit.DevicePixel).height() / float(self.form_widget.height())
            scale = min(w, h)

            painter.scale(scale, scale)
            self.form_widget.render(painter)
            painter.end()

        self.save_and_cancel_btns.save_btn.stop()

    class FormWidget(QWidget):
        def __init__(self, data, parent=None):
            super().__init__(parent)

            name_and_logo_layout = QVBoxLayout()
            name_and_logo_layout.setContentsMargins(0, 0, 0, 0)
            name_and_logo_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            name_and_logo_layout.setSpacing(10)

            name_label = QLabel(data["name"])
            name_label.setFixedHeight(30)
            name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            name_label.setStyleSheet(" QLabel { border:0; color:black}")

            name_font = name_label.font()
            name_font.setStyleStrategy(name_font.StyleStrategy.PreferQuality)
            name_font.setWeight(name_font.Weight.Bold)
            name_font.setPointSize(18)
            name_label.setFont(name_font)

            name_and_logo_layout.addWidget(name_label, 0)

            placeholder_path = os.path.abspath(os.path.join(os.getcwd(), resource_dir, placeholder_image))

            if data["logo_image_path"] and data["logo_image_path"] != placeholder_path:
                file_extension = extract_file_extension(data["logo_image_path"])

                pixmap = mask_image(data["logo_image_data"], img_type=file_extension.replace(".", ""),
                                    border=True, border_color="#E9E9E9")

                self.logo = QLabel()
                self.logo.setAlignment(Qt.AlignmentFlag.AlignHCenter)
                self.logo.setPixmap(pixmap)

                name_and_logo_layout.addWidget(self.logo)
            # ------------------------------------------------------------------------------

            clinic_description = self.KeyValueWidget(key="", value=data["services_offered"])
            clinic_address = self.KeyValueWidget(key="", value=data["address"])

            mobile_number = self.KeyValueWidget(key="Mobile", value=data["phone_number"])

            fax_number = self.KeyValueWidget(key="Fax", value=data["fax_number"])

            mobile_fax_number_layout = QVBoxLayout()
            mobile_fax_number_layout.setSpacing(15)
            mobile_fax_number_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

            mobile_fax_number_layout.addWidget(mobile_number)
            mobile_fax_number_layout.addWidget(fax_number)

            website = self.KeyValueWidget(key="Website", value=data["website"])
            email = self.KeyValueWidget(key="Email", value=data["email"])

            clinic_info_line_seperator = QFrame()
            clinic_info_line_seperator.setFrameShape(QFrame.Shape.HLine)
            clinic_info_line_seperator.setFrameShadow(QFrame.Shadow.Plain)
            clinic_info_line_seperator.setLineWidth(2)

            clinic_information_layout = QVBoxLayout()
            clinic_information_layout.setSpacing(10)
            clinic_information_layout.setContentsMargins(0, 0, 0, 0)
            clinic_information_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

            clinic_information_layout.addWidget(clinic_description)
            clinic_information_layout.addWidget(clinic_address)
            clinic_information_layout.addLayout(mobile_fax_number_layout)
            clinic_information_layout.addWidget(website)
            clinic_information_layout.addWidget(email)
            clinic_information_layout.addWidget(clinic_info_line_seperator)
            # ------------------------------------------------------------------------------

            invoice_number = self.KeyValueWidget(key="Invoice", value=data["billing_id"])

            invoice_date = self.KeyValueWidget(key="Invoice Date ",
                                               value=datetime.datetime.fromisoformat(data["created_at"]).strftime(
                                                   "%a, %B %d, %Y"))
            invoice_due_date = self.KeyValueWidget(key="Due Date",
                                                   value=datetime.datetime.fromisoformat(data["created_at"]).strftime(
                                                       "%a, %B %d, %Y"))

            invoice_number_and_date_layout = QVBoxLayout()
            invoice_number_and_date_layout.setSpacing(15)
            invoice_number_and_date_layout.setContentsMargins(0, 0, 0, 0)
            invoice_number_and_date_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

            invoice_number_and_date_layout.addWidget(invoice_number)
            invoice_number_and_date_layout.addWidget(invoice_date)
            invoice_number_and_date_layout.addWidget(invoice_due_date)

            clinic_information_invoice_layout = QHBoxLayout()
            clinic_information_invoice_layout.setSpacing(20)
            clinic_information_invoice_layout.setContentsMargins(0, 10, 0, 10)

            spacer = QSpacerItem(20, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

            clinic_information_invoice_layout.addLayout(clinic_information_layout)
            clinic_information_invoice_layout.addSpacerItem(spacer)
            clinic_information_invoice_layout.addLayout(invoice_number_and_date_layout)

            clinic_logo_invoice_upper_layout = QVBoxLayout()
            clinic_logo_invoice_upper_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
            clinic_logo_invoice_upper_layout.setSpacing(0)
            clinic_logo_invoice_upper_layout.setContentsMargins(0, 0, 0, 0)

            clinic_logo_invoice_upper_layout.addLayout(name_and_logo_layout)
            clinic_logo_invoice_upper_layout.addLayout(clinic_information_invoice_layout)
            # ------------------------------------------------------------------------------

            patient_name = self.KeyValueWidget(key="Customer Name",
                                               value=data["patient_firstname"] + " " + data["patient_lastname"])

            patient_address = self.KeyValueWidget(key="Customer Address", value=data["patient_address"])

            patient_phone_number = self.KeyValueWidget(key="Customer Phone number", value=data["patient_phone_number"])

            patient_information_layout = QVBoxLayout()
            patient_information_layout.setSpacing(10)
            patient_information_layout.setContentsMargins(0, 20, 0, 20)

            patient_information_layout.addWidget(patient_name)
            patient_information_layout.addWidget(patient_address)
            patient_information_layout.addWidget(patient_phone_number)

            patient_info_line_seperator = QFrame()
            patient_info_line_seperator.setFrameShape(QFrame.Shape.HLine)
            patient_info_line_seperator.setFrameShadow(QFrame.Shadow.Plain)
            patient_info_line_seperator.setLineWidth(2)
            # ------------------------------------------------------------------------------

            service_name = self.KeyValueWidget(key="Service", expandable=0, value=data["service_name"])

            payment_method = self.KeyValueWidget(key="Payment Method", expandable=0, value=data["payment_method"])

            total_price = self.KeyValueWidget(key="Total Amount", expandable=0, value=data["total_amount"])

            discount = self.KeyValueWidget(key="Discount", expandable=0, value=data["coverage_percentage"])

            net_amount = self.KeyValueWidget(key="Net Amount", expandable=0, value=data["net_amount"])

            service_information_layout = QVBoxLayout()
            service_information_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
            service_information_layout.setSpacing(10)
            service_information_layout.setContentsMargins(0, 0, 0, 0)

            service_information_layout.addWidget(payment_method)
            service_information_layout.addWidget(service_name)
            service_information_layout.addWidget(total_price)
            service_information_layout.addWidget(discount)
            service_information_layout.addWidget(net_amount)

            patient_and_service_information_layout = QVBoxLayout()
            patient_and_service_information_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
            patient_and_service_information_layout.setSpacing(20)
            patient_and_service_information_layout.setContentsMargins(0, 0, 0, 0)

            patient_and_service_information_layout.addLayout(patient_information_layout)
            patient_and_service_information_layout.addWidget(patient_info_line_seperator)
            patient_and_service_information_layout.addLayout(service_information_layout)

            main_v_layout = QVBoxLayout()
            main_v_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
            main_v_layout.setSpacing(0)
            main_v_layout.setContentsMargins(30, 0, 30, 0)

            main_v_layout.addLayout(clinic_logo_invoice_upper_layout)
            main_v_layout.addLayout(patient_and_service_information_layout)

            central_widget = QWidget()
            central_widget.setStyleSheet("""
                QFrame {
                    color:#262626;
                }
            """)
            central_widget.setLayout(main_v_layout)

            main_v_layout = QVBoxLayout()
            main_v_layout.setContentsMargins(20, 20, 20, 20)
            main_v_layout.setSpacing(0)
            main_v_layout.addWidget(central_widget)

            self.setLayout(main_v_layout)

        class KeyValueWidget(QWidget):
            def __init__(self, key, value, expandable=1, parent=None):
                super().__init__(parent)

                stylesheet = """
                QLabel {
                    border:0;
                    color:#262626;
                }
                """

                main_layout = QHBoxLayout()
                main_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
                main_layout.setContentsMargins(0, 0, 0, 0)
                main_layout.setSpacing(0)

                if key:
                    key_label = QLabel(key + " :     ")
                    key_label.setStyleSheet(stylesheet)
                    main_layout.addWidget(key_label, 0)

                value = QLabel(str(value))
                value.setWordWrap(True)
                value.setAlignment(Qt.AlignmentFlag.AlignLeft)
                value.setStyleSheet(stylesheet)

                main_layout.addWidget(value, expandable)

                layout = QVBoxLayout()
                layout.setContentsMargins(0, 0, 0, 0)
                layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

                layout.addLayout(main_layout)

                self.setLayout(layout)


class ViewInvoiceDialog(QDialog):
    def __init__(self, data, parent=None):
        super().__init__(parent)

        self.parent = parent
        self.data = data

        self.line_break = "<br></br>"

        self.text_edit = QTextEdit(parent=self)
        self.text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.text_edit.setFixedSize(793, 1122)
        self.text_edit.setStyleSheet("""
                QTextEdit {
                     background-color:white;
                     color:black;
                }

            """)

        self.text_edit.setFontPointSize(12)
        self.text_edit.setFontWeight(500)

        self.doc = self.text_edit.document()
        self.doc.setDocumentMargin(20)
        self.doc.setPageSize(QSizeF(753, 1080))

        placeholder_path = os.path.abspath(os.path.join(os.getcwd(), resource_dir, placeholder_image))
        temp_logo_path = os.path.abspath(os.path.join(os.getcwd(), resource_dir, "temp_clinic_logo.jpg"))

        if data["logo_image_path"] and data["logo_image_path"] != placeholder_path:
            file_extension = extract_file_extension(data["logo_image_path"])
            pixmap = mask_image(data["logo_image_data"], img_type=file_extension.replace(".", ""), border=True,
                                border_color="#E9E9E9")
        else:
            pixmap = self.prepare_place_holder()

        pixmap.save(temp_logo_path)
        self.insert_clinic_data(QUrl(temp_logo_path), pixmap, self.data)
        # ------------------------------------------------------------------------------

        self.insert_patient_data(data)

        scroll_area = CustomScrollArea(self)
        scroll_area.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setWidget(self.text_edit)

        central_widget = QWidget()
        central_widget.setObjectName("view_report_text_edit_central_widget")
        central_widget.setStyleSheet("""
              QWidget#view_report_text_edit_central_widget {
                  border:0;      
              }


            """)

        main_v_layout = QVBoxLayout(central_widget)
        main_v_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        main_v_layout.setContentsMargins(30, 20, 30, 20)
        main_v_layout.addWidget(scroll_area, 1)

        self.save_and_cancel_btns = SaveAndCancelButtonsWithLoader(text="Print")
        self.save_and_cancel_btns.save_btn.clicked.connect(self.print)
        self.save_and_cancel_btns.cancel_btn.clicked.connect(self.close)

        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(10)
        controls_layout.setContentsMargins(30, 20, 30, 20)
        controls_layout.addWidget(self.save_and_cancel_btns, 1, Qt.AlignmentFlag.AlignRight)

        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(central_widget)
        layout.addLayout(controls_layout, Qt.AlignmentFlag.AlignRight)

        self.setLayout(layout)
        self.setMinimumSize(1000, 768)

        self.setStyleSheet("border:0;background-color:#f8f8f8;")

    def insert_patient_data(self, data):

        self.text_edit.insertHtml(self.line_break)
        self.text_edit.insertHtml(self.line_break)

        cursor = self.text_edit.textCursor()

        # table format
        table_format = QTextTableFormat()
        table_format.setCellPadding(5)
        table_format.setCellSpacing(0)
        table_format.setBorder(1)
        table_format.setBorderStyle(QTextTableFormat.BorderStyle.BorderStyle_Solid)
        table_format.setBorderBrush(QColor("lightgray"))
        table_format.setAlignment(Qt.AlignmentFlag.AlignRight)
        table_format.setBorderCollapse(True)

        # column width constraints
        thirty_five_percent = QTextLength(QTextLength.Type.PercentageLength, 35)
        thirty_percent = QTextLength(QTextLength.Type.PercentageLength, 30)

        constraints = [thirty_five_percent, thirty_five_percent, thirty_percent]
        table_format.setColumnWidthConstraints(constraints)

        # alignment format for the second column
        align_right_format = QTextBlockFormat()
        align_right_format.setAlignment(Qt.AlignmentFlag.AlignLeading)

        align_left_format = QTextBlockFormat()
        align_left_format.setAlignment(Qt.AlignmentFlag.AlignLeft)

        align_center_format = QTextBlockFormat()
        align_center_format.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        # Define a cell format with no border
        no_border_format = QTextTableCellFormat()
        no_border_format.setLeftBorder(0)
        no_border_format.setRightBorder(0)
        no_border_format.setTopBorder(0)
        no_border_format.setBottomBorder(0)

        cell_font = no_border_format.font()
        cell_font.setPointSize(12)
        cell_font.setWeight(cell_font.Weight.Medium)
        no_border_format.setFont(cell_font)

        patient_table = cursor.insertTable(2, 3, table_format)

        first_col_cells_data = [
            "Customer Address",
            data['patient_firstname'] + ' ' + data['patient_lastname']
        ]

        second_col_cells_data = [
            "Customer Name",
            data['patient_address']
        ]

        for row, text in enumerate(first_col_cells_data):
            cursor = patient_table.cellAt(row, 0).firstCursorPosition()
            cursor.insertText(text, no_border_format)

        for row, text in enumerate(second_col_cells_data):
            cursor = patient_table.cellAt(row, 1).firstCursorPosition()
            cursor.insertText(text, no_border_format)

        third_col_cells_data = [
            "Customer Phone number",
            data['patient_phone_number']
        ]

        for row, text in enumerate(third_col_cells_data):
            cursor = patient_table.cellAt(row, 2).firstCursorPosition()
            cursor.mergeBlockFormat(align_right_format)
            cursor.insertText(text, no_border_format)

        cursor.movePosition(QTextCursor.MoveOperation.End)

        cursor.insertBlock()

        block_fmt = cursor.blockFormat()
        char_fmt = QTextCharFormat()
        char_fmt.setFontPointSize(12)
        char_fmt.setFontWeight(500)

        block_fmt.clearProperty(QTextBlockFormat.Property.BlockTrailingHorizontalRulerWidth)
        cursor.setBlockFormat(block_fmt)

        self.text_edit.insertHtml(self.line_break)
        self.text_edit.insertHtml(self.line_break)

        payment_table_format = QTextTableFormat()
        payment_table_format.setCellPadding(5)
        payment_table_format.setCellSpacing(0)
        payment_table_format.setBorder(1)
        payment_table_format.setBorderStyle(QTextTableFormat.BorderStyle.BorderStyle_Solid)
        payment_table_format.setBorderBrush(QColor("lightgray"))
        payment_table_format.setAlignment(Qt.AlignmentFlag.AlignRight)
        payment_table_format.setBorderCollapse(True)

        # column width constraints
        twenty_percent = QTextLength(QTextLength.Type.PercentageLength, 20)
        thirty_five_percent = QTextLength(QTextLength.Type.PercentageLength, 35)
        fifteen_percent = QTextLength(QTextLength.Type.PercentageLength, 15)

        constraints = [thirty_five_percent, twenty_percent, fifteen_percent, fifteen_percent, fifteen_percent]
        payment_table_format.setColumnWidthConstraints(constraints)

        payment_table = cursor.insertTable(2, 5, payment_table_format)

        first_col_cells_data = [
            "Service",
            data['service_name']
        ]

        for row, text in enumerate(first_col_cells_data):
            cursor = payment_table.cellAt(row, 0).firstCursorPosition()
            cursor.insertText(text, no_border_format)

        second_col_cells_data = [
            "Payment Method",
            data['payment_method']
        ]

        for row, text in enumerate(second_col_cells_data):
            cursor = payment_table.cellAt(row, 1).firstCursorPosition()
            cursor.insertText(text, no_border_format)

        third_col_cells_data = [
            "Total Amount",
            str(data['total_amount'])
        ]

        for row, text in enumerate(third_col_cells_data):
            cursor = payment_table.cellAt(row, 2).firstCursorPosition()
            cursor.mergeBlockFormat(align_right_format)
            cursor.insertText(text, no_border_format)

        forth_col_cells_data = [
            "Discount %",
            str(data['coverage_percentage'])
        ]

        for row, text in enumerate(forth_col_cells_data):
            cursor = payment_table.cellAt(row, 3).firstCursorPosition()
            cursor.mergeBlockFormat(align_right_format)
            cursor.insertText(text, no_border_format)

        fifth_col_cells_data = [
            "Net Amount",
            str(data['net_amount'])
        ]

        for row, text in enumerate(fifth_col_cells_data):
            cursor = payment_table.cellAt(row, 4).firstCursorPosition()
            cursor.mergeBlockFormat(align_right_format)
            cursor.insertText(text, no_border_format)

    def load_image(self, data):
        placeholder_path = os.path.abspath(os.path.join(os.getcwd(), resource_dir, placeholder_image))
        temp_logo_path = os.path.abspath(os.path.join(os.getcwd(), resource_dir, "temp_clinic_logo.jpg"))

        if data["logo_image_path"] and data["logo_image_path"] != placeholder_path:
            file_extension = extract_file_extension(data["logo_image_path"])
            pixmap = mask_image(data["logo_image_data"], img_type=file_extension.replace(".", ""),
                                border=True,
                                border_color="#E9E9E9")
        else:
            pixmap = self.prepare_place_holder()

        pixmap.save(temp_logo_path)
        self.insert_clinic_data(QUrl(temp_logo_path), pixmap, self.data)

    def print(self):

        doc = self.doc
        self.doc.setPageSize(QSizeF(753, 1080))

        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        printer.setFullPage(True)
        printer.setResolution(300)
        printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)

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

    def prepare_place_holder(self):
        placeholder_path = os.path.abspath(os.path.join(os.getcwd(), resource_dir, placeholder_image))
        with open(placeholder_path, 'rb') as f:
            image_bytes = f.read()
            pixmap = mask_image(image_bytes, img_type="jpg", border=True, border_color="#E9E9E9")
            return pixmap

    def insert_clinic_data(self, uri, image, data):

        self.text_edit.document().addResource(QTextDocument.ResourceType.ImageResource, uri, image)

        cursor = self.text_edit.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.NextBlock)

        image_format = QTextImageFormat()
        image_format.setWidth(image.width())
        image_format.setHeight(image.height())
        image_format.setName(uri.toString())

        cursor = self.text_edit.textCursor()

        # table format
        table_format = QTextTableFormat()
        table_format.setCellPadding(5)
        table_format.setCellSpacing(0)
        table_format.setBorder(0)
        table_format.setBorderStyle(QTextTableFormat.BorderStyle.BorderStyle_Solid)
        table_format.setBorderBrush(QColor("lightgray"))
        table_format.setAlignment(Qt.AlignmentFlag.AlignRight)
        table_format.setBorderCollapse(True)

        # column width constraints
        forty_percent = QTextLength(QTextLength.Type.PercentageLength, 40)
        thirty_percent = QTextLength(QTextLength.Type.PercentageLength, 30)

        constraints = [thirty_percent, forty_percent, thirty_percent]
        table_format.setColumnWidthConstraints(constraints)

        # alignment format for the second column
        align_right_format = QTextBlockFormat()
        align_right_format.setAlignment(Qt.AlignmentFlag.AlignLeading)

        align_left_format = QTextBlockFormat()
        align_left_format.setAlignment(Qt.AlignmentFlag.AlignLeft)

        align_center_format = QTextBlockFormat()
        align_center_format.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        table = cursor.insertTable(6, 3, table_format)

        # Define a cell format with no border
        no_border_format = QTextTableCellFormat()
        no_border_format.setLeftBorder(0)
        no_border_format.setRightBorder(0)
        no_border_format.setTopBorder(0)
        no_border_format.setBottomBorder(0)

        cell_font = no_border_format.font()
        cell_font.setPointSize(12)
        cell_font.setWeight(cell_font.Weight.Medium)
        no_border_format.setFont(cell_font)

        first_col_cells_data = [
            "",
            data["services_offered"],
            data["address"],
            f"Mobile: {data['phone_number']}",
            f"Website: \n {data['website']}",
            f"Fax: {data['email']}"
        ]

        for row, text in enumerate(first_col_cells_data):
            cursor = table.cellAt(row, 0).firstCursorPosition()
            cursor.insertText(text, no_border_format)

        cursor = table.cellAt(0, 1).firstCursorPosition()
        cursor.insertHtml(f'<h3> {self.data["name"]} </h3>')
        cursor.mergeBlockFormat(align_center_format)

        cursor = table.cellAt(1, 1).firstCursorPosition()
        cursor.insertImage(image_format)
        cursor.mergeBlockFormat(align_center_format)

        third_col_cells_data = [
            "",
            f"Invoice: {data['billing_id']}\n\n"
            f"Date: {datetime.datetime.now().strftime('%a, %B %d, %Y')}",
        ]

        for row, text in enumerate(third_col_cells_data):
            cursor = table.cellAt(row, 2).firstCursorPosition()
            cursor.mergeBlockFormat(align_right_format)
            cursor.insertText(text, no_border_format)
