import asyncio

from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QMessageBox, QStackedWidget
from qasync import asyncSlot

from loggers.logger_configs import set_up_logger
from signals import SignalRepositorySingleton
from services.supabase.controllers.report_workshop.category_controller import CategoryController
from views.report_workshop.category.category_dialog import CategoryDialog
from views.componenets.table.mangement.table_header_filtration_component import TableHeaderFiltration
from views.componenets.table.mangement.table_layout import TableLayout

logger = set_up_logger('main.views.category.categories_management_view')


class CategoriesManagementView(QWidget):
    def __init__(self):
        super().__init__()

        self.data = []
        self.is_search_enabled = False
        self.central_widget = None
        self.table_view = None
        self.table_header_filtration = None
        self.add_category_dialog = None
        self.view_category_dialog = None
        self.edit_category_dialog = None

        self.stacked_content_widget = QStackedWidget()

        # Signals
        self.signals = SignalRepositorySingleton.instance()

        # API model
        self.category_controller = CategoryController()

        self.main_h_layout = QHBoxLayout()
        self.main_h_layout.setContentsMargins(10, 10, 10, 10)
        self.main_h_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.main_h_layout.addWidget(self.stacked_content_widget)

        self.setLayout(self.main_h_layout)

        asyncio.create_task(self.get_initial_data())

    async def get_initial_data(self):
        self.data = await self.category_controller.get_items()
        self.setup_table_ui()

    def setup_table_ui(self):
        self.table_view = TableLayout(table_name="categories", data_controller=self.category_controller,
                                      data_columns=["category_id", "name", "description", "created_at", "updated_at"],
                                      column_display_names={
                                          "category_id": "ID",
                                          "name": "Name",
                                          "description": "Description",
                                          "created_at": "Created At",
                                          "updated_at": "Updated At",
                                      },
                                      parent=self)

        self.table_view.update_table_view()

        self.table_header_filtration = TableHeaderFiltration(add_btn_name="Category",
                                                             controller=self.category_controller,
                                                             apply_search=True, search_place_holder="search by name and description",
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

        self.table_header_filtration.add_btn.clicked.connect(self.show_add_category_dialog)
        self.table_view.viewSignal.connect(self.view_category)
        self.table_view.editSignal.connect(self.edit_category)
        self.table_view.deleteSignal.connect(self.delete_category)
        self.set_main_content(self.central_widget)

    def set_main_content(self, content_widget):
        self.stacked_content_widget.addWidget(content_widget)
        self.stacked_content_widget.setCurrentWidget(content_widget)

    def fetch_and_update_table_view(self):
        self.table_view.update_table_view()

    @pyqtSlot()
    @asyncSlot()
    async def refresh_table(self):
        self.data = await self.category_controller.get_items(self.data["current_page"], 10)
        self.fetch_and_update_table_view()

    @pyqtSlot()
    @asyncSlot()
    async def view_category(self):
        if self.table_view.get_current_id():
            self.signals.globalCreateLoadingNotificationSignal.emit("VIEW_CATEGORY")
            data = await self.category_controller.get_category_by_id(self.table_view.get_current_id())
            if not data:
                self.signals.globalLoadingNotificationControllerSignal.emit("VIEW_CATEGORY")
                self.signals.globalCreateMessageNotificationSignal.emit({
                    "message_type": "error",
                    "message": "Error while getting category data.",
                    "duration": 2000,
                })
            else:
                self.view_category_dialog = CategoryDialog("view_category", parent=self)

                self.view_category_dialog.form_widget.name_input.setText(data["name"])
                self.view_category_dialog.form_widget.desc_input.setText(data["description"])
                self.view_category_dialog.form_widget.name_input.setReadOnly(True)
                self.view_category_dialog.form_widget.desc_input.setReadOnly(True)
                self.view_category_dialog.update_btn.hide()
                self.view_category_dialog.save_and_cancel_btns.save_btn.hide()

                self.signals.globalLoadingNotificationControllerSignal.emit("VIEW_CATEGORY")
                self.view_category_dialog.show()

    @pyqtSlot()
    @asyncSlot()
    async def edit_category(self):
        if self.table_view.get_current_id():
            self.signals.globalCreateLoadingNotificationSignal.emit("VIEW_CATEGORY")
            data = await self.category_controller.get_category_by_id(self.table_view.get_current_id())
            if not data:
                self.signals.globalLoadingNotificationControllerSignal.emit("VIEW_CATEGORY")
                self.signals.globalCreateMessageNotificationSignal.emit({
                    "message_type": "error",
                    "message": "Error while getting category data.",
                    "duration": 2000,
                })
            else:
                self.edit_category_dialog = CategoryDialog("Edit Category", parent=self)
                self.edit_category_dialog.form_widget.name_input.setText(data["name"])
                self.edit_category_dialog.form_widget.desc_input.setText(data["description"])
                self.edit_category_dialog.save_and_cancel_btns.hide()

                self.signals.globalLoadingNotificationControllerSignal.emit("VIEW_CATEGORY")
                self.edit_category_dialog.show()

    @pyqtSlot()
    def show_add_category_dialog(self):
        self.add_category_dialog = CategoryDialog("Add Category", parent=self)
        self.add_category_dialog.update_btn.hide()
        self.add_category_dialog.show()

    @pyqtSlot()
    @asyncSlot()
    async def delete_category(self):
        if self.table_view.get_current_id():
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText('Are you sure you want to delete?')
            msg.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
            reply = msg.exec()

            if reply == QMessageBox.StandardButton.Ok:
                self.signals.globalCreateLoadingNotificationSignal.emit("DELETE_CATEGORY")
                data = await self.category_controller.delete_category(self.table_view.get_current_id())
                if not data:
                    self.signals.globalLoadingNotificationControllerSignal.emit("DELETE_CATEGORY")
                    self.signals.globalCreateMessageNotificationSignal.emit({
                        "message_type": "error",
                        "message": "An unexpected error occurred",
                        "duration": 5000,
                    })
                else:
                    await self.refresh_table()
                self.signals.globalLoadingNotificationControllerSignal.emit("DELETE_CATEGORY")
