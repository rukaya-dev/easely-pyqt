import datetime

from PyQt6.QtCore import Qt, pyqtSlot, QSize, pyqtSignal
from PyQt6.QtGui import QIcon, QTextCursor, QTextDocument, QTextLength, QTextBlockFormat, \
    QTextTableCellFormat, QTextTableFormat, QColor
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QWidget, QMessageBox, QStackedWidget, QPushButton, QLabel
from qasync import asyncSlot

from loggers.logger_configs import set_up_logger
from services.supabase.controllers.report.report_controller import ReportController
from services.supabase.controllers.report_workshop.category_controller import CategoryController
from services.supabase.controllers.report_workshop.option_controller import OptionController
from services.supabase.controllers.report_workshop.report_layout_controller import ReportLayoutController
from services.supabase.controllers.report_workshop.template_controller import TemplateController
from services.supabase.controllers.staff.referring_doctor.referring_doctor_controller import ReferringDoctorController
from signals import SignalRepositorySingleton
from utils.editor import preview_report
from views.componenets.customsComponents.buttons.button_with_loader import ButtonWithLoader
from views.componenets.customsComponents.buttons.preview_button import PreviewButton
from views.componenets.customsComponents.loaders.internal_loader import InternalLoader
from views.editor.report.main_report_editor_view import MainReportEditorView
from views.report.reports_management.report_form import ReportForm
from views.report.reports_management.report_rendered_options_widget import ReportRenderedOptionsWidgets

logger = set_up_logger('views.report.report_dialog')


