import datetime

from PyQt6.QtCore import Qt, pyqtSlot, QSize, pyqtSignal
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QWidget, QMessageBox, QStackedWidget, QPushButton, QLabel
from qasync import asyncSlot

from loggers.logger_configs import set_up_logger
from services.supabase.controllers.report_workshop.template_controller import TemplateController
from signals import SignalRepositorySingleton
from views.componenets.customsComponents.buttons.button_with_loader import ButtonWithLoader
from views.componenets.customsComponents.loaders.internal_loader import InternalLoader
from views.editor.template.main_template_editor_view import MainTemplateEditorView
from views.report_workshop.template.template_form import TemplateForm

logger = set_up_logger('views.report_workshop.template.template_dialog')


class TemplateDialog(QDialog):
    def __init__(self, action_type, parent=None):
        super().__init__(parent)

        self.setStyleSheet("background-color:white;")
        self.tab_buttons = None
        self.parent = parent
        self.action_type = action_type

        self.data = []

        # Signals
        self.signals = SignalRepositorySingleton.instance()

        # API model
        self.template_controller = TemplateController()
        self.category_controller = self.parent.category_controller

        self.stacked_content_widget = QStackedWidget()
        self.stacked_content_widget.setStyleSheet("background-color:#FAFAFA;")

        self.editor_view = MainTemplateEditorView([], data=None, parent=self)

        self.template_from_widget = TemplateForm(parent=self)

        self.header_widget = HeaderWidget(parent=self)

        self.header_widget.next_btn.clicked.connect(self.show_editor_view)
        self.header_widget.back_btn.clicked.connect(lambda: self.set_main_content(self.template_from_widget))
        self.header_widget.save_btn.clicked.connect(self.add_new_template)
        self.header_widget.update_btn.clicked.connect(self.update_template)

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

        self.set_main_content(self.template_from_widget)

        # Set Layouts
        self.setLayout(main_v_layout)
        self.setMinimumSize(1366, 768)

    def set_main_content(self, content_widget):
        self.stacked_content_widget.addWidget(content_widget)
        self.stacked_content_widget.setCurrentWidget(content_widget)

        if content_widget == self.template_from_widget:

            self.header_widget.next_btn.show()
            self.header_widget.back_btn.hide()
            self.header_widget.save_btn.hide()
            self.header_widget.update_btn.hide()

            self.header_widget.template_name.setVisible(False)

        elif content_widget == self.editor_view:

            if self.action_type == "create":
                self.render_category_options()
                self.header_widget.save_btn.setEnabled(True)
                self.header_widget.save_btn.show()

            elif self.action_type == "update":
                self.header_widget.save_btn.hide()
                self.header_widget.update_btn.show()

            self.header_widget.next_btn.hide()
            self.header_widget.back_btn.show()
            self.header_widget.back_btn.setEnabled(True)

            self.header_widget.template_name.setVisible(True)

    def show_editor_view(self):
        self.header_widget.template_name.setText(self.template_from_widget.template_name_input.text())
        self.set_main_content(self.editor_view)

    def render_category_options(self):
        self.signals.templateHeaderInternalLoaderSignal.emit(True)

        self.editor_view.options_widget.category_label.setText(
            self.template_from_widget.category_combo.currentText())

        options = self.template_from_widget.get_category_options()
        if options:
            self.editor_view.options_widget.options = options
            options_slugs = {option['slug'] for option in options}
            self.editor_view.options_widget.add_options_to_list_view(options_slugs)
        else:
            self.editor_view.options_widget.options = []

        self.signals.templateHeaderInternalLoaderSignal.emit(False)

    @pyqtSlot()
    @asyncSlot()
    async def add_new_template(self):
        if self.validate_data():
            self.header_widget.save_btn.start()
            data = self.get_data()

            is_exits = await self.template_controller.check_if_template_exist(data)
            if is_exits:
                self.header_widget.save_btn.stop()
                msg = QMessageBox()
                msg.setText(f'Template with name : {data["name"]} already exist')
                msg.setIcon(QMessageBox.Icon.Critical)
                msg.exec()
            else:
                res = await self.template_controller.create_template(data=data)
                if not res:
                    self.header_widget.save_btn.stop()
                    msg = QMessageBox()
                    msg.setText('Could not create a new template')
                    msg.setIcon(QMessageBox.Icon.Critical)
                    msg.setDetailedText("error occurred while creating, please contact your service provider.")
                    msg.exec()
                else:
                    self.header_widget.save_btn.stop()
                    self.signals.globalCreateMessageNotificationSignal.emit({
                        "message_type": "success",
                        "message": "Successful create new template",
                        "duration": 2000,
                    })
                    self.close()
                    await self.parent.refresh_table()

    @pyqtSlot()
    @asyncSlot()
    async def update_template(self):
        if self.validate_data():
            self.header_widget.update_btn.start()

            data = self.get_data()
            template_id = self.parent.table_view.get_current_id()

            data.update({"updated_at": datetime.datetime.now().isoformat()})

            is_exits = await self.template_controller.check_if_updated_template_exist(template_id=template_id,
                                                                                      data=data)
            if is_exits:
                self.header_widget.update_btn.stop()
                msg = QMessageBox()
                msg.setText(f'Template with name : {data["name"]} and category {data["category_id"]} already exist')
                msg.setIcon(QMessageBox.Icon.Critical)
                msg.exec()
            else:
                res = await self.template_controller.update_template(template_id=template_id, data=data)
                if not res:
                    self.header_widget.update_btn.stop()
                    msg = QMessageBox()
                    msg.setText('Could not update template')
                    msg.setIcon(QMessageBox.Icon.Critical)
                    msg.setDetailedText("error occurred while updating, please contact your service provider.")
                    msg.exec()
                else:
                    self.header_widget.update_btn.stop()
                    self.close()
                    await self.parent.refresh_table()

                    self.signals.globalCreateMessageNotificationSignal.emit({
                        "message_type": "success",
                        "message": "Template Successfully updated",
                        "duration": 2000,
                    })

    def get_data(self):
        name = self.template_from_widget.template_name_input.text()
        template_content = self.editor_view.zeus_editor_text_box.toHtml()
        options_list = self.editor_view.zeus_editor_text_box.options_list
        if template_content:
            template_options = options_list if options_list else None
            return {
                'name': name,
                'content': template_content,
                'category_id': self.template_from_widget.category_combo.currentText(),
                'template_options': template_options,
                'description': self.template_from_widget.desc_input.toPlainText()
            }

    def validate_data(self):
        template_content = self.editor_view.zeus_editor_text_box.toPlainText()

        if not bool(template_content.strip()):
            QMessageBox.warning(self, "Error", "Template Content is required")
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
        font.setWeight(font.Weight.Normal)
        font.setPointSize(16)

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

        self.next_btn = ButtonWithLoader("Next", size=QSize(95, 34))

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

        next_save_btns_layout = QHBoxLayout()
        next_save_btns_layout.setAlignment(Qt.AlignmentFlag.AlignRight)

        next_save_btns_layout.addWidget(self.next_btn)
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
