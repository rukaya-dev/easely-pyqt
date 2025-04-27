import datetime

from PyQt6.QtCore import Qt, QSize, pyqtSlot
from PyQt6.QtGui import QTextCursor, QTextDocument
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QWidget, QMessageBox, QHBoxLayout
from qasync import asyncSlot

from signals import SignalRepositorySingleton
from utils.editor import preview_report, zoom
from views.componenets.customsComponents.buttons.button_with_loader import ButtonWithLoader
from views.componenets.customsComponents.buttons.preview_button import PreviewButton
from views.editor.report.main_report_editor_view import MainReportEditorView
from views.report.reports_management.report_rendered_options_widget import ReportRenderedOptionsWidgets


class UpdateReportContentDialog(QDialog):
    def __init__(self, report_controller, parent=None):
        super().__init__(parent)

        self.rendered_options = None
        self.rendered_options_widgets = None
        self.parent = parent

        self.signals = SignalRepositorySingleton.instance()

        self.reports_controller = report_controller

        self.editor_view = MainReportEditorView([], data=None, parent=self)

        self.update_btn = ButtonWithLoader("Update", size=QSize(95, 34))
        self.update_btn.clicked.connect(self.update_report_content)

        self.preview_btn = PreviewButton(parent=self)
        self.preview_btn.clicked.connect(self.preview)

        controls_layout = QHBoxLayout()
        controls_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        controls_layout.setContentsMargins(0, 20, 35, 0)
        controls_layout.setSpacing(20)

        controls_layout.addWidget(self.preview_btn, 0, Qt.AlignmentFlag.AlignRight)
        controls_layout.addWidget(self.update_btn, 0, Qt.AlignmentFlag.AlignRight)

        main_vertical_layout = QVBoxLayout()
        main_vertical_layout.setSpacing(0)
        main_vertical_layout.setContentsMargins(0, 0, 0, 0)

        main_vertical_layout.addLayout(controls_layout)
        main_vertical_layout.addWidget(self.editor_view)

        central_widget = QWidget()
        central_widget.setStyleSheet("background-color:#FAFAFA;")
        central_widget.setLayout(main_vertical_layout)

        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(central_widget)

        self.setLayout(layout)
        self.setMinimumSize(1366, 768)

    async def render_existing_options_widgets(self, options_list_data):
        if options_list_data:
            self.rendered_options_widgets = ReportRenderedOptionsWidgets(options_list_data, parent=self)
            self.rendered_options_widgets.optionIsAddedToEditor.connect(self.on_add_option_to_editor)

            if self.rendered_options is not None:
                self.editor_view.editor_layout.removeWidget(self.rendered_options)
                self.rendered_options.deleteLater()

            self.rendered_options = self.rendered_options_widgets

            if self.rendered_options:
                self.editor_view.rendered_templates_stack_widget.addWidget(self.rendered_options)
                self.editor_view.rendered_templates_stack_widget.setCurrentWidget(self.rendered_options)
        else:
            if self.rendered_options is not None:
                self.editor_view.editor_layout.removeWidget(self.rendered_options)
                self.rendered_options.deleteLater()
                self.rendered_options = None

            self.editor_view.rendered_templates_stack_widget.setCurrentWidget(None)

    def on_add_option_to_editor(self, option_name):
        if option_name:
            option_content = self.rendered_options_widgets.get_option_content()
            if option_content:
                self.search_option_and_apply_its_content(option_name, option_content)

    def search_option_and_apply_its_content(self, option_name, option_content):
        # Preparing the items without additional spaces
        formatted_option_values = [f"{item} " for item in option_content['children_values']]

        # Joining the items into a single string
        full_option_values = ''.join(formatted_option_values)

        self.editor_view.zeus_editor_text_box.textCursor().beginEditBlock()
        doc = self.editor_view.zeus_editor_text_box.document()
        cursor = QTextCursor(doc)
        found = False

        while True:
            cursor = doc.find(option_name, cursor, QTextDocument.FindFlag.FindCaseSensitively)
            if cursor.isNull():
                if not found:
                    # If option_name not found, insert at current cursor position
                    current_cursor = self.editor_view.zeus_editor_text_box.textCursor()
                    current_cursor.setCharFormat(self.editor_view.zeus_editor_text_box.currentCharFormat())
                    current_cursor.insertText(full_option_values)
                break
            else:
                found = True
                cursor.setCharFormat(self.editor_view.zeus_editor_text_box.currentCharFormat())
                cursor.insertText(full_option_values)

        self.editor_view.zeus_editor_text_box.textCursor().endEditBlock()

    @pyqtSlot()
    @asyncSlot()
    async def update_report_content(self):
        self.update_btn.start()

        data = {"report_content": self.editor_view.zeus_editor_text_box.toHtml(),
                "updated_at": datetime.datetime.now().isoformat()}

        res = await self.reports_controller.update_report(
            self.parent.table_view.get_current_id(),
            data)
        if not res:
            self.update_btn.stop()
            msg = QMessageBox()
            msg.setText('Error occurred')
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setDetailedText(
                "error occurred while updating report content, please contact your service provider.")
            msg.exec()
        else:
            self.update_btn.stop()
            self.signals.globalReportUpdateTableViewSignal.emit()
            self.close()
            msg = QMessageBox()
            msg.setText('Report Content Successfully Updated')
            msg.setIcon(QMessageBox.Icon.Information)
            msg.exec()

    @pyqtSlot()
    def preview(self):
        html_content = self.editor_view.zeus_editor_text_box.toHtml()
        preview_report(html_content)