class ReportDialog(QDialog):
    def __init__(self, action_type, patient_appointment_data, parent=None):
        super().__init__(parent)

        self.rendered_options = None
        self.rendered_options_widgets = None
        self.tab_buttons = None
        self.parent = parent
        self.action_type = action_type

        self.setStyleSheet("background-color:white;")

        self.patient_appointment_data = patient_appointment_data

        # Signals
        self.signals = SignalRepositorySingleton.instance()

        # API model
        self.template_controller = TemplateController()
        self.category_controller = CategoryController()
        self.option_controller = OptionController()
        self.report_controller = ReportController()
        self.referring_doctor_controller = ReferringDoctorController()
        self.report_layouts_controller = ReportLayoutController()

        self.stacked_content_widget = QStackedWidget()
        self.stacked_content_widget.setStyleSheet("background-color:#FAFAFA;")

        self.editor_view = MainReportEditorView([], data=None, parent=self)

        self.report_form_widget = ReportForm(parent=self)

        self.header_widget = HeaderWidget(parent=self)

        self.header_widget.next_btn.clicked.connect(self.show_editor_view)
        self.header_widget.back_btn.clicked.connect(lambda: self.set_main_content(self.report_form_widget))
        self.header_widget.save_btn.clicked.connect(self.add_new_report)
        self.header_widget.preview_btn.clicked.connect(self.preview)

        main_h_layout = QHBoxLayout()
        main_h_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        main_h_layout.setContentsMargins(0, 0, 0, 0)

        main_h_layout.addWidget(self.stacked_content_widget)

        main_v_layout = QVBoxLayout()
        main_v_layout.setContentsMargins(0, 0, 0, 0)
        main_v_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        main_v_layout.setSpacing(0)

        main_v_layout.setContentsMargins(0, 0, 0, 0)
        main_v_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        main_v_layout.addWidget(self.header_widget)
        main_v_layout.addLayout(main_h_layout)

        self.set_main_content(self.report_form_widget)

        self.setLayout(main_v_layout)
        self.setMinimumSize(1366, 768)

    @pyqtSlot()
    @asyncSlot()
    async def show_editor_view(self):
        try:
            self.reset_editor_view()
            self.header_widget.next_btn.start()

            template_name = self.report_form_widget.get_current_selected_template_name()

            template_data = await self.template_controller.get_template_by_name(template_name)

            all_category_options = await self.option_controller.get_options_by_category(template_data["category_id"])

            referring_doctor_name = self.report_form_widget.referring_doctor_combo.currentText()

            self.patient_appointment_data[
                "referring_doctor_name"] = referring_doctor_name if referring_doctor_name else ""

            report_header_layout_data = await self.report_layouts_controller.get_report_header_layout()

            self.set_report_initial_data(self.patient_appointment_data, template_data["content"],
                                         report_header_layout_data)

            if template_data["template_options"]:
                options_list_data = await self.option_controller.get_options_by_slugs(
                    options_slugs=template_data["template_options"],
                    category_id=template_data["category_id"])

                for option in all_category_options:
                    if option not in options_list_data:
                        options_list_data.append(option)

                if options_list_data:
                    await self.render_existing_options_widgets(options_list_data=options_list_data)
                    self.editor_view.zeus_editor_text_box.update_options_list(template_data["template_options"])

            else:
                await self.render_existing_options_widgets(options_list_data=all_category_options)
                self.editor_view.zeus_editor_text_box.update_options_list([])

            self.set_main_content(self.editor_view)
            self.header_widget.next_btn.stop()

        except Exception as e:
            self.signals.globalCreateMessageNotificationSignal.emit({
                "message_type": "error",
                "message": "An unexpected error occurred",
                "duration": 2000,
            })
            logger.error(e, exc_info=True)
            return

    @pyqtSlot()
    @asyncSlot()
    async def add_new_report(self):
        if self.validate_data():
            self.header_widget.save_btn.start()

            insert_data = self.get_data()

            insert_data["patient_id"] = self.patient_appointment_data["patient_id"]
            insert_data["appointment_id"] = self.patient_appointment_data["appointment_id"]

            res = await self.report_controller.create_report(data=insert_data,
                                                             logging_data=self.patient_appointment_data)
            if not res:
                self.header_widget.save_btn.stop()
                msg = QMessageBox()
                msg.setText('Could not create a new report')
                msg.setIcon(QMessageBox.Icon.Critical)
                msg.setDetailedText("error occurred while creating, please contact your service provider.")
                msg.exec()
            else:
                self.header_widget.save_btn.stop()
                self.signals.globalCreateMessageNotificationSignal.emit({
                    "message_type": "success",
                    "message": "Successful create new report",
                    "duration": 2000,
                })
                self.close()

    async def render_existing_options_widgets(self, options_list_data):
        if options_list_data:
            self.rendered_options_widgets = ReportRenderedOptionsWidgets(options_list_data, parent=self)
            self.rendered_options_widgets.optionIsAddedToEditor.connect(self.on_add_option_to_editor)

            if self.rendered_options is not None:
                if self.editor_view.editor_layout is not None:
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

    def preview(self):
        html_content = self.editor_view.zeus_editor_text_box.toHtml()
        preview_report(html_content)

    def set_report_initial_data(self, data, template_content, report_header_layout_data):
        # Header

        if report_header_layout_data and report_header_layout_data.get("content"):
            self.editor_view.zeus_editor_text_box.insertHtml(report_header_layout_data["content"])
            self.editor_view.zeus_editor_text_box.insertHtml("<br><br/>")

        cursor = self.editor_view.zeus_editor_text_box.textCursor()

        # table format
        table_format = QTextTableFormat()
        table_format.setCellPadding(5)
        table_format.setCellSpacing(0)
        table_format.setBorder(1)
        table_format.setBorderStyle(QTextTableFormat.BorderStyle.BorderStyle_Solid)
        table_format.setBorderBrush(QColor("lightgray"))
        table_format.setAlignment(Qt.AlignmentFlag.AlignRight)
        table_format.setBorderCollapse(True)

        sixty_percent = QTextLength(QTextLength.Type.PercentageLength, 60)
        forty_percent = QTextLength(QTextLength.Type.PercentageLength, 40)
        constraints = [sixty_percent, forty_percent]
        table_format.setColumnWidthConstraints(constraints)

        align_right_format = QTextBlockFormat()
        align_right_format.setAlignment(Qt.AlignmentFlag.AlignRight)

        table = cursor.insertTable(3, 2, table_format)

        no_border_format = QTextTableCellFormat()
        no_border_format.setLeftBorder(0)
        no_border_format.setRightBorder(0)
        no_border_format.setTopBorder(0)
        no_border_format.setBottomBorder(0)

        cell_font = no_border_format.font()
        cell_font.setPointSize(14)
        cell_font.setWeight(cell_font.Weight.Medium)
        no_border_format.setFont(cell_font)

        first_col_cells_data = [
            f"Name: {data['patient_first_name'] + ' ' + data['patient_last_name']}",
            f"Age/Sex: {data['patient_age']}{data['patient_age_unit']}/{data['patient_gender'][:1]}",
            f"Clinical Data: {data['patient_clinical_data']}"
        ]

        for row, text in enumerate(first_col_cells_data):
            cursor = table.cellAt(row, 0).firstCursorPosition()
            cursor.insertText(text, no_border_format)

        second_col_cells_data = [
            f"Doctor: {data['doctor_name']}",
            f"Ref_By: Dr. {data['referring_doctor_name']}" if data['referring_doctor_name'] != 'None' else "Ref_By:",
            f"Date: {datetime.datetime.now().strftime('%a, %B %d, %Y')}",
        ]

        for row, text in enumerate(second_col_cells_data):
            cursor = table.cellAt(row, 1).firstCursorPosition()
            cursor.insertText(text, no_border_format)
            cursor.mergeBlockFormat(align_right_format)

        # Content
        self.editor_view.zeus_editor_text_box.insertHtml("<br><br/>")
        self.editor_view.zeus_editor_text_box.insertHtml(template_content)
        cursor.mergeBlockFormat(align_right_format)

    def on_add_option_to_editor(self, option_name):
        if option_name:
            option_content = self.rendered_options_widgets.get_option_content()
            if option_content:
                self.search_option_and_apply_its_content(option_name, option_content)

    def search_option_and_apply_its_content(self, option_name, option_content):
        formatted_option_values = [f"{item} " for item in option_content['children_values']]

        full_option_values = ''.join(formatted_option_values)

        self.editor_view.zeus_editor_text_box.textCursor().beginEditBlock()
        doc = self.editor_view.zeus_editor_text_box.document()
        cursor = QTextCursor(doc)
        found = False

        while True:
            cursor = doc.find(option_name, cursor, QTextDocument.FindFlag.FindCaseSensitively)
            if cursor.isNull():
                if not found:
                    current_cursor = self.editor_view.zeus_editor_text_box.textCursor()
                    current_cursor.setCharFormat(self.editor_view.zeus_editor_text_box.currentCharFormat())
                    current_cursor.insertText(full_option_values)
                break
            else:
                found = True
                cursor.setCharFormat(self.editor_view.zeus_editor_text_box.currentCharFormat())
                cursor.insertText(full_option_values)

        self.editor_view.zeus_editor_text_box.textCursor().endEditBlock()

    def reset_editor_view(self):
        self.editor_view.zeus_editor_text_box.setText("")

    def set_main_content(self, content_widget):
        self.stacked_content_widget.addWidget(content_widget)
        self.stacked_content_widget.setCurrentWidget(content_widget)

        if content_widget == self.report_form_widget:

            self.header_widget.next_btn.show()
            self.header_widget.back_btn.hide()
            self.header_widget.save_btn.hide()
            self.header_widget.preview_btn.hide()
            self.header_widget.update_btn.hide()

            self.header_widget.template_name.setVisible(False)

        elif content_widget == self.editor_view:

            if self.action_type == "create":
                self.header_widget.save_btn.setEnabled(True)
                self.header_widget.save_btn.show()
                self.header_widget.preview_btn.show()

            elif self.action_type == "update":
                self.header_widget.save_btn.hide()
                self.header_widget.update_btn.show()
                self.header_widget.preview_btn.show()

            self.header_widget.next_btn.hide()
            self.header_widget.back_btn.show()
            self.header_widget.back_btn.setEnabled(True)

            self.header_widget.template_name.setVisible(True)

    def get_data(self):
        template_name = self.report_form_widget.get_current_selected_template_name()
        referring_doctor_id = self.report_form_widget.get_current_selected_referring_doctor_id()
        data = {
            'patient_id': "",
            'appointment_id': "",
            'template_name': template_name,
            'report_title': template_name,
            'category': self.report_form_widget.category_combo.currentText(),
            'report_content': self.editor_view.zeus_editor_text_box.toHtml(),
        }

        if referring_doctor_id:
            data['referring_doctor_id'] = referring_doctor_id
        return data

    def validate_data(self):
        report_content = self.editor_view.zeus_editor_text_box.toPlainText()

        if not bool(report_content.strip()):
            QMessageBox.warning(self, "Error", "Report Content is required")
            return

        return True


