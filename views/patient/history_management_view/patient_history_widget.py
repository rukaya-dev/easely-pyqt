import json
import os

from PyQt6 import QtGui, QtCore
from PyQt6.QtGui import QPixmap, QFont, QIcon
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy, QPushButton
from PyQt6.QtCore import QSize, Qt, pyqtSlot, QTimer, pyqtSignal
from PyQt6.QtWidgets import QHBoxLayout
from qasync import asyncSlot

from loggers.logger_configs import set_up_logger
from services.supabase.controllers.patient.patient_controller import PatientController
from services.supabase.controllers.patient.patient_history_change_logs_controller import \
    PatientHistoryChangeLogsController
from signals import SignalRepositorySingleton
from utils.utlis import convert_to_html_text
from views.componenets.customsComponents.custom_lable_with_icon import CustomLabelWithIcon
from views.componenets.customsComponents.custom_scroll_area import CustomScrollArea
from views.componenets.customsComponents.custom_searchbar import CustomSearchBar
from views.componenets.customsComponents.dates_and_times.change_date_filter_componenet import ChangeDateFilterComponent
from views.componenets.customsComponents.loaders.internal_loader import InternalLoader
from views.componenets.customsComponents.menus.custom_view_option_menu import CustomViewOptionMenu
from views.componenets.customsComponents.messages.no_data_widget import NoDataWidget
from views.patient.history_management_view.history_view_dialog import HistoryViewDialog

logger = set_up_logger('main.views.patient.history.patient_history_widget')


