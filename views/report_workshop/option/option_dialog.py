import datetime

from PyQt6.QtCore import QSize, Qt, pyqtSlot
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QWidget, QMessageBox, QSpacerItem, QSizePolicy
from qasync import asyncSlot

from loggers.logger_configs import set_up_logger
from signals import SignalRepositorySingleton
from services.supabase.controllers.report_workshop.option_controller import OptionController
from utils.utlis import string_to_slug
from views.componenets.customsComponents.buttons.button_with_loader import ButtonWithLoader
from views.componenets.customsComponents.table.save_and_cancel_buttons import SaveAndCancelButtonsWithLoader
from views.report_workshop.option.option_form import OptionForm

logger = set_up_logger('main.views.report_workshop.option.categories_dialog')


class OptionDialog(QDialog):
    def __init__(self, category_controller, parent=None):
        super().__init__(parent)

        self.setStyleSheet("background-color:#f3f4f6;")

        self.parent = parent
        self.is_option_data_widget = None

        self.option_controller = OptionController()
        self.category_controller = category_controller

        # Signals
        self.signals = SignalRepositorySingleton.instance()

        central_widget = QWidget(self)
        central_widget.setObjectName("central_widget")

        self.form_widget = OptionForm(parent=self)

        self.save_and_cancel_btns = SaveAndCancelButtonsWithLoader(text="Save")
        self.save_and_cancel_btns.save_btn.clicked.connect(self.add_new_option)
        self.save_and_cancel_btns.cancel_btn.clicked.connect(self.close)

        self.update_btn = ButtonWithLoader("Update", size=QSize(95, 34))
        self.update_btn.clicked.connect(self.update_option)

        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(10)
        controls_layout.setContentsMargins(20, 20, 20, 20)
        controls_layout.setAlignment(Qt.AlignmentFlag.AlignRight)

        controls_layout.addWidget(self.save_and_cancel_btns)
        controls_layout.addWidget(self.update_btn)

        main_h_layout = QHBoxLayout()
        main_h_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        main_h_layout.setContentsMargins(0, 0, 0, 0)

        main_h_layout.addWidget(self.form_widget)

        central_widget.setLayout(main_h_layout)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(central_widget)
        layout.addLayout(controls_layout)

        self.setLayout(layout)

        self.setMinimumHeight(768)

        self.setModal(True)

    def validate_data(self):
        name = self.form_widget.option_name_input.text()
        category = self.form_widget.category_combo.currentText()
        option_structure = self.form_widget.treeWidget.ValidateTree(self.form_widget.treeWidget.treeWidget)

        if not category:
            QMessageBox().warning(self, "Warning", "Category is required")
            return

        if not name:
            QMessageBox().warning(self, "Warning", "Name is required")
            return

        if not option_structure:
            QMessageBox().warning(self, "Warning", "Option structure is required")
            return

        return True

    def get_data(self):
        name = self.form_widget.option_name_input.text()
        return {
            'category_id': self.form_widget.category_combo.currentText(),
            'name': name,
            'description': self.form_widget.desc_input.toPlainText(),
            'option_structure': self.form_widget.treeWidget.getTreeStructure(self.form_widget.treeWidget.treeWidget),
            'slug': string_to_slug(name),
            'type': 'type'
        }

    @pyqtSlot()
    @asyncSlot()
    async def add_new_option(self):
        if self.validate_data():
            data = self.get_data()
            self.save_and_cancel_btns.save_btn.start()

            is_exist = await self.option_controller.check_if_option_exist(data["name"], data["category_id"])
            if is_exist:
                QMessageBox.warning(None, "Warning",
                                    f"""option with name: {data["name"]} and category: {data["category_id"]} already exist.""")
                self.save_and_cancel_btns.save_btn.stop()
            else:
                res = await self.option_controller.create_option(data)
                if not res:
                    self.signals.globalCreateMessageNotificationSignal.emit({
                        "message_type": "error",
                        "message": "An unexpected error occurred",
                        "duration": 2000,
                    })
                    self.save_and_cancel_btns.save_btn.stop()
                else:
                    await self.parent.refresh_table()
                    self.save_and_cancel_btns.save_btn.stop()
                    self.signals.globalCreateMessageNotificationSignal.emit({
                        "message_type": "success",
                        "message": "Successfully created a new option",
                        "duration": 2000,
                    })
                    self.save_and_cancel_btns.save_btn.stop()
                    self.close()

    @pyqtSlot()
    @asyncSlot()
    async def update_option(self):
        if self.validate_data():
            data = self.get_data()

            modified_data = {"updated_at": datetime.datetime.now().isoformat()}
            modified_data.update(data)

            self.update_btn.start()

            is_exist = await self.option_controller.check_if_updated_option_exist(self.parent.table_view.current_id,
                                                                                  modified_data["name"], modified_data["category_id"])
            if is_exist:
                QMessageBox.warning(None, "Warning",
                                    f"""option with name: {data["name"]} and category: {data["category_id"]} already exist.""")
                self.update_btn.stop()
            else:
                res = await self.option_controller.update_option(option_id=self.parent.table_view.current_id, data=modified_data)
                if not res:
                    self.signals.globalCreateMessageNotificationSignal.emit({
                        "message_type": "error",
                        "message": "An unexpected error occurred",
                        "duration": 2000,
                    })
                    self.update_btn.stop()
                else:
                    await self.parent.refresh_table()
                    self.update_btn.stop()
                    self.close()
                    self.signals.globalCreateMessageNotificationSignal.emit({
                        "message_type": "success",
                        "message": "Option successfully updated",
                        "duration": 2000,
                    })
