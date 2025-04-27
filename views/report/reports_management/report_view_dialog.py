from datetime import datetime

from PyQt6.QtCore import Qt, QMarginsF, QSizeF
from PyQt6.QtGui import QFont, QPageLayout, QPageSize, QTextCharFormat, QTextBlockFormat, QColor, QTextTableFormat, \
    QTextLength, QTextTableCellFormat, QTextDocument
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QSizePolicy, QSpacerItem, \
    QTextEdit
from loggers.logger_configs import set_up_logger
from utils.editor import zoom, preview_report
from views.componenets.customsComponents.custom_scroll_area import CustomScrollArea
from views.componenets.customsComponents.table.save_and_cancel_buttons import SaveAndCancelButtonsWithLoader

logger = set_up_logger('main.views.report.view_report_dialog')


class ViewReportDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.parent = parent

        self.text_edit = QTextEdit(parent=self)
        self.text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.text_edit.setFixedSize(793, 1122)
        self.text_edit.document().setDocumentMargin(20)
        self.text_edit.setStyleSheet("""
            QTextEdit {
                 background-color:white;
                 color:black;
            }
            
        """)

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

    def print(self):
        html_content = self.text_edit.toHtml()
        preview_report(html_content)

#     class TextEdit(QTextEdit):
#         def __init__(self, data, parent=None):
#             super().__init__(parent)
#
#             self.setFixedSize(793, 1122)
#
#             self.data = data
#
#             if self.data["report_header_layout_data"]["content"]:
#                 self.insertHtml(self.data["report_header_layout_data"]["content"])
#
#             cursor = self.textCursor()
#
#             # table format
#             table_format = QTextTableFormat()
#             table_format.setCellPadding(5)
#             table_format.setCellSpacing(0)
#             table_format.setBorder(1)
#             table_format.setBorderStyle(QTextTableFormat.BorderStyle.BorderStyle_Solid)
#             table_format.setBorderBrush(QColor("lightgray"))
#             table_format.setAlignment(Qt.AlignmentFlag.AlignRight)
#             table_format.setBorderCollapse(True)
#
#             # column width constraints
#             seventy_percent = QTextLength(QTextLength.Type.PercentageLength, 60)
#             thirty_percent = QTextLength(QTextLength.Type.PercentageLength, 40)
#             constraints = [seventy_percent, thirty_percent]
#             table_format.setColumnWidthConstraints(constraints)
#
#             # alignment format for the second column
#             align_right_format = QTextBlockFormat()
#             align_right_format.setAlignment(Qt.AlignmentFlag.AlignRight)
#
#             table = cursor.insertTable(3, 2, table_format)
#
#             cell_format = QTextCharFormat()
#             # Define a cell format with no border
#             no_border_format = QTextTableCellFormat()
#             no_border_format.setLeftBorder(0)
#             no_border_format.setRightBorder(0)
#             no_border_format.setTopBorder(0)
#             no_border_format.setBottomBorder(0)
#
#             first_col_cells_data = [
#                 f"Patient ID : {self.data['patient_id']}",
#                 f"Name : {self.data['patient_first_name'] + ' ' + self.data['patient_last_name']}",
#                 f"Clinical Data : {self.data['patient_clinical_data']}"
#             ]
#
#             for row, text in enumerate(first_col_cells_data):
#                 cursor = table.cellAt(row, 0).firstCursorPosition()
#                 cursor.insertText(text, no_border_format)
#
#             second_col_cells_data = [
#                 f"Age/Sex : {data['patient_age']}{data['patient_age_unit']}/{data['patient_gender'][:1]}",
#                 f"Date : {datetime.now().strftime('%a, %B %d, %Y')}",
#                 f"Ref_By : Dr. {data['referring_doctor_first_name'] + data['referring_doctor_last_name']}"
#             ]
#
#             for row, text in enumerate(second_col_cells_data):
#                 cursor = table.cellAt(row, 1).firstCursorPosition()
#                 cursor.insertText(text, no_border_format)
#                 cursor.mergeBlockFormat(align_right_format)
#
#             if self.data["report_content"]:
#                 self.insertHtml("<br><br/>")
#                 self.insertHtml(self.data["report_content"])
#
#             if self.data["report_footer_layout_data"]["content"]:
#                 self.insertHtml(self.data["report_footer_layout_data"]["content"])
#
#
# class PatientInformation(QWidget):
#     def __init__(self, parent=None):
#         super().__init__(parent)
#
#         id_label = QLabel("ID: " + "1053")
#         name_label = QLabel("Name: " + " Danial Ross")
#         clinical_data_label = QLabel("Clinical Data: " + "Pain in epicastrium")
#
#         left_side_information_layout = QVBoxLayout()
#         left_side_information_layout.setContentsMargins(0, 0, 0, 0)
#         left_side_information_layout.setSpacing(15)
#
#         left_side_information_layout.addWidget(id_label)
#         left_side_information_layout.addWidget(name_label)
#         left_side_information_layout.addWidget(clinical_data_label)
#
#         age_and_sex_label = QLabel("Age/Sex: " + "38" + "years" + "/" + "F")
#         date_label = QLabel("Date: " + " 9 August 2023")
#         referring_doctor_label = QLabel("Ref.Dr:Dr." + " Marvin MD ")
#
#         right_side_information_layout = QVBoxLayout()
#         right_side_information_layout.setContentsMargins(0, 0, 0, 0)
#         right_side_information_layout.setSpacing(15)
#
#         right_side_information_layout.addWidget(age_and_sex_label)
#         right_side_information_layout.addWidget(date_label)
#         right_side_information_layout.addWidget(referring_doctor_label)
#
#         spacer = QSpacerItem(20, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
#
#         central_widget = QWidget()
#         central_widget.setStyleSheet("""
#             QWidget {
#                 border:1px solid #BCB6B6;
#                 border-radius:5px;
#             }
#             QLabel {
#                 background-color:transparent;
#                 color:black;
#                 font-size:14pt;
#                 border:0;
#
#             }
#         """)
#
#         main_h_layout = QHBoxLayout(central_widget)
#         main_h_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
#         main_h_layout.setSpacing(20)
#         main_h_layout.setContentsMargins(15, 15, 15, 15)
#
#         main_h_layout.addLayout(left_side_information_layout)
#         main_h_layout.addSpacerItem(spacer)
#         main_h_layout.addLayout(right_side_information_layout)
#
#         layout = QVBoxLayout()
#         layout.setContentsMargins(0, 0, 0, 0)
#         layout.setSpacing(0)
#
#         layout.addWidget(central_widget)
#
#         self.setLayout(layout)
