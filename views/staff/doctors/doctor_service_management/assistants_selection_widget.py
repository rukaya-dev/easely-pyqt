from PyQt6.QtGui import QPixmap, QFont, QIcon
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy, QPushButton, QMessageBox
from PyQt6.QtCore import QSize, Qt, pyqtSlot, QTimer, pyqtSignal
from PyQt6.QtWidgets import QHBoxLayout
from qasync import asyncSlot

from loggers.logger_configs import set_up_logger
from services.supabase.controllers.staff.assistant.assistant_controller import AssistantController

from signals import SignalRepositorySingleton
from views.componenets.customsComponents.custom_scroll_area import CustomScrollArea
from views.componenets.customsComponents.custom_searchbar import CustomSearchBar
from views.componenets.customsComponents.dates_and_times.created_updated_at_filter_component import \
    CreatedUpdatedAtFilterWidget
from views.componenets.customsComponents.loaders.internal_loader import InternalLoader
from views.componenets.customsComponents.menus.custom_view_option_menu import CustomViewOptionMenu
from views.componenets.customsComponents.table.form_componenets.custom_label import CustomLabel
from views.staff.assistants.assistant_dialog import AssistantDialog

logger = set_up_logger('main.views.staff.doctors.doctor_service_management.assistants_selection_widget')


def generate_label(label_content):
    widget = QWidget()
    widget.setStyleSheet("border:0;")

    item_content = QLabel(label_content)
    item_content.setAlignment(Qt.AlignmentFlag.AlignCenter)
    item_content.setStyleSheet("background-color:#F3F4F6;border-radius:7px;color:black;padding:5px;")

    item_layout = QHBoxLayout()
    item_layout.setContentsMargins(0, 0, 0, 0)
    item_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
    item_layout.setSpacing(10)

    item_layout.addWidget(item_content)

    widget.setLayout(item_layout)

    return widget


