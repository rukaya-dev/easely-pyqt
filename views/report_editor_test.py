import asyncio

from PyQt6.QtCore import Qt, QSize, pyqtSlot, QRectF
from PyQt6.QtGui import QColor, QPainter
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QSpacerItem, QSizePolicy, QHBoxLayout, QMessageBox
from qasync import asyncSlot

from services.supabase.controllers.report_workshop.report_layout_controller import ReportLayoutController
from signals import SignalRepositorySingleton
from utils.editor import preview_report
from views.componenets.customsComponents.buttons.button_with_loader import ButtonWithLoader
from views.componenets.customsComponents.buttons.preview_button import PreviewButton
from views.componenets.textEditorComponenets.menuBar.format_bar import FormatBar
from views.componenets.textEditorComponenets.zeusEditor.zeus_editor import ZeusTextBox


class ReportEditorTest(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.tab_buttons = None

        # Signals
        self.signals = SignalRepositorySingleton.instance()

        self.report_layouts_controller = ReportLayoutController()

        self.header_editor = HeaderEditor(parent=self)

        editor_start_spacer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        editor_end_spacer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        header_widget = QWidget()
        header_widget.setObjectName("report_header_widget")
        # header_widget.setStyleSheet("""
        #     QWidget#report_header_widget {
        #     background-color: #FAFAFA;
        #     }
        # """)
        header_widget.setFixedHeight(86)

        self.save_btn = ButtonWithLoader("Print", size=QSize(95, 34))
        self.save_btn.clicked.connect(self.print_content)
        #
        self.preview_btn = PreviewButton(parent=self)
        self.preview_btn.setText("Insert")
        self.preview_btn.clicked.connect(self.insert_option)

        save_preview_btns_layout = QHBoxLayout(header_widget)
        save_preview_btns_layout.setContentsMargins(20, 0, 20, 0)
        save_preview_btns_layout.setAlignment(Qt.AlignmentFlag.AlignRight)

        save_preview_btns_layout.addWidget(self.preview_btn)
        save_preview_btns_layout.addWidget(self.save_btn)

        main_layout = QVBoxLayout()
        main_layout.addSpacerItem(editor_start_spacer)
        main_layout.addWidget(self.header_editor)
        main_layout.addSpacerItem(editor_end_spacer)

        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addLayout(main_layout)
        layout.addWidget(header_widget)

        self.setLayout(layout)

    @pyqtSlot()
    def insert_option(self):
        cursor = self.header_editor.zeus_editor_text_box.textCursor()
        option_html = "test option"
        cursor.insertText(" ")
        start_pos = cursor.position()
        cursor.insertText(option_html)
        cursor.insertText(" ")

        cursor.setPosition(start_pos)
        cursor.movePosition(cursor.MoveOperation.Right, cursor.MoveMode.KeepAnchor, len(option_html))

        option_char_format = cursor.charFormat()
        option_char_format.setBackground(QColor("#edebfc"))
        option_char_format.setForeground(QColor("black"))
        cursor.setCharFormat(option_char_format)

        self.header_editor.zeus_editor_text_box.options_list.append(option_html)

    def print_content(self):
        html_content = self.header_editor.zeus_editor_text_box.toHtml()
        preview_report(html_content)



class HeaderEditor(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.zeus_editor_text_box = ZeusTextBox(self)

        self.format_bar = FormatBar(self.zeus_editor_text_box, self)
        self.format_bar.menu_bar_central_widget.setFixedWidth(1000)

        central_widget = QWidget()
        central_widget.setStyleSheet("""
            background-color:#FAFAFA;
        """)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        main_layout.setSpacing(20)

        main_layout.addWidget(self.format_bar)
        main_layout.addWidget(self.zeus_editor_text_box, 1, Qt.AlignmentFlag.AlignHCenter)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(central_widget)

        self.setLayout(layout)