class PatientHistoryWidget(QWidget):
    patientHistoryRevertedSignal = pyqtSignal()

    def __init__(self, data=None, parent=None):
        super().__init__(parent)

        self.parent = parent
        self.data = data
        self.not_data_widget = None

        self.error_message = "An unexpected error occurred"

        self.patient_history_controller = PatientHistoryChangeLogsController()
        self.patient_controller = PatientController()

        # Signals
        self.signals = SignalRepositorySingleton.instance()

        self.label_policy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

        central_widget = QWidget(self)
        central_widget.setStyleSheet("""
                  background-color:white;
              """)

        self.history_label = CustomLabelWithIcon(name="History", icon_path=":resources/icons/black_history.svg",
                                                 icon_size=QSize(19, 16))
        font = self.history_label.font()
        font.setPointSizeF(20)
        font.setBold(True)
        self.history_label.label.setFont(font)
        self.history_label.label.setFixedHeight(70)

        self.internal_loader = InternalLoader(height=30, parent=self)
        history_header_layout = QHBoxLayout()
        history_header_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        history_header_layout.setSpacing(0)

        history_header_layout.addWidget(self.history_label, 0, Qt.AlignmentFlag.AlignLeft)
        history_header_layout.addWidget(self.internal_loader, 1, Qt.AlignmentFlag.AlignRight)

        # search bar and filteration
        self.search_bar = CustomSearchBar()
        self.search_bar.search_bar.textChanged.connect(self.on_search_text_change)

        self.filter_widget = ChangeDateFilterComponent(menu_pos="left", parent=self)

        self.filter_widget.clear_button.button.clicked.connect(self.clear_filter)
        self.filter_widget.save_and_cancel_buttons_widget.save_btn.clicked.connect(self.apply_filter)

        self.search_filter_layout = QHBoxLayout()
        self.search_filter_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.search_filter_layout.setSpacing(0)
        self.search_filter_layout.setContentsMargins(0, 0, 0, 0)

        self.search_filter_layout.addWidget(self.search_bar)
        self.search_filter_layout.addWidget(self.filter_widget)

        self.history_content_widgets = self.render_history_widgets(self.data)

        self.search_history_content_layout = QVBoxLayout()
        self.search_history_content_layout.setSpacing(20)
        self.search_history_content_layout.setContentsMargins(30, 0, 0, 0)

        self.search_history_content_layout.addLayout(self.search_filter_layout)
        self.search_history_content_layout.addWidget(self.history_content_widgets)

        history_header_search_content_vertical_layout = QVBoxLayout()
        history_header_search_content_vertical_layout.setContentsMargins(20, 0, 20, 20)

        history_header_search_content_vertical_layout.addLayout(history_header_layout)

        history_header_search_content_vertical_layout.addLayout(self.search_history_content_layout)

        central_widget.setLayout(history_header_search_content_vertical_layout)

        main_vertical_layout = QVBoxLayout()
        main_vertical_layout.setSpacing(10)
        main_vertical_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        main_vertical_layout.setContentsMargins(0, 0, 0, 0)

        main_vertical_layout.addWidget(central_widget)

        self.setLayout(main_vertical_layout)
        self.setMinimumHeight(768)
        self.setMinimumWidth(600)

    def re_render_history_content_widget(self, data):
        # remove previously rendered widgets
        self.search_history_content_layout.removeWidget(self.history_content_widgets)

        # Re-render history widgets
        self.history_content_widgets = self.render_history_widgets(data)
        self.search_history_content_layout.addWidget(self.history_content_widgets)

    def render_history_widgets(self, data):
        if data:
            central_widget = QWidget()
            central_widget.setStyleSheet(
                """
                QWidget {
                    border:0;
                }
                QLabel {
                    border:0;
                    color:black;
                
                }
                """
            )

            scroll_area = CustomScrollArea(self)
            scroll_area.setWidget(central_widget)
            scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

            layout = QVBoxLayout()
            layout.setAlignment(Qt.AlignmentFlag.AlignTop)
            layout.setSpacing(20)
            layout.setContentsMargins(0, 0, 10, 0)

            central_widget.setLayout(layout)

            for item in data:
                main_vertical_layout = QVBoxLayout()
                main_vertical_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
                main_vertical_layout.setContentsMargins(10, 10, 10, 10)

                main_widget = QWidget()
                main_widget.setObjectName("main_patient_history_widget")
                main_widget.setStyleSheet("""
                    QWidget#main_patient_history_widget {
                        border:1px solid #D5D6D8;
                        border-radius:3px;
                    }
                """)
                main_widget.setMinimumWidth(550)
                main_widget.setFixedHeight(150)
                main_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
                main_widget.setLayout(main_vertical_layout)

                controls_layout = QHBoxLayout()
                controls_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
                controls_layout.setSpacing(0)
                controls_layout.setContentsMargins(0, 0, 0, 0)

                revert_pixmap = QPixmap(":resources/icons/revert.svg")

                revert_icon_label = QLabel()
                revert_icon_label.setFixedSize(25, 25)

                revert_icon_label.setPixmap(revert_pixmap)

                revert_button = RevertButton()
                revert_button.clicked.connect(lambda _, log_id=item["change_id"]: self.revert_history_log(log_id))

                options_menu = CustomViewOptionMenu()
                options_menu.view_action.triggered.connect(
                    lambda _, log_id=item["change_id"]: self.view_patient_history_log_data(log_id))

                controls_layout.addWidget(revert_button)
                controls_layout.addWidget(options_menu)

                main_vertical_layout.addLayout(controls_layout)

                item_type_widget = self.generate_label_and_its_content("Type", item["change_type"])
                item_user_widget = self.generate_label_and_its_content("User", item["changed_by"])
                item_date_widget = self.generate_label_and_its_content("Date", item["change_date"])

                main_vertical_layout.addWidget(item_type_widget)
                main_vertical_layout.addWidget(item_user_widget)
                main_vertical_layout.addWidget(item_date_widget)

                layout.addWidget(main_widget)

            return scroll_area
        else:
            empty_label = QLabel("Empty")

            font = empty_label.font()
            font.setPointSizeF(20)
            font.setWeight(QFont.Weight.Bold)
            empty_label.setFont(font)

            self.not_data_widget = NoDataWidget()
            scaled_pixmap = self.not_data_widget.pixmap.scaled(QSize(200, 200), Qt.AspectRatioMode.KeepAspectRatio,
                                                               Qt.TransformationMode.SmoothTransformation)
            self.not_data_widget.imageLabel.setPixmap(scaled_pixmap)

            main_vertical_layout = QVBoxLayout()
            main_vertical_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            main_vertical_layout.setContentsMargins(10, 10, 10, 10)
            main_vertical_layout.addWidget(self.not_data_widget)

            main_widget = QWidget()
            main_widget.setMinimumSize(600, 150)
            main_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            main_widget.setLayout(main_vertical_layout)

            return main_widget

    @pyqtSlot(str)
    def on_search_text_change(self, text):
        QTimer.singleShot(100, lambda: (self.update_search_filter(text)))

    @asyncSlot(str)
    async def update_search_filter(self, text):
        self.internal_loader.start()
        if len(text) >= 1:
            self.patient_history_controller.store.set_search_text(text)
            await self.refresh_history_content()

        else:
            self.patient_history_controller.store.set_search_text("")
            await self.refresh_history_content()
        self.internal_loader.stop()

    @pyqtSlot()
    @asyncSlot()
    async def clear_filter(self):
        self.internal_loader.start()
        self.filter_widget.change_date_filter_selection.check_box.setChecked(False)
        self.patient_history_controller.store.set_filter_preferences({})

        await self.refresh_history_content()
        self.internal_loader.stop()
        self.filter_widget.custom_drop_down_menu.menu.close()

    @pyqtSlot()
    @asyncSlot()
    async def apply_filter(self):
        self.filter_widget.save_and_cancel_buttons_widget.save_btn.start()
        current_patient_data = self.patient_controller.store.get_patient()

        change_date = self.filter_widget.change_date_filter_selection.custom_date_range_selection_widget.selection_widget.custom_date_calendar.selectedDate().toString()

        preferences = {
            "patient_id": current_patient_data["patient_id"],
            "change_date": {
                "enabled": False,
                "filteration_type": "",
                "preset_filter_id": "",
                "custom_date_value": "",
            },
        }

        if self.filter_widget.change_date_filter_selection.check_box.isChecked():
            preferences["change_date"]["enabled"] = True
            present_filter_checked_action = self.filter_widget.change_date_filter_selection.preset_date_filter_selection_widget.menu.actions_group.checkedAction()
            if present_filter_checked_action:
                preferences["change_date"]["filteration_type"] = "preset_filter"
                preset_filter_data = present_filter_checked_action.data()
                preferences["change_date"]["preset_filter_id"] = preset_filter_data["id"]
            else:
                preferences["change_date"]["filteration_type"] = "custom_filter"
                preferences["change_date"]["custom_date_value"] = change_date

        self.patient_history_controller.store.set_filter_preferences(preferences)
        await self.refresh_history_content()

        self.filter_widget.save_and_cancel_buttons_widget.save_btn.stop()
        self.filter_widget.custom_drop_down_menu.menu.close()

    @pyqtSlot(int)
    @asyncSlot()
    async def view_patient_history_log_data(self, log_id):
        self.internal_loader.start()
        data = await self.patient_history_controller.get_history_by_id(log_id)
        if not data:
            self.signals.globalCreateMessageNotificationSignal.emit({
                "message_type": "error",
                "message": "Could not get patient history log data.",
                "duration": 2000,
            })
        else:
            data = self.patient_history_controller.store.get_history_record()
            history_view_dialog = HistoryViewDialog(parent=self)

            history_view_dialog.form_widget.action_type_input.setText(data["change_type"])
            history_view_dialog.form_widget.changed_by_input.setText(data["changed_by"])
            history_view_dialog.form_widget.change_date_input.setText(data["change_date"])

            data_before_as_html = convert_to_html_text(json.loads(data["data_before"]))
            history_view_dialog.form_widget.data_before_input.setText(data_before_as_html)

            data_after_as_html = convert_to_html_text(json.loads(data["data_after"]))
            history_view_dialog.form_widget.data_after_input.setText(data_after_as_html)

            history_view_dialog.form_widget.details_input.setText(data["details"])

            history_view_dialog.form_widget.action_type_input.setReadOnly(True)
            history_view_dialog.form_widget.changed_by_input.setReadOnly(True)
            history_view_dialog.form_widget.change_date_input.setReadOnly(True)
            history_view_dialog.form_widget.data_before_input.setReadOnly(True)
            history_view_dialog.form_widget.data_after_input.setReadOnly(True)
            history_view_dialog.form_widget.details_input.setReadOnly(True)

            history_view_dialog.update_btn.hide()
            history_view_dialog.save_and_cancel_btns.save_btn.hide()

            self.internal_loader.stop()

            history_view_dialog.show()

    @pyqtSlot(int)
    @asyncSlot()
    async def revert_history_log(self, log_id):
        self.internal_loader.start()
        data = await self.patient_history_controller.get_history_by_id(log_id)
        if not data:
            self.signals.globalCreateMessageNotificationSignal.emit({
                "message_type": "error",
                "message": self.error_message,
                "duration": 3000,
            })
            self.internal_loader.stop()
        else:
            res = await self.patient_history_controller.revert_history_record(data)
            if not res:
                self.signals.globalCreateMessageNotificationSignal.emit({
                    "message_type": "error",
                    "message": self.error_message,
                    "duration": 3000,
                })
                self.internal_loader.stop()
            else:
                await self.refresh_history_content()
                self.signals.updatePatientsTableSignal.emit()
                self.internal_loader.stop()

    @pyqtSlot()
    @asyncSlot()
    async def refresh_history_content(self):
        current_patient_data = self.patient_controller.store.get_patient()
        self.data = await self.patient_history_controller.get_items(patient_id=current_patient_data["patient_id"],
                                                                    page_number=1,
                                                                    item_per_page=10)
        if not self.data:
            self.signals.globalCreateMessageNotificationSignal.emit({
                "message_type": "error",
                "message": self.error_message,
                "duration": 3000,
            })
            self.filter_widget.save_and_cancel_buttons_widget.save_btn.stop()
        else:
            self.re_render_history_content_widget(self.data["data"])

            self.signals.globalCreateMessageNotificationSignal.emit({
                "message_type": "success",
                "message": "Successful get patients filtered data.",
                "duration": 1000,
            })

    def generate_label_and_its_content(self, label_name, label_content):
        widget = QWidget()

        item_label = QLabel(label_name)
        item_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        item_label.setSizePolicy(self.label_policy)
        item_label.setMinimumSize(50, 20)

        item_content = QLabel(label_content)
        item_content.setAlignment(Qt.AlignmentFlag.AlignCenter)
        item_content.setStyleSheet("background-color:#F3F4F6;border-radius:7px;color:black;padding:5px;")

        item_layout = QHBoxLayout()
        item_layout.setContentsMargins(0, 0, 0, 0)
        item_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        item_layout.setSpacing(10)

        item_layout.addWidget(item_label)
        item_layout.addWidget(item_content)

        widget.setLayout(item_layout)

        return widget


