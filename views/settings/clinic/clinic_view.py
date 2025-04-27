import asyncio
import datetime
import mimetypes
import os
import time

from PyQt6.QtWidgets import QSizePolicy, QFileDialog, QMessageBox
from PyQt6.QtCore import Qt, QSize, QTime, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QButtonGroup, QLabel, QStackedWidget
from qasync import asyncSlot

from services.supabase.controllers.clinic.clinic_controller import ClinicController
from services.supabase.controllers.image.image_controller import ImageController
from utils.utlis import extract_file_extension, validate_file_size
from utils.validator import phone_number_validator, email_validator
from views.componenets.customsComponents.dates_and_times.custom_range_time_picker import CustomRangeTimePicker
from signals import SignalRepositorySingleton
from views.componenets.customsComponents.buttons.button_with_loader import ButtonWithLoader
from views.componenets.customsComponents.circular_avatar import mask_image
from views.componenets.customsComponents.custom_line_edit_with_icon import CustomLineEditWithIcon
from views.componenets.customsComponents.custom_rounded_line_edit import CustomRoundedLineEdit
from views.componenets.customsComponents.custom_scroll_area import CustomScrollArea
from views.componenets.customsComponents.flow_layout import FlowLayout
from views.componenets.customsComponents.table.form_componenets.custom_label import CustomLabel
from views.componenets.customsComponents.table.form_componenets.custom_text_edit import CustomTextEdit


