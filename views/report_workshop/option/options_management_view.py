import asyncio

from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QStandardItem
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QMessageBox, QStackedWidget
from qasync import asyncSlot

from loggers.logger_configs import set_up_logger
from services.supabase.controllers.report_workshop.category_controller import CategoryController
from services.supabase.controllers.report_workshop.option_controller import OptionController
from signals import SignalRepositorySingleton
from views.componenets.table.mangement.table_header_filtration_component import TableHeaderFiltration
from views.componenets.table.mangement.table_layout import TableLayout
from views.report_workshop.option.option_dialog import OptionDialog
from views.report_workshop.option.option_filter_widget import FilterWidget

logger = set_up_logger('main.views.option.options_management_view')


class OptionsManagementView(QWidget):
    def __init__(self):
        super().__init__()

        self.data = []
        self.table_view = None
        self.table_header_filtration = None
        self.add_option_dialog = None
        self.view_option_dialog = None
        self.edit_option_dialog = None

        self.stacked_content_widget = QStackedWidget()

        # Signals
        self.signals = SignalRepositorySingleton.instance()

        # API model
        self.option_controller = OptionController()
        self.category_controller = CategoryController()

        self.main_h_layout = QHBoxLayout()
        self.main_h_layout.setContentsMargins(10, 10, 10, 10)
        self.main_h_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.main_h_layout.addWidget(self.stacked_content_widget)

        self.setLayout(self.main_h_layout)

        asyncio.create_task(self.get_initial_data())

    async def get_initial_data(self):
        self.data = await self.option_controller.get_items(1, 10)
        await self.get_categories()
        self.setup_table_ui()

    def setup_table_ui(self):
        self.table_view = TableLayout(table_name="options", data_controller=self.option_controller,
                                      data_columns=["option_id", "name", "category_id", "option_description",
                                                    "created_at", "updated_at"],
                                      column_display_names={
                                          "option_id": "ID",
                                          "name": "Name",
                                          "category_id": "Category",
                                          "option_description": "Description",
                                          "created_at": "Created At",
                                          "updated_at": "Updated At",
                                      },
                                      parent=self)

        self.table_view.update_table_view()

        self.filter_widget = FilterWidget(categories_controller=self.category_controller,
                                          option_controller=self.option_controller,
                                          parent=self)

        self.table_header_filtration = TableHeaderFiltration(add_btn_name="Option",
                                                             controller=self.option_controller,
                                                             apply_search=True,
                                                             apply_filter=True, page_filter_widget=self.filter_widget,
                                                             search_place_holder="search by name, category and description",
                                                             parent=self)
        self.central_widget = QWidget()

        table_content_v_layout = QVBoxLayout()
        self.central_widget.setLayout(table_content_v_layout)

        table_content_v_layout.setContentsMargins(0, 0, 0, 0)
        table_content_v_layout.setSpacing(0)

        table_header_with_table_layout = QVBoxLayout()
        table_header_with_table_layout.setContentsMargins(0, 10, 0, 0)
        table_header_with_table_layout.setSpacing(0)

        table_header_with_table_layout.addWidget(self.table_header_filtration)
        table_header_with_table_layout.addWidget(self.table_view)
        table_content_v_layout.addLayout(table_header_with_table_layout)

        self.table_header_filtration.add_btn.clicked.connect(self.show_add_option_dialog)
        self.table_view.viewSignal.connect(self.view_option)
        self.table_view.editSignal.connect(self.edit_option)
        self.table_view.deleteSignal.connect(self.delete_option)
        self.set_main_content(self.central_widget)

    def set_main_content(self, content_widget):
        self.stacked_content_widget.addWidget(content_widget)
        self.stacked_content_widget.setCurrentWidget(content_widget)

    def fetch_and_update_table_view(self):
        self.table_view.update_table_view()

    @pyqtSlot()
    @asyncSlot()
    async def refresh_table(self):
        self.data = await self.option_controller.get_items(self.data["current_page"], 10)
        self.fetch_and_update_table_view()

    @pyqtSlot()
    @asyncSlot()
    async def view_option(self):
        if self.table_view.get_current_id():
            self.signals.globalCreateLoadingNotificationSignal.emit("VIEW_OPTION")
            data = await self.option_controller.get_option_by_id(self.table_view.get_current_id())
            if not data:
                self.signals.globalLoadingNotificationControllerSignal.emit("VIEW_OPTION")
                self.signals.globalCreateMessageNotificationSignal.emit({
                    "message_type": "error",
                    "message": "Error while getting option data.",
                    "duration": 2000,
                })
            else:
                self.view_option_dialog = OptionDialog(category_controller=self.category_controller, parent=self)

                self.view_option_dialog.form_widget.option_name_input.setText(data["name"])
                self.view_option_dialog.form_widget.category_combo.setCurrentText(data["category_id"])
                self.view_option_dialog.form_widget.desc_input.setText(data["description"])
                self.view_option_dialog.form_widget.treeWidget.renderTree(data["option_structure"])

                self.view_option_dialog.form_widget.option_name_input.setReadOnly(True)
                self.view_option_dialog.form_widget.desc_input.setReadOnly(True)
                self.view_option_dialog.form_widget.category_combo.setDisabled(True)
                self.view_option_dialog.form_widget.treeWidget.setDisabled(True)


                self.view_option_dialog.update_btn.hide()
                self.view_option_dialog.save_and_cancel_btns.save_btn.hide()

                self.signals.globalLoadingNotificationControllerSignal.emit("VIEW_OPTION")
                self.view_option_dialog.show()

    @pyqtSlot()
    @asyncSlot()
    async def edit_option(self):
        if self.table_view.get_current_id():
            self.signals.globalCreateLoadingNotificationSignal.emit("VIEW_OPTION")

            data = await self.option_controller.get_option_by_id(self.table_view.get_current_id())

            if not data:
                self.signals.globalLoadingNotificationControllerSignal.emit("VIEW_OPTION")
                self.signals.globalCreateMessageNotificationSignal.emit({
                    "message_type": "error",
                    "message": "Error while getting option data.",
                    "duration": 2000,
                })
            else:
                self.view_option_dialog = OptionDialog(category_controller=self.category_controller, parent=self)

                self.view_option_dialog.form_widget.option_name_input.setText(data["name"])
                self.view_option_dialog.form_widget.category_combo.setCurrentText(data["category_id"])
                self.view_option_dialog.form_widget.desc_input.setText(data["description"])

                self.view_option_dialog.form_widget.treeWidget.renderTree(data["option_structure"])

                self.view_option_dialog.save_and_cancel_btns.save_btn.hide()

                self.signals.globalLoadingNotificationControllerSignal.emit("VIEW_OPTION")
                self.view_option_dialog.show()

    @pyqtSlot()
    def show_add_option_dialog(self):
        self.add_option_dialog = OptionDialog(category_controller=self.category_controller, parent=self)
        self.add_option_dialog.update_btn.hide()
        self.add_option_dialog.show()

    @pyqtSlot()
    @asyncSlot()
    async def delete_option(self):
        if self.table_view.get_current_id():
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText('Are you sure you want to delete?')
            msg.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
            reply = msg.exec()

            if reply == QMessageBox.StandardButton.Ok:
                self.signals.globalCreateLoadingNotificationSignal.emit("DELETE_OPTION")
                data = await self.option_controller.delete_option(self.table_view.get_current_id())
                if not data:
                    self.signals.globalLoadingNotificationControllerSignal.emit("DELETE_OPTION")
                    self.signals.globalCreateMessageNotificationSignal.emit({
                        "message_type": "error",
                        "message": "An unexpected error occurred",
                        "duration": 5000,
                    })
                else:
                    await self.refresh_table()
                self.signals.globalLoadingNotificationControllerSignal.emit("DELETE_OPTION")

    @asyncSlot()
    async def get_categories(self):
        await self.category_controller.get_all_categories()