class RevertButton(QPushButton):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setGif()

        self.setStyleSheet(""" 
            border: 0;
            background-color: transparent; 
            color: black;
            letter-spacing: 0.3px;
        """)

        icon_pixmap = QPixmap(":resources/icons/revert.svg")
        icon = QIcon(icon_pixmap)

        self.setIcon(icon)
        self.setIconSize(QSize(20, 20))
        self.setFixedSize(QSize(107, 30))
        self.setText("revert")

    @QtCore.pyqtSlot()
    def start(self):
        self.setText("Loading")
        self.setDisabled(True)
        if hasattr(self, "_movie"):
            self._movie.start()

    @QtCore.pyqtSlot()
    def stop(self):
        if hasattr(self, "_movie"):
            self._movie.stop()
            self.setIcon(QtGui.QIcon())
            self.setDisabled(False)
            self.setText("revert")

    def setGif(self):
        if not hasattr(self, "_movie"):
            self._movie = QtGui.QMovie(self)
            self._movie.setFileName(":resources/images/loading.gif")
            self._movie.frameChanged.connect(self.on_frameChanged)
            if self._movie.loopCount() != -1:
                self._movie.finished.connect(self.start)
        self.stop()

    @QtCore.pyqtSlot(int)
    def on_frameChanged(self, frame_number):
        self.setIcon(QtGui.QIcon(self._movie.currentPixmap()))