class ClinicView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Signals
        self.form_widget = None
        self.data = None

        self.signals = SignalRepositorySingleton.instance()

        self.clinic_controller = ClinicController()
        self.image_controller = ImageController()

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.setLayout(self.layout)
        asyncio.create_task(self.get_initial_data())

    async def get_initial_data(self):
        self.signals.globalCreateLoadingNotificationSignal.emit("GET_CLINIC_DATA")

        self.data = await self.clinic_controller.get_data()
        if self.data and self.data["logo_image_path"]:
            logo_file = await self.image_controller.get_image_from_storage(self.data["logo_image_path"])
            if logo_file:
                self.data["logo_image_data"] = logo_file

        self.setup_table_ui()
        self.signals.globalLoadingNotificationControllerSignal.emit("GET_CLINIC_DATA")

    def setup_table_ui(self):
        self.form_widget = self.FormWidget(self.data, self.clinic_controller, image_controller=self.image_controller)

        main_vertical_layout = QVBoxLayout()
        main_vertical_layout.setContentsMargins(0, 0, 0, 0)
        main_vertical_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        main_vertical_layout.addWidget(self.form_widget)

        central_widget = QWidget()
        central_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        central_widget.setStyleSheet("""
            QWidget {
                background-color:#F9FBFC;
            }
            QLabel {
                border:0;
            }
        """)
        central_widget.setMinimumHeight(800)

        central_widget.setLayout(main_vertical_layout)

        scroll_area = CustomScrollArea(self)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setWidget(central_widget)
        scroll_area.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.MinimumExpanding)

        self.layout.addWidget(scroll_area)

    class FormWidget(QWidget):
        def __init__(self, data, clinic_controller, image_controller, parent=None):
            super().__init__(parent)

            # Signals
            self.signals = SignalRepositorySingleton.instance()

            self.clinic_controller = clinic_controller
            self.image_controller = image_controller

            self.data = data

            self.clinic_settings_header_widget = self.ClinicSettingsHeader(parent=self)
            self.clinic_settings_header_widget.save_btn.clicked.connect(self.update_clinic)

            self.logo_section_widget = self.LogoSection(data)

            self.clinic_information_widget = self.ClinicInformationWidget(data=self.data, parent=self)

            self.contact_person_widget = self.ContactPersonWidget(data=self.data, parent=self)

            central_widget = QWidget()
            central_widget.setObjectName("clinic_form_widget")
            central_widget.setStyleSheet("""
            QWidget#clinic_form_widget {
                border:1px solid #E0E4EA;
                border-radius:5px;
                background-color:white;
            }
            """)

            main_v_layout = QVBoxLayout(central_widget)
            main_v_layout.setContentsMargins(0, 0, 0, 0)
            main_v_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
            main_v_layout.setSpacing(32)

            main_v_layout.addWidget(self.clinic_settings_header_widget)
            main_v_layout.addWidget(self.logo_section_widget)
            main_v_layout.addWidget(self.clinic_information_widget)
            main_v_layout.addWidget(self.contact_person_widget)

            layout = QVBoxLayout()
            layout.setContentsMargins(65, 65, 65, 65)
            layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
            layout.addWidget(central_widget)

            self.setLayout(layout)

        @asyncSlot()
        async def update_clinic(self):
            if self.validate_data():
                self.clinic_settings_header_widget.save_btn.start()

                data = {
                    "name": self.clinic_information_widget.name_input.input.text(),
                    "address": self.clinic_information_widget.address_input.input.text(),
                    "phone_number": self.clinic_information_widget.phone_number_input.input.line_edit.text(),
                    "email": self.clinic_information_widget.email_input.input.line_edit.text(),
                    "website": self.clinic_information_widget.website_input.input.line_edit.text(),
                    "fax_number": self.clinic_information_widget.fax_number_input.input.text(),
                    "contact_person": self.contact_person_widget.name_input.input.line_edit.text(),
                    "contact_person_phone": self.contact_person_widget.phone_number_input.input.line_edit.text(),
                    "contact_person_email": self.contact_person_widget.email_input.input.line_edit.text(),
                    "services_offered": self.clinic_information_widget.services_offered_widget.services_offered_input.toPlainText(),
                    "clinic_hours": self.clinic_information_widget.clinic_days_widget.get_days_and_time_slots_data(),
                    "registration_number": self.clinic_information_widget.registration_number_input.input.text(),
                    "latitude": self.clinic_information_widget.latitude_input.input.line_edit.text(),
                    "longitude": self.clinic_information_widget.longitude_input.input.line_edit.text(),
                    "updated_at": datetime.datetime.now().isoformat()
                }

                # Upload Image To Storage
                logo_data = self.logo_section_widget.logo_data
                if logo_data["file_path"] and not logo_data["is_placeholder"]:
                    if self.data["logo_image_path"] != logo_data["file_path"]:
                        res = await self.image_controller.upload_image_to_storage(
                            logo_data["file_path"], logo_data["file"], logo_data["mime_type"]
                        )
                        if not res:
                            self._show_error_message('Could not upload image',
                                                     'Error occurred while uploading image to storage, please contact your service provider.')
                            return
                        data["logo_image_path"] = logo_data["file_path"]

                # Update clinic data
                res = await self.clinic_controller.update_clinic(data)
                if not res:
                    self._show_error_message('Could not update clinic',
                                             'Error occurred while updating clinic, please contact your service provider.')
                else:
                    self.signals.globalCreateMessageNotificationSignal.emit({
                        "message_type": "success",
                        "message": "Clinic Successfully Updated.",
                        "duration": 2000,
                    })

            self.clinic_settings_header_widget.save_btn.stop()

        def _show_error_message(self, text, detailed_text):
            self.clinic_settings_header_widget.save_btn.stop()
            msg = QMessageBox()
            msg.setText(text)
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setDetailedText(detailed_text)
            msg.exec()

        def validate_data(self):
            name = self.clinic_information_widget.name_input.input.text()
            address = self.clinic_information_widget.address_input.input.text()

            if not name or name[0] == " ":
                QMessageBox.warning(self, "Error", "Name is required.")
                return

            if not address or address[0] == " ":
                QMessageBox.warning(self, "Error", "Address is required.")
                return

            return True

        class ClinicSettingsHeader(QWidget):
            def __init__(self, parent=None):
                super().__init__(parent)

                clinic_settings_label = QLabel("Clinic Settings")
                clinic_settings_label.setStyleSheet("color:#22282B;")

                clinic_settings_label_font = clinic_settings_label.font()
                clinic_settings_label_font.setWeight(clinic_settings_label_font.Weight.Medium)
                clinic_settings_label_font.setPointSize(16)

                clinic_settings_label.setFont(clinic_settings_label_font)

                clinic_settings_description_label = QLabel("You can edit your clinic information here")
                clinic_settings_description_label.setStyleSheet("""
                         color:#87959E;
                         border:0;
                     """)

                clinic_settings_description_label_font = clinic_settings_description_label.font()
                clinic_settings_description_label_font.setWeight(clinic_settings_description_label_font.Weight.Normal)
                clinic_settings_description_label_font.setPointSize(12)
                clinic_settings_description_label.setFont(clinic_settings_description_label_font)

                wrapper_widget = QWidget()
                wrapper_widget.setObjectName("clinic_settings_header")
                wrapper_widget.setStyleSheet("""
                QWidget#clinic_settings_header {
                    border:0;border-bottom:1px solid #E1E5EB;
                    background-color:transparent;
                }
                QLabel {
                    border:0;
                    background-color:transparent;
                }
                
                """)

                clinic_settings_labels_layout = QVBoxLayout()
                clinic_settings_labels_layout.setSpacing(10)

                clinic_settings_labels_layout.addWidget(clinic_settings_label)
                clinic_settings_labels_layout.addWidget(clinic_settings_description_label)

                self.save_btn = ButtonWithLoader(text="Save", size=QSize(100, 45))
                self.save_btn.setStyleSheet("""
                    QPushButton {
                        border:0;
                        border-radius:5px;
                        font-size:13pt;
                        background-color:#7ED321;
                        color:white;
                        font-weight:bold;
                    }
                    QPushButton:pressed {
                        border:0;
                        border-radius:3px;
                        color:#F5F5F5;
                        padding-top: 2px;
                        padding-left: 2px;
                    }
                """)

                main_h_layout = QHBoxLayout(wrapper_widget)
                main_h_layout.setContentsMargins(40, 30, 40, 30)
                main_h_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

                main_h_layout.addLayout(clinic_settings_labels_layout, Qt.AlignmentFlag.AlignLeft)
                main_h_layout.addWidget(self.save_btn, Qt.AlignmentFlag.AlignRight)

                layout = QVBoxLayout()
                layout.setContentsMargins(0, 0, 0, 0)
                layout.setSpacing(0)

                layout.addWidget(wrapper_widget)

                self.setLayout(layout)

        class LogoSection(QWidget):
            def __init__(self, data, parent=None):
                super().__init__(parent)

                self.data = data
                if not self.data or not self.data.get("logo_image_path"):

                    self.logo_data = {'file_path': None,
                                      'image_type': "jpg",
                                      "file": None,
                                      "mime_type": 'jpg',
                                      "is_placeholder": True,
                                      }
                else:
                    mime_type, _ = mimetypes.guess_type(self.data["logo_image_path"])
                    file_extension = extract_file_extension(self.data["logo_image_path"])

                    self.logo_data = {'file_path': self.data["logo_image_path"],
                                      'image_type': file_extension,
                                      "file": self.data["logo_image_data"],
                                      "mime_type": mime_type,
                                      "is_placeholder": False,
                                      }

                pixmap = mask_image(self.logo_data["file"], img_type=self.logo_data["image_type"].replace(".", ""),
                                    border=True, border_color="#E9E9E9")

                self.logo = QLabel()
                self.logo.setFixedWidth(64)
                self.logo.setPixmap(pixmap)

                change_avatar_label = QLabel("Change Avatar")
                change_avatar_label.setStyleSheet("color:#22282B;")

                change_avatar_label_font = change_avatar_label.font()
                change_avatar_label_font.setWeight(change_avatar_label_font.Weight.Normal)
                change_avatar_label_font.setPointSize(14)

                change_avatar_label.setFont(change_avatar_label_font)

                change_avatar_description_label = QLabel("Supported avatar format is png, or jpg")
                change_avatar_description_label.setStyleSheet("""
                          color:#87959E;
                          border:0;
                      """)

                change_avatar_description_label_font = change_avatar_description_label.font()
                change_avatar_description_label_font.setWeight(change_avatar_description_label_font.Weight.Normal)
                change_avatar_description_label_font.setPointSize(12)
                change_avatar_description_label.setFont(change_avatar_description_label_font)

                wrapper_widget = QWidget()
                wrapper_widget.setObjectName("logo_section")
                wrapper_widget.setStyleSheet("""
                 QWidget#logo_section {
                     border:0;border-bottom:1px solid #E1E5EB;
                     background-color:transparent;
                 }
                 QLabel {
                     border:0;
                     background-color:transparent;
                 }

                 """)

                change_avatar_labels_layout = QVBoxLayout()
                change_avatar_labels_layout.setSpacing(10)

                change_avatar_labels_layout.addWidget(change_avatar_label)
                change_avatar_labels_layout.addWidget(change_avatar_description_label)

                self.upload_btn = ButtonWithLoader(text="Upload", size=QSize(100, 45))
                self.upload_btn.clicked.connect(self.open_dialog)
                self.upload_btn.setStyleSheet("""
                     QPushButton {
                         border:1px solid #D1D7DF;
                         border-radius:5px;
                         font-size:12pt;
                         background-color:transparent;
                         color:#85939D;
                         font-weight:500;
                     }
                     QPushButton:pressed {
                         border:0;
                         border-radius:3px;
                         padding-top: 2px;
                         padding-left: 2px;
                     }
                 """)

                main_h_layout = QHBoxLayout(wrapper_widget)
                main_h_layout.setSpacing(30)
                main_h_layout.setContentsMargins(20, 20, 20, 20)
                main_h_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

                main_h_layout.addWidget(self.logo)
                main_h_layout.addLayout(change_avatar_labels_layout)
                main_h_layout.addWidget(self.upload_btn, 0)

                layout = QVBoxLayout()
                layout.setContentsMargins(20, 0, 20, 0)
                layout.setSpacing(0)

                layout.addWidget(wrapper_widget)

                self.setLayout(layout)

            def set_logo_data(self, data):
                self.logo_data = data

            @pyqtSlot()
            def open_dialog(self):
                fname, _ = QFileDialog.getOpenFileName(
                    self,
                    "Open File",
                    "/home",
                    "Images (*.png *.jpg)")

                if fname and self.validate_file(file_name=fname):
                    self.upload_btn.start()
                    self.loadImage(file_name=fname)

            def loadImage(self, file_name):
                file_extension = extract_file_extension(file_name)
                file_data = open(file_name, 'rb').read()
                mime_type, _ = mimetypes.guess_type(file_name)

                updated_file_path = ("images/" + datetime.datetime.today().strftime("%Y") + "/"
                                     + datetime.datetime.today().strftime("%m") + "/"
                                     + datetime.datetime.today().strftime("%d") + "/" +
                                     str(time.time()) + f"{file_extension}")

                self.set_logo_data({
                    "file_path": updated_file_path,
                    "image_type": file_extension,
                    "file": file_data,
                    "mime_type": mime_type,
                    "is_placeholder": False
                })

                pixmap = mask_image(file_data, img_type=file_extension, border=True, border_color="#E9E9E9")
                self.logo.setPixmap(pixmap)
                self.logo.update()
                self.upload_btn.stop()

            def validate_file(self, file_name):
                allowed_format = [".jpg", ".png", ".dicom"]
                allowed_mime_type = ["image/jpeg", "image/png", "image/dicom"]
                file_extension = extract_file_extension(file_name)
                mime_type, _ = mimetypes.guess_type(file_name)

                if file_extension not in allowed_format:
                    QMessageBox.critical(self, "Error", "Allowed file format: jpg, png,dicom")
                    return

                if not validate_file_size(file_name):
                    QMessageBox.critical(self, "Error", "Maximum Allowed file size :10MB")
                    return

                if mime_type not in allowed_mime_type:
                    QMessageBox.critical(self, "Error", "Unsupported Image Mime Type")
                    return

                return True

        class ClinicInformationWidget(QWidget):
            def __init__(self, data, parent=None):
                super().__init__(parent)

                self.data = data


                self.name_input = LabelAndInputWithIconWidget(name="Name", minimal_w=300)

                self.email_input = LabelAndInputWithIconWidget(name="Email Address", minimal_w=300,
                                                               icon_path=":/resources/icons/fill_email.svg")
                self.email_input.input.line_edit.setValidator(email_validator)

                self.phone_number_input = LabelAndInputWithIconWidget(name="Phone Number", minimal_w=300,
                                                                      icon_path=":/resources/icons/dial.svg")
                self.phone_number_input.input.line_edit.setValidator(phone_number_validator)
                self.address_input = LabelAndInputWithIconWidget(name="Address", minimal_w=300)

                self.longitude_input = LabelAndInputWithIconWidget(name="Longitude", minimal_w=300,
                                                                   icon_path=":/resources/icons/location.svg")
                self.latitude_input = LabelAndInputWithIconWidget(name="Latitude", minimal_w=300,
                                                                  icon_path=":/resources/icons/location.svg")
                self.website_input = LabelAndInputWithIconWidget(name="Website", minimal_w=300,
                                                                 icon_path=":/resources/icons/website.svg")
                self.fax_number_input = LabelAndInputWithIconWidget(name="Fax Number", minimal_w=300)

                self.registration_number_input = LabelAndInputWithIconWidget(name="Registration Number",
                                                                             minimal_w=300)

                self.services_offered_widget = ServiceOfferedWidget()

                information_flow_layout = FlowLayout(h_spacing=50, v_spacing=50)
                information_flow_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

                information_flow_layout.addWidget(self.name_input)
                information_flow_layout.addWidget(self.email_input)
                information_flow_layout.addWidget(self.phone_number_input)
                information_flow_layout.addWidget(self.address_input)
                information_flow_layout.addWidget(self.longitude_input)
                information_flow_layout.addWidget(self.latitude_input)
                information_flow_layout.addWidget(self.website_input)
                information_flow_layout.addWidget(self.fax_number_input)
                information_flow_layout.addWidget(self.registration_number_input)
                # information_flow_layout.addWidget(self.services_offered_widget)

                self.clinic_days_widget = self.AvailableDaysWidget(data)

                wrapper_widget = QWidget()
                wrapper_widget.setObjectName("clinic_information_widget")
                wrapper_widget.setStyleSheet("""
                          QWidget#clinic_information_widget {
                              border:0;border-bottom:1px solid #E1E5EB;
                              background-color:transparent;
                          }
                          QLabel {
                              border:0;
                              background-color:transparent;
                          }

                          """)
                wrapper_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

                main_v_layout = QVBoxLayout(wrapper_widget)
                main_v_layout.setSpacing(30)
                main_v_layout.setContentsMargins(20, 0, 20, 20)
                main_v_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

                main_v_layout.addLayout(information_flow_layout)
                main_v_layout.addWidget(self.services_offered_widget)
                main_v_layout.addWidget(self.clinic_days_widget, 0)

                layout = QVBoxLayout()
                layout.setAlignment(Qt.AlignmentFlag.AlignTop)
                layout.setContentsMargins(20, 20, 20, 20)
                layout.setSpacing(0)

                layout.addWidget(wrapper_widget, 0)

                self.setLayout(layout)

                self.set_data()

            def set_data(self):
                if self.data:
                    self.name_input.input.setText(self.data["name"])
                    self.email_input.input.line_edit.setText(self.data["email"])
                    self.phone_number_input.input.line_edit.setText(self.data["phone_number"])
                    self.address_input.input.setText(self.data["address"])

                    self.longitude_input.input.line_edit.setText(str(self.data["longitude"]))
                    self.latitude_input.input.line_edit.setText(str(self.data["latitude"]))
                    self.website_input.input.line_edit.setText(self.data["website"])
                    self.fax_number_input.input.setText(self.data["fax_number"])

                    self.registration_number_input.input.setText(self.data["registration_number"])
                    self.services_offered_widget.services_offered_input.setText(self.data["services_offered"])

            class AvailableDaysWidget(QWidget):
                def __init__(self, data, parent=None):
                    super().__init__(parent)

                    self.data = data

                    self.available_days_data = []
                    self.available_days_buttons = []
                    self.days_views = {}

                    self.days = [
                        {
                            "name": "Sunday",
                            "id": 1,
                            "is_active": False,
                        },
                        {
                            "name": "Monday",
                            "id": 2,
                            "is_active": False,

                        },
                        {
                            "name": "Tuesday",
                            "id": 3,
                            "is_active": False,

                        },
                        {
                            "name": "Wednesday",
                            "id": 4,

                            "is_active": False,

                        },
                        {
                            "name": "Thursday",
                            "id": 5,

                            "is_active": False,

                        },
                        {
                            "name": "Friday",
                            "id": 6,
                            "is_active": False,

                        },
                        {
                            "name": "Saturday",
                            "id": 7,
                            "is_active": False,

                        },
                    ]

                    self.days_buttons_group = QButtonGroup()

                    self.days_buttons_group.buttonClicked.connect(self.change_day_button_style)

                    days_layout = self.create_days_layout()
                    self.stacked_widget = self.create_stacked_widget()

                    # Set first Day
                    self.set_main_content("Sunday")
                    self.change_day_button_style(self.available_days_buttons[0])

                    layout = QVBoxLayout()
                    layout.setContentsMargins(0, 20, 0, 20)
                    layout.setAlignment(Qt.AlignmentFlag.AlignTop)
                    layout.setSpacing(20)

                    layout.addLayout(days_layout)
                    layout.addWidget(self.stacked_widget)

                    self.setLayout(layout)
                    self.setStyleSheet("background-color:white;")

                def create_days_layout(self):

                    clinic_days_label = CustomLabel("Clinic Days")
                    clinic_days_label.setFixedSize(QSize(150, 30))

                    font = clinic_days_label.font()
                    font.setPointSize(14)
                    font.setWeight(QFont.Weight.Medium)
                    clinic_days_label.setFont(font)

                    clinic_label_and_days_layout = QVBoxLayout()
                    clinic_label_and_days_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
                    clinic_label_and_days_layout.setSpacing(20)

                    clinic_label_and_days_layout.addWidget(clinic_days_label)

                    days_layout = QHBoxLayout()
                    days_layout.setSpacing(20)

                    for day in self.days:
                        button = QPushButton(day["name"][:3])
                        button.setFixedHeight(50)
                        self.configure_button(button, day)
                        self.days_buttons_group.addButton(button, day["id"])
                        self.available_days_buttons.append(button)
                        days_layout.addWidget(button)

                    clinic_label_and_days_layout.addLayout(days_layout)
                    return clinic_label_and_days_layout

                def configure_button(self, button, day):
                    button.setCheckable(True)
                    button.setFixedSize(QSize(50, 50))
                    self.apply_default_style(button)

                    button.setObjectName(day["name"])

                    button_id = day["id"]
                    button.setProperty("id", button_id)
                    button.setProperty("is_active", False)
                    if self.data and self.data.get("clinic_hours"):
                        for clinic_hour in self.data["clinic_hours"]:
                            if day["name"] == clinic_hour["day"]:
                                self.apply_active_button_style(button)

                    button.clicked.connect(lambda _, b=button.objectName(): self.set_main_content(b))

                def create_stacked_widget(self):
                    stack_widget = QStackedWidget()

                    for day in self.days:
                        day_view = self.TimeSlotsSelectionWidget(day["name"])
                        stack_widget.addWidget(day_view)
                        self.days_views[day["name"]] = day_view

                        day_button = self.days_buttons_group.button(day["id"])
                        day_view.dayActivatedSignal.connect(self.connect_day_activated_signal(day_button))
                        day_view.dayDisActivatingSignal.connect(self.connect_day_dis_activating_signal(day_button))
                        if self.data and self.data.get("clinic_hours"):
                            for clinic_hour in self.data["clinic_hours"]:
                                if day["name"] == clinic_hour["day"]:
                                    day_view.time_picker.from_time_picker.setTime(
                                        QTime.fromString(clinic_hour["start_time"]))
                                    day_view.time_picker.to_time_picker.setTime(
                                        QTime.fromString(clinic_hour["end_time"]))

                    return stack_widget

                def change_day_button_style(self, button):
                    if button.property("is_active"):
                        self.apply_active_and_focused_button_style(button)
                    else:
                        self.apply_focus_button_style(button)

                    for btn in self.days_buttons_group.buttons():
                        if btn != button:
                            if btn.property("is_active"):
                                self.apply_active_button_style(btn)
                            else:
                                self.apply_default_style(btn)

                def set_main_content(self, day):
                    widget = self.days_views.get(day)
                    if widget:
                        self.stacked_widget.setCurrentWidget(widget)

                def get_days_and_time_slots_data(self):
                    available_days_data = []
                    days_stack_widget = self.stacked_widget
                    for i in range(days_stack_widget.count()):
                        day_widget = days_stack_widget.widget(i)
                        if day_widget and day_widget.day_data["start_time"] and day_widget.day_data["end_time"]:
                            available_days_data.append(day_widget.day_data)

                    return available_days_data

                class TimeSlotsSelectionWidget(QWidget):
                    dayActivatedSignal = pyqtSignal(str)
                    dayDisActivatingSignal = pyqtSignal(str)

                    def __init__(self, day, parent=None):
                        super().__init__(parent)

                        # Signals
                        self.signals = SignalRepositorySingleton.instance()

                        self.generated_time_slots = None
                        self.day = day

                        self.day_data = {
                            "day": self.day,
                            "start_time": QTime(),
                            "end_time": QTime(),
                        }
                        self.setObjectName(self.day)

                        day_label = CustomLabel(day)

                        font = day_label.font()
                        font.setPointSize(13)
                        font.setWeight(QFont.Weight.Normal)
                        day_label.setFont(font)

                        day_label.setFixedSize(150, 30)

                        self.time_picker = CustomRangeTimePicker()
                        self.time_picker.from_time_picker.timeChanged.connect(self.handle_time_picker_changed)
                        self.time_picker.to_time_picker.timeChanged.connect(self.handle_time_picker_changed)

                        self.layout = QHBoxLayout()
                        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
                        self.layout.setContentsMargins(0, 20, 0, 20)
                        self.layout.setSpacing(30)

                        self.layout.addWidget(day_label)
                        self.layout.addWidget(self.time_picker)

                        self.setStyleSheet("""
                        QWidget {
                            background-color:white;
                        }
                        QLabel {
                            background-color:transparent;
                        }
                        """)

                        self.setLayout(self.layout)

                    def get_day_data(self):
                        self.day_data["start_time"] = QTime(
                            self.time_picker.from_time_picker.time().toPyTime()).toString()
                        self.day_data["end_time"] = QTime(self.time_picker.to_time_picker.time().toPyTime()).toString()
                        return self.day_data

                    def set_day_data(self):
                        self.day_data["start_time"] = QTime(
                            self.time_picker.from_time_picker.time().toPyTime()).toString()
                        self.day_data["end_time"] = QTime(self.time_picker.to_time_picker.time().toPyTime()).toString()

                    @pyqtSlot(QTime)
                    def handle_time_picker_changed(self, time):
                        start_time_slot = self.time_picker.from_time_picker.time()
                        end_time_slot = self.time_picker.to_time_picker.time()
                        self.set_day_data()

                        if start_time_slot == QTime(0, 0) and end_time_slot == QTime(0, 0):
                            self.dayDisActivatingSignal.emit(self.day)
                            return

                        if start_time_slot == end_time_slot:
                            self.dayDisActivatingSignal.emit(self.day)
                            return

                        if start_time_slot > end_time_slot:
                            self.dayDisActivatingSignal.emit(self.day)
                            return

                        self.dayActivatedSignal.emit(self.day)

                def connect_day_dis_activating_signal(self, day_button: QPushButton):
                    return lambda: self.apply_day_dis_activate_logic(day_button)

                def apply_day_dis_activate_logic(self, day_button):
                    day_button.setProperty("is_active", False)
                    self.apply_focus_button_style(day_button)

                def apply_day_activated_logic(self, day_button):
                    day_button.setProperty("is_active", True)
                    self.apply_active_and_focused_button_style(day_button)

                def connect_day_activated_signal(self, day_button: QPushButton):
                    return lambda: self.apply_day_activated_logic(day_button)

                @staticmethod
                def apply_default_style(button: QPushButton):
                    button.setStyleSheet("""
                            QPushButton {
                                border:1px solid #E0E4EA;
                                border-radius:25px;
                                background-color:#F6F8FA;
                                color:#4B4E58;
                            }
                            """)
                    button.setProperty("is_active", False)

                @staticmethod
                def apply_focus_button_style(button: QPushButton):
                    button.setStyleSheet("""
                            QPushButton {
                                border:1px solid #d97706;
                                border-radius:24px;
                                background-color:transparent;
                                color:#4B4E58;
                            }
                            """)

                @staticmethod
                def apply_active_button_style(button: QPushButton):
                    font = button.font()
                    font.setPointSize(13)
                    font.setWeight(QFont.Weight.Medium)
                    button.setFont(font)

                    button.setStyleSheet("""
                            QPushButton {
                                border:0;
                                border-radius:24px;
                                background-color:#fbbf24;
                                color:white;
                            }
                            """)
                    button.setProperty("is_active", True)

                @staticmethod
                def apply_active_and_focused_button_style(button: QPushButton):
                    font = button.font()
                    font.setPointSize(13)
                    font.setWeight(QFont.Weight.Medium)
                    button.setFont(font)

                    button.setStyleSheet("""
                            QPushButton {
                                border:1px solid #d97706;
                                border-radius:24px;
                                background-color:#fbbf24;
                                color:white;
                            }
                            """)

        class ContactPersonWidget(QWidget):
            def __init__(self, data, parent=None):
                super().__init__(parent)

                self.data = data

                font = QFont()
                font.setPointSize(16)
                font.setWeight(QFont.Weight.DemiBold)

                self.name_input = LabelAndInputWithIconWidget(name="Contact Person", minimal_w=300,
                                                              icon_path=":/resources/icons/filled_person.svg")

                self.email_input = LabelAndInputWithIconWidget(name="Contact Person Email Address", minimal_w=300,
                                                               icon_path=":/resources/icons/fill_email.svg")
                self.email_input.input.line_edit.setValidator(email_validator)
                self.phone_number_input = LabelAndInputWithIconWidget(name="Contact Person Phone Number", minimal_w=300,
                                                                      icon_path=":/resources/icons/dial.svg")
                self.phone_number_input.input.line_edit.setValidator(phone_number_validator)

                information_layout = QHBoxLayout()
                information_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

                information_layout.addWidget(self.name_input)
                information_layout.addWidget(self.phone_number_input)
                information_layout.addWidget(self.email_input)

                wrapper_widget = QWidget()
                wrapper_widget.setObjectName("contact_person_widget")
                wrapper_widget.setStyleSheet("""
                          QWidget#contact_person_widget {
                              border:0;;
                              background-color:transparent;
                          }
                          QLabel {
                              border:0;
                              background-color:transparent;
                          }

                          """)

                main_v_layout = QVBoxLayout(wrapper_widget)
                main_v_layout.setSpacing(30)
                main_v_layout.setContentsMargins(20, 0, 20, 20)
                main_v_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

                main_v_layout.addLayout(information_layout)

                layout = QVBoxLayout()
                layout.setAlignment(Qt.AlignmentFlag.AlignTop)
                layout.setContentsMargins(20, 0, 20, 50)

                layout.addWidget(wrapper_widget)

                self.setLayout(layout)
                self.set_data()

            def set_data(self):
                if self.data:
                    self.name_input.input.line_edit.setText(self.data["contact_person"])

                    self.email_input.input.line_edit.setText(self.data["contact_person_email"])
                    self.phone_number_input.input.line_edit.setText(self.data["contact_person_phone"])


class LabelAndInputWithIconWidget(QWidget):
    def __init__(self, name, minimal_w, icon_path=None, parent=None):
        super().__init__(parent)

        label = CustomLabel(name=name)

        if icon_path:
            self.input = CustomLineEditWithIcon(icon_path=icon_path, placeholder_text="")
        else:
            self.input = CustomRoundedLineEdit(placeholder_text="")

        self.input.setFixedHeight(40)

        self.input.setMinimumWidth(minimal_w)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        layout.addWidget(label)
        layout.addWidget(self.input)

        self.setLayout(layout)


class ServiceOfferedWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        services_offered_label = CustomLabel(name="Services Offered")

        self.services_offered_input = CustomTextEdit(border_radius=7, placeholder_text="")
        self.services_offered_input.setFixedWidth(300)
        self.services_offered_input.setFixedHeight(100)

        services_offered_layout = QVBoxLayout()
        services_offered_layout.setContentsMargins(0, 0, 0, 0)
        services_offered_layout.setSpacing(10)

        services_offered_layout.addWidget(services_offered_label)
        services_offered_layout.addWidget(self.services_offered_input)

        self.setLayout(services_offered_layout)
