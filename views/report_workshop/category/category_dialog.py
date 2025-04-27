import datetime

from PyQt6.QtCore import QSize, Qt, pyqtSlot
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QWidget, QMessageBox, QSpacerItem, QSizePolicy
from qasync import asyncSlot

from loggers.logger_configs import set_up_logger
from signals import SignalRepositorySingleton
from services.supabase.controllers.report_workshop.category_controller import CategoryController
from views.componenets.customsComponents.buttons.button_with_loader import ButtonWithLoader
from views.report_workshop.category.category_form import CategoryForm
from views.componenets.customsComponents.table.save_and_cancel_buttons import SaveAndCancelButtonsWithLoader

logger = set_up_logger('main.views.report_workshop.category.categories_dialog')


class CategoryDialog(QDialog):
    def __init__(self, action_type, parent=None):
        super().__init__(parent)

        self.action_type = action_type
        self.setStyleSheet("background-color:#f3f4f6;")

        self.parent = parent
        self.is_category_data_widget = None

        self.category_controller = CategoryController()

        # Signals
        self.signals = SignalRepositorySingleton.instance()

        central_widget = QWidget(self)
        central_widget.setObjectName("central_widget")

        self.form_widget = CategoryForm()

        main_category_data_vertical_layout = QVBoxLayout()
        main_category_data_vertical_layout.setContentsMargins(20, 20, 20, 20)

        main_category_data_vertical_layout.addWidget(self.form_widget)

        self.save_and_cancel_btns = SaveAndCancelButtonsWithLoader(text="Save")
        self.save_and_cancel_btns.save_btn.clicked.connect(self.add_new_category)
        self.save_and_cancel_btns.cancel_btn.clicked.connect(self.close)

        self.update_btn = ButtonWithLoader("Update", size=QSize(95, 34))
        self.update_btn.clicked.connect(self.update_category)

        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(10)
        controls_layout.setContentsMargins(20, 20, 20, 20)
        controls_layout.setAlignment(Qt.AlignmentFlag.AlignRight)

        controls_layout.addWidget(self.save_and_cancel_btns)
        controls_layout.addWidget(self.update_btn)

        spacer = QSpacerItem(10, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        main_vertical_layout = QHBoxLayout()
        main_vertical_layout.setContentsMargins(0, 0, 0, 0)

        main_vertical_layout.addLayout(main_category_data_vertical_layout)
        main_vertical_layout.addSpacerItem(spacer)

        central_widget.setLayout(main_vertical_layout)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(30, 30, 30, 30)

        self.layout.addWidget(central_widget)
        self.layout.addLayout(controls_layout)

        self.setLayout(self.layout)

        self.setMinimumWidth(500)

        self.setModal(True)

    def validate_data(self):
        category_name = self.form_widget.name_input.text()
        if not category_name:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText("Please enter a valid category Name")
            msg.exec()
        elif category_name == " ":
            QMessageBox.warning(self, "Warning", "Please enter a valid category Name")

        return True

    def get_data(self):
        return {
            'name': self.form_widget.name_input.text(),
            'description': self.form_widget.desc_input.text(),
        }

    @pyqtSlot()
    @asyncSlot()
    async def add_new_category(self):
        if self.validate_data():
            data = self.get_data()
            self.save_and_cancel_btns.save_btn.start()

            is_exist = await self.category_controller.check_if_category_exist(data["name"])
            if is_exist:
                QMessageBox.warning(None, "Warning", f"""Category with name {data["name"]} already exist.""")
                self.save_and_cancel_btns.save_btn.stop()
            else:
                res = await self.category_controller.create_category(data)
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
                        "message": "Successfully created a new category",
                        "duration": 2000,
                    })
                    self.save_and_cancel_btns.save_btn.stop()
                    self.close()

    @pyqtSlot()
    @asyncSlot()
    async def update_category(self):
        if self.validate_data():
            data = self.get_data()

            modified_data = {"updated_at": datetime.datetime.now().isoformat()}
            modified_data.update(data)

            self.update_btn.start()

            is_exist = await self.category_controller.check_if_updated_category_exist(self.parent.table_view.current_id,
                                                                                      modified_data["name"])
            if is_exist:
                QMessageBox.warning(None, "Warning", f"""Category with name {modified_data["name"]} already exist.""")
                self.update_btn.stop()
            else:
                res = await self.category_controller.update_category(
                    category_id=self.parent.table_view.current_id, data=modified_data)
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
                        "message": "Successfully updated category",
                        "duration": 2000,
                    })
