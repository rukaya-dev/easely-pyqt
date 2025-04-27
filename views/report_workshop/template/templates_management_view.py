import asyncio

from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QMessageBox, QStackedWidget
from qasync import asyncSlot

from loggers.logger_configs import set_up_logger
from services.supabase.controllers.report_workshop.category_controller import CategoryController
from services.supabase.controllers.report_workshop.option_controller import OptionController
from services.supabase.controllers.report_workshop.template_controller import TemplateController
from signals import SignalRepositorySingleton
from views.componenets.table.mangement.table_header_filtration_component import TableHeaderFiltration
from views.componenets.table.mangement.table_layout import TableLayout
from views.report_workshop.template.template_dialog import TemplateDialog
from views.report_workshop.template.template_filter_widget import FilterWidget

logger = set_up_logger('main.views.template.templates_management_view')


class TemplatesManagementView(QWidget):
    def __init__(self):
        super().__init__()

        self.data = []
        self.table_view = None
        self.table_header_filtration = None
        self.add_template_dialog = None
        self.template_view = None
        self.edit_template_dialog = None
        self.categories = None

        self.stacked_content_widget = QStackedWidget()

        # Signals
        self.signals = SignalRepositorySingleton.instance()

        # API model
        self.template_controller = TemplateController()
        self.category_controller = CategoryController()
        self.option_controller = OptionController()

        self.main_h_layout = QHBoxLayout()
        self.main_h_layout.setContentsMargins(10, 10, 10, 10)
        self.main_h_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.main_h_layout.addWidget(self.stacked_content_widget)

        self.setLayout(self.main_h_layout)

        asyncio.create_task(self.get_initial_data())

    async def get_initial_data(self):
        self.signals.globalCreateLoadingNotificationSignal.emit("GET_TEMPLATES_LIST")
        self.data = await self.template_controller.get_items(1, 10)
        await self.get_categories()
        self.setup_table_ui()
        self.signals.globalLoadingNotificationControllerSignal.emit("GET_TEMPLATES_LIST")

    def setup_table_ui(self):
        self.table_view = TableLayout(table_name="templates", data_controller=self.template_controller,
                                      data_columns=["template_id", "name", "category_id", "template_description",
                                                    "created_at", "updated_at"],
                                      column_display_names={
                                          "template_id": "ID",
                                          "name": "Name",
                                          "category_id": "Category",
                                          "template_description": "Description",
                                          "created_at": "Created At",
                                          "updated_at": "Updated At",
                                      },
                                      parent=self)

        self.table_view.update_table_view()

        self.filter_widget = FilterWidget(self.categories, template_controller=self.template_controller,
                                          parent=self)

        self.table_header_filtration = TableHeaderFiltration(add_btn_name="Template",
                                                             controller=self.template_controller,
                                                             apply_search=True,
                                                             apply_filter=True, page_filter_widget=self.filter_widget,
                                                             search_place_holder="search by name, category and description",
                                                             parent=self)
        central_widget = QWidget()

        table_content_v_layout = QVBoxLayout()
        central_widget.setLayout(table_content_v_layout)

        table_content_v_layout.setContentsMargins(0, 0, 0, 0)
        table_content_v_layout.setSpacing(0)

        table_header_with_table_layout = QVBoxLayout()
        table_header_with_table_layout.setContentsMargins(0, 10, 0, 0)
        table_header_with_table_layout.setSpacing(0)

        table_header_with_table_layout.addWidget(self.table_header_filtration)
        table_header_with_table_layout.addWidget(self.table_view)
        table_content_v_layout.addLayout(table_header_with_table_layout)

        self.table_header_filtration.add_btn.clicked.connect(self.show_add_template_dialog)
        self.table_view.viewSignal.connect(self.view_template)
        self.table_view.editSignal.connect(self.edit_template)
        self.table_view.deleteSignal.connect(self.delete_template)
        self.set_main_content(central_widget)

    def set_main_content(self, content_widget):
        self.stacked_content_widget.addWidget(content_widget)
        self.stacked_content_widget.setCurrentWidget(content_widget)

    def fetch_and_update_table_view(self):
        self.table_view.update_table_view()

    @pyqtSlot()
    @asyncSlot()
    async def refresh_table(self):
        self.data = await self.template_controller.get_items(self.data["current_page"], 10)
        self.fetch_and_update_table_view()

    @pyqtSlot()
    @asyncSlot()
    async def view_template(self):
        if self.table_view.get_current_id():
            self.signals.globalCreateLoadingNotificationSignal.emit("VIEW_TEMPLATE")

            data = await self.template_controller.get_template_by_id(self.table_view.get_current_id())

            if not data:
                self.signals.globalLoadingNotificationControllerSignal.emit("VIEW_TEMPLATE")
                self.signals.globalCreateMessageNotificationSignal.emit({
                    "message_type": "error",
                    "message": "Error while getting template data.",
                    "duration": 2000,
                })
            else:
                self.template_view = TemplateDialog(action_type="view", parent=self)
                await self.template_view.template_from_widget.populate_categories()

                template_form_widget = self.template_view.template_from_widget
                editor_widget = self.template_view.editor_view

                template_form_widget.template_name_input.setText(data["name"])
                template_form_widget.desc_input.setText(data["description"])
                template_form_widget.category_combo.setCurrentText(data["category_id"])

                editor_widget.zeus_editor_text_box.insertHtml(data["content"])
                editor_widget.zeus_editor_text_box.update_options_list(data["template_options"])

                editor_widget.options_widget.add_options_to_list_view(data["template_options"])

                editor_widget.options_widget.set_checked_items_by_default(data["template_options"])

                editor_widget.setDisabled(True)
                template_form_widget.setDisabled(True)

                self.template_view.header_widget.save_btn.hide()

                self.signals.globalLoadingNotificationControllerSignal.emit("VIEW_TEMPLATE")
                self.template_view.showMaximized()

    @pyqtSlot()
    @asyncSlot()
    async def edit_template(self):
        if self.table_view.get_current_id():
            self.signals.globalCreateLoadingNotificationSignal.emit("VIEW_TEMPLATE")

            data = await self.template_controller.get_template_by_id(self.table_view.get_current_id())
            category_options = await self.option_controller.get_options_by_category(data["category_id"])

            if not data:
                self.signals.globalLoadingNotificationControllerSignal.emit("VIEW_TEMPLATE")
                self.signals.globalCreateMessageNotificationSignal.emit({
                    "message_type": "error",
                    "message": "Error while getting template data.",
                    "duration": 2000,
                })
            else:
                self.template_view = TemplateDialog(action_type="update", parent=self)
                await self.template_view.template_from_widget.populate_categories()

                template_form_widget = self.template_view.template_from_widget
                editor_widget = self.template_view.editor_view

                template_form_widget.template_name_input.setText(data["name"])
                template_form_widget.desc_input.setText(data["description"])
                template_form_widget.category_combo.setCurrentText(data["category_id"])

                template_form_widget.category_combo.setDisabled(True)
                template_form_widget.category_combo.setToolTip(
                    "template category cannot be updated, create new template instead.")

                editor_widget.zeus_editor_text_box.insertHtml(data["content"])

                if data["template_options"]:
                    editor_widget.zeus_editor_text_box.update_options_list(data["template_options"])

                combined_categories = []
                if data["template_options"]:
                    combined_categories.extend(data["template_options"])

                if category_options:
                    for option in category_options:
                        if option["slug"] not in combined_categories:
                            combined_categories.append(option["slug"])

                editor_widget.options_widget.add_options_to_list_view(combined_categories)

                editor_widget.options_widget.set_checked_items_by_default(data["template_options"])

                self.template_view.header_widget.save_btn.hide()

                self.signals.globalLoadingNotificationControllerSignal.emit("VIEW_TEMPLATE")
                self.template_view.showMaximized()

    @pyqtSlot()
    @asyncSlot()
    async def show_add_template_dialog(self):
        self.template_view = TemplateDialog(action_type="create", parent=self)
        await self.template_view.template_from_widget.populate_categories()
        self.template_view.showMaximized()

    @pyqtSlot()
    @asyncSlot()
    async def delete_template(self):
        if self.table_view.get_current_id():
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText('Are you sure you want to delete?')
            msg.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
            reply = msg.exec()

            if reply == QMessageBox.StandardButton.Ok:
                self.signals.globalCreateLoadingNotificationSignal.emit("DELETE_TEMPLATE")
                data = await self.template_controller.delete_template(self.table_view.get_current_id())
                if not data:
                    self.signals.globalLoadingNotificationControllerSignal.emit("DELETE_TEMPLATE")
                    self.signals.globalCreateMessageNotificationSignal.emit({
                        "message_type": "error",
                        "message": "An unexpected error occurred",
                        "duration": 5000,
                    })
                else:
                    await self.refresh_table()
                self.signals.globalLoadingNotificationControllerSignal.emit("DELETE_TEMPLATE")

    @asyncSlot()
    async def get_categories(self):
        self.categories = await self.category_controller.get_all_categories()