class HeaderWidget(QWidget):
    backBtnClicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        # Signals
        self.signals = SignalRepositorySingleton.instance()
        self.signals.templateHeaderInternalLoaderSignal.connect(self.handle_internal_loader_status)

        self.template_name = QLabel()

        font = self.template_name.font()
        font.setWeight(font.Weight.Medium)
        font.setPointSize(18)

        self.template_name.setFont(font)

        self.back_btn = QPushButton()
        self.back_btn.setFixedSize(QSize(35, 35))
        self.back_btn.setStyleSheet("""
        QPushButton {
            border:0;
        }
        QPushButton:pressed {
            color: #E0E0E0;
            padding-top: 2px;
            padding-left: 2px;
        }
        """)
        self.back_btn.hide()

        back_btn_icon = QIcon(":/resources/icons/back_btn.svg")

        self.back_btn.setIcon(back_btn_icon)
        self.back_btn.setIconSize(QSize(30, 30))

        self.next_btn = ButtonWithLoader("Next", size=QSize(100, 34))
        self.next_btn.setDisabled(True)
        self.disable_button_style(self.next_btn)

        self.update_btn = ButtonWithLoader("Update", size=QSize(100, 34))
        self.update_btn.hide()

        self.internal_loader = InternalLoader(height=34)

        back_btn_and_template_name_layout = QHBoxLayout()
        back_btn_and_template_name_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        back_btn_and_template_name_layout.addWidget(self.back_btn)
        back_btn_and_template_name_layout.addWidget(self.template_name)
        back_btn_and_template_name_layout.addWidget(self.internal_loader)

        self.save_btn = ButtonWithLoader("Save", size=QSize(95, 34))
        self.save_btn.hide()

        self.preview_btn = PreviewButton(parent=self)
        self.preview_btn.hide()

        next_save_btns_layout = QHBoxLayout()
        next_save_btns_layout.setAlignment(Qt.AlignmentFlag.AlignRight)

        next_save_btns_layout.addWidget(self.next_btn)
        next_save_btns_layout.addWidget(self.preview_btn)
        next_save_btns_layout.addWidget(self.save_btn)
        next_save_btns_layout.addWidget(self.update_btn)

        central_widget = QWidget()
        central_widget.setObjectName("template_header_widget")
        central_widget.setStyleSheet("""
        QWidget#template_header_widget {
        background-color: white;
        }
        """)
        central_widget.setFixedHeight(86)

        template_header_layout = QHBoxLayout(central_widget)
        template_header_layout.setContentsMargins(30, 0, 30, 0)
        template_header_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        template_header_layout.addLayout(back_btn_and_template_name_layout)
        template_header_layout.addLayout(next_save_btns_layout)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(central_widget)

        self.setLayout(layout)

    def disable_button_style(self, button: QPushButton):
        button.setStyleSheet("""
        QPushButton {
            border:0;
            border-radius:3px;
            font-size:13pt;
            background-color:#ebebeb;
            color:#a4a4a4;
        }
        """)

    def enable_button_style(self, button: QPushButton):
        button.setStyleSheet("""
        QPushButton {
            border:0;
            border-radius:3px;
            font-size:13pt;
            background-color:#2563EB;
            color:#F5F5F5;
        }
        QPushButton:pressed {
            border:0;
            border-radius:3px;
            font-size:13pt;
            color:#F5F5F5;
            padding-top: 2px;
            padding-left: 2px;
        }

        """)

    @pyqtSlot(bool)
    def handle_internal_loader_status(self, status: bool):
        if status:
            self.internal_loader.start()
        else:
            self.internal_loader.stop()