class AssistantsSelectionWidget(QWidget):
    assistantRevertedSignal = pyqtSignal()
    updateDialogHeightSignal = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.parent = parent
        self.not_data_widget = None

        self.assistant_controller = AssistantController()

        # Signals
        self.signals = SignalRepositorySingleton.instance()

        self.label_policy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

        central_widget = QWidget(self)
        central_widget.setStyleSheet("""
                  background-color:white;
              """)

        scroll_area = CustomScrollArea(self)
        scroll_area.setWidget(central_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setContentsMargins(0, 0, 0, 0)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # search bar and filteration
        self.search_bar = CustomSearchBar()
        self.search_bar.search_bar.setPlaceholderText("search by first name, last name and role")
        self.search_bar.search_bar.textChanged.connect(self.on_search_text_change)

        self.filter_widget = CreatedUpdatedAtFilterWidget(menu_pos="right", parent=self)

        self.filter_widget.clear_button.button.clicked.connect(self.clear_filter)
        self.filter_widget.save_and_cancel_buttons_widget.save_btn.clicked.connect(self.apply_filter)

        self.internal_loader = InternalLoader(height=30, parent=self)

        self.search_filter_layout = QHBoxLayout()
        self.search_filter_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.search_filter_layout.setSpacing(0)
        self.search_filter_layout.setContentsMargins(0, 0, 0, 0)

        self.search_filter_layout.addWidget(self.search_bar)
        self.search_filter_layout.addWidget(self.filter_widget)
        self.search_filter_layout.addWidget(self.internal_loader)

        self.assistants_content_widgets = QLabel("")
        self.selected_assistants_content_widgets = SelectedAssistantsWidget()

        self.search_assistant_content_layout = QVBoxLayout()
        self.search_assistant_content_layout.setSpacing(20)
        self.search_assistant_content_layout.setContentsMargins(0, 0, 0, 0)

        self.search_assistant_content_layout.addLayout(self.search_filter_layout)
        self.search_assistant_content_layout.addWidget(self.assistants_content_widgets)
        self.search_assistant_content_layout.addWidget(self.selected_assistants_content_widgets)

        assistant_header_search_content_vertical_layout = QVBoxLayout()
        assistant_header_search_content_vertical_layout.setContentsMargins(10, 0, 10, 0)

        assistant_header_search_content_vertical_layout.addLayout(self.search_assistant_content_layout)

        central_widget.setLayout(assistant_header_search_content_vertical_layout)

        main_vertical_layout = QVBoxLayout()
        main_vertical_layout.setSpacing(0)
        main_vertical_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        main_vertical_layout.setContentsMargins(0, 0, 0, 0)

        main_vertical_layout.addWidget(scroll_area)

        self.setLayout(main_vertical_layout)
        self.setMinimumSize(600, 400)

    def re_render_assistant_content_widget(self, data):
        # Create the new widget
        new_assistants_content_widgets = self.render_assistant_widgets(data)

        if self.assistants_content_widgets is not None:
            self.search_assistant_content_layout.removeWidget(self.assistants_content_widgets)
            self.assistants_content_widgets.deleteLater()

        # Update the reference to the new widget
        self.assistants_content_widgets = new_assistants_content_widgets

        # Insert the new widget at the correct position
        if self.assistants_content_widgets:
            self.search_assistant_content_layout.insertWidget(1, self.assistants_content_widgets)

            # Update the layout
            self.search_assistant_content_layout.update()

    def render_assistant_widgets(self, data):
        if data:
            central_widget = QWidget()
            central_widget.setStyleSheet("border:0;background-color:transparent;")

            layout = QVBoxLayout()
            layout.setAlignment(Qt.AlignmentFlag.AlignTop)
            layout.setSpacing(10)
            layout.setContentsMargins(0, 0, 0, 0)

            central_widget.setLayout(layout)

            for item in data:
                item_name = item["first_name"] + " " + item["last_name"]
                if item["assistant_id"] not in self.selected_assistants_content_widgets.selected_assistants_data:
                    main_layout = QHBoxLayout()
                    main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
                    main_layout.setContentsMargins(10, 10, 10, 10)

                    main_widget = QWidget()
                    main_widget.setFixedHeight(50)
                    main_widget.setStyleSheet("border:0;background-color:#F3F4F6;")
                    main_widget.setLayout(main_layout)
                    main_widget.setProperty("id", item["assistant_id"])

                    controls_layout = QHBoxLayout()
                    controls_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
                    controls_layout.setSpacing(0)
                    controls_layout.setContentsMargins(0, 0, 0, 0)

                    add_button = ControlButton(icon_path=":/resources/icons/active_plus.svg")
                    add_button.clicked.connect(lambda _, assistant_id=item["assistant_id"], assistant_name=item_name:
                                               self.add_assistant(assistant_id, assistant_name))

                    options_menu = CustomViewOptionMenu()
                    options_menu.view_action.triggered.connect(
                        lambda _, assistant_id=item["assistant_id"]: self.view_assistant(assistant_id))

                    name = generate_label(item_name)

                    controls_layout.addWidget(add_button)
                    controls_layout.addWidget(options_menu)

                    main_layout.addWidget(name, Qt.AlignmentFlag.AlignRight)
                    main_layout.addLayout(controls_layout)

                    layout.addWidget(main_widget)
                    central_widget.updateGeometry()

                    self.signals.doctorServiceFormWidgetNewContentIsAddedSignal.emit()

            return central_widget

    @pyqtSlot(str)
    def on_search_text_change(self, text):
        QTimer.singleShot(100, lambda: (self.search_assistant(text)))

    @asyncSlot(str)
    async def search_assistant(self, text):
        self.internal_loader.start()
        if len(text) >= 1:
            self.assistant_controller.store.set_search_text(text)
            await self.refresh_assistant_content()

        else:
            self.re_render_assistant_content_widget([])
        self.internal_loader.stop()

    @pyqtSlot()
    @asyncSlot()
    async def clear_filter(self):
        self.internal_loader.start()
        self.filter_widget.created_at_date_filter_selection.check_box.setChecked(False)
        self.filter_widget.updated_at_date_filter_selection.check_box.setChecked(False)
        self.assistant_controller.store.set_filter_preferences({})

        if not self.search_bar.search_bar.text():
            self.re_render_assistant_content_widget([])
        else:
            await self.refresh_assistant_content()
        self.internal_loader.stop()
        self.filter_widget.custom_drop_down_menu.menu.close()

    @pyqtSlot()
    @asyncSlot()
    async def apply_filter(self):
        self.filter_widget.save_and_cancel_buttons_widget.save_btn.start()

        created_at = self.filter_widget.created_at_date_filter_selection.custom_date_range_selection_widget.selection_widget.custom_date_calendar.selectedDate().toString()
        updated_at = self.filter_widget.updated_at_date_filter_selection.custom_date_range_selection_widget.selection_widget.custom_date_calendar.selectedDate().toString()

        preferences = {
            "created_at": {
                "enabled": False,
                "filteration_type": "",
                "preset_filter_id": "",
                "custom_date_value": "",
            },
            "updated_at": {
                "enabled": False,
                "filteration_type": "",
                "preset_filter_id": "",
                "custom_date_value": "",
            },
        }

        if self.filter_widget.created_at_date_filter_selection.check_box.isChecked():
            preferences["created_at"]["enabled"] = True
            present_filter_checked_action = self.filter_widget.created_at_date_filter_selection.preset_date_filter_selection_widget.menu.actions_group.checkedAction()
            if present_filter_checked_action:
                preferences["created_at"]["filteration_type"] = "preset_filter"
                preset_filter_data = present_filter_checked_action.data()
                preferences["created_at"]["preset_filter_id"] = preset_filter_data["id"]
            else:
                preferences["created_at"]["filteration_type"] = "custom_filter"
                preferences["created_at"]["custom_date_value"] = created_at

        if self.filter_widget.updated_at_date_filter_selection.check_box.isChecked():
            preferences["created_at"]["enabled"] = True
            present_filter_checked_action = self.filter_widget.updated_at_date_filter_selection.preset_date_filter_selection_widget.menu.actions_group.checkedAction()
            if present_filter_checked_action:
                preferences["updated_at"]["filteration_type"] = "preset_filter"
                preset_filter_data = present_filter_checked_action.data()
                preferences["updated_at"]["preset_filter_id"] = preset_filter_data["id"]
            else:
                preferences["updated_at"]["filteration_type"] = "custom_filter"
                preferences["updated_at"]["custom_date_value"] = updated_at

        self.assistant_controller.store.set_filter_preferences(preferences)
        await self.refresh_assistant_content()

        self.filter_widget.save_and_cancel_buttons_widget.save_btn.stop()
        self.filter_widget.custom_drop_down_menu.menu.close()

    @pyqtSlot(int)
    @asyncSlot()
    async def view_assistant(self, assistant_id):
        self.internal_loader.start()
        data = await self.assistant_controller.get_assistant_by_id(assistant_id)
        if not data:
            QMessageBox.critical(None, "Critical", """Could not fetch assistant data""",
                                 QMessageBox.StandardButton.Ok)

        else:
            self.assistant_view_dialog = AssistantDialog("view", parent=self)
            self.view_assistant_information_widget = self.assistant_view_dialog.form_widget

            # setting assistant data
            self.view_assistant_information_widget.first_name_input.setText(data["first_name"])
            self.view_assistant_information_widget.last_name_input.setText(data["last_name"])
            self.view_assistant_information_widget.qualifications_input.setText(data["qualifications"])
            self.view_assistant_information_widget.email_input.setText(data["email"])
            self.view_assistant_information_widget.phone_number_input.setText(data["phone_number"])
            self.view_assistant_information_widget.address_input.setText(data["address"])
            self.view_assistant_information_widget.role_input.setText(data["role"])

            self.view_assistant_information_widget.first_name_input.setReadOnly(True)
            self.view_assistant_information_widget.last_name_input.setReadOnly(True)
            self.view_assistant_information_widget.qualifications_input.setDisabled(True)
            self.view_assistant_information_widget.email_input.setReadOnly(True)
            self.view_assistant_information_widget.phone_number_input.setReadOnly(True)
            self.view_assistant_information_widget.address_input.setDisabled(True)

            self.assistant_view_dialog.update_btn.hide()
            self.assistant_view_dialog.save_and_cancel_btns.save_btn.hide()

            self.assistant_view_dialog.show()
            # 
            self.internal_loader.stop()
            self.assistant_view_dialog.show()

    @pyqtSlot(int, str)
    @asyncSlot()
    async def add_assistant(self, assistant_id, assistant_name):
        if assistant_id:
            if assistant_id not in self.selected_assistants_content_widgets.selected_assistants_data:
                self.internal_loader.start()

                main_layout = QHBoxLayout()
                main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
                main_layout.setContentsMargins(10, 10, 10, 10)

                main_widget = QWidget()
                main_widget.setFixedHeight(50)
                main_widget.setStyleSheet("border:0;background-color:#F3F4F6;")
                main_widget.setLayout(main_layout)
                main_widget.setObjectName(assistant_name)
                main_widget.setProperty("id", assistant_id)

                controls_layout = QHBoxLayout()
                controls_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
                controls_layout.setSpacing(0)
                controls_layout.setContentsMargins(0, 0, 0, 0)

                remove_button = ControlButton(icon_path=":/resources/icons/active_remove.svg")
                remove_button.clicked.connect(lambda _, assist_id=assistant_id:
                                              self.remove_assistant(assist_id))

                options_menu = CustomViewOptionMenu()
                options_menu.view_action.triggered.connect(
                    lambda _, assist_id=assistant_id: self.view_assistant(assist_id))

                name = generate_label(assistant_name)

                controls_layout.addWidget(remove_button)
                controls_layout.addWidget(options_menu)

                main_layout.addWidget(name, Qt.AlignmentFlag.AlignRight)
                main_layout.addLayout(controls_layout)

                items_layout = self.selected_assistants_content_widgets.items_layout

                items_layout.insertWidget(items_layout.count() - 1, main_widget, 1)
                items_layout.update()

                self.selected_assistants_content_widgets.selected_assistants_label.setVisible(True)
                self.selected_assistants_content_widgets.updateGeometry()
                self.selected_assistants_content_widgets.selected_assistants_data.append(assistant_id)

                # Remove it from already rendered
                already_rendered_items_layout = self.assistants_content_widgets.layout()

                for i in range(already_rendered_items_layout.count()):
                    assistant_widget = already_rendered_items_layout.itemAt(i)
                    if assistant_widget and assistant_widget.widget():
                        if assistant_widget.widget().property("id") == assistant_id:
                            already_rendered_items_layout.removeWidget(assistant_widget.widget())

                already_rendered_items_layout.update()
                self.assistants_content_widgets.updateGeometry()

                self.internal_loader.stop()

    @pyqtSlot(int, str)
    @asyncSlot()
    async def remove_assistant(self, assistant_id):
        self.internal_loader.start()
        if assistant_id and assistant_id in self.selected_assistants_content_widgets.selected_assistants_data:
            items_layout = self.selected_assistants_content_widgets.items_layout

            for i in range(items_layout.count()):
                assistant_widget = items_layout.itemAt(i)
                if assistant_widget and assistant_widget.widget():
                    if assistant_widget.widget().property("id") == assistant_id:
                        items_layout.removeWidget(assistant_widget.widget())

            items_layout.update()
            self.selected_assistants_content_widgets.updateGeometry()

        if assistant_id in self.selected_assistants_content_widgets.selected_assistants_data:
            self.selected_assistants_content_widgets.selected_assistants_data.remove(assistant_id)
        self.internal_loader.stop()

    @pyqtSlot()
    @asyncSlot()
    async def refresh_assistant_content(self):
        data = await self.assistant_controller.get_items()
        self.re_render_assistant_content_widget(data["data"])


class ControlButton(QPushButton):

    def __init__(self, icon_path, parent=None):
        super().__init__(parent)

        font = QFont("arial")
        font.setPixelSize(14)
        self.setFont(font)

        self.setStyleSheet(""" 
        QPushButton {
            border: 0;
            border-radius:20px;
            background-color: transparent; 
        }
        QPushButton:hover {
            border-radius:15px;
            background-color: white; 
        }
        """)

        icon_pixmap = QPixmap(icon_path)
        icon = QIcon(icon_pixmap)

        self.setIcon(icon)
        self.setIconSize(QSize(24, 24))
        self.setFixedSize(QSize(30, 30))
        self.setText("")


class SelectedAssistantsWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.selected_assistants_data = []

        central_widget = QWidget()
        central_widget.setStyleSheet("border:0;background-color:transparent;")

        self.items_layout = QVBoxLayout()
        self.items_layout.setSpacing(10)
        self.items_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.items_layout.setContentsMargins(0, 0, 0, 0)

        central_widget.setLayout(self.items_layout)

        self.selected_assistants_label = CustomLabel("Selected Assistants")
        self.selected_assistants_label.setVisible(False)

        font = self.selected_assistants_label.font()
        font.setPixelSize(14)
        font.setWeight(font.Weight.DemiBold)

        self.selected_assistants_label.setFont(font)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setSpacing(10)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(self.selected_assistants_label)
        layout.addWidget(central_widget)

        self.setLayout(layout)
