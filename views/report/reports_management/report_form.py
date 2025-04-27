from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QStandardItem, QStandardItemModel, QFont
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QButtonGroup, QPushButton, QAbstractButton, QLabel, QStackedWidget, \
    QHBoxLayout
from qasync import asyncSlot

from services.supabase.controllers.report_workshop.template_controller import TemplateController
from signals import SignalRepositorySingleton
from views.componenets.customsComponents.custom_combobox import CustomComboBox
from views.componenets.customsComponents.custom_scroll_area import CustomScrollArea
from views.componenets.customsComponents.flow_layout import FlowLayout
from views.componenets.customsComponents.table.form_componenets.custom_label import CustomLabel


class ReportForm(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Signals
        self.rendered_templates = None
        self.rendered_templates_widget_wrapper = None
        self.signals = SignalRepositorySingleton.instance()

        self.parent = parent
        self.current_selected_template_name = None
        self.current_selected_referring_doctor_id = None

        self.template_controller = TemplateController()

        category_label = CustomLabel(name="Category")

        self.category_model = QStandardItemModel()

        self.category_combo = CustomComboBox(parent=self)
        self.category_combo.setFixedWidth(600)
        self.category_combo.currentIndexChanged.connect(self.on_categories_index_changed)

        self.category_combo.setModel(self.category_model)

        category_selection_data_vertical_layout = QVBoxLayout()
        category_selection_data_vertical_layout.setSpacing(10)

        category_selection_data_vertical_layout.addWidget(category_label)
        category_selection_data_vertical_layout.addWidget(self.category_combo)
        # ----------------------------------------------------------------------

        referring_doctor_label = CustomLabel(name="Referring Doctor")

        self.referring_doctor_model = QStandardItemModel()

        self.referring_doctor_combo = CustomComboBox(parent=self)
        self.referring_doctor_combo.currentIndexChanged.connect(self.on_referring_doctor_index_changed)
        self.referring_doctor_combo.setFixedWidth(600)

        self.referring_doctor_combo.setModel(self.referring_doctor_model)

        referring_doctor_selection_data_vertical_layout = QVBoxLayout()
        referring_doctor_selection_data_vertical_layout.setSpacing(10)

        referring_doctor_selection_data_vertical_layout.addWidget(referring_doctor_label)
        referring_doctor_selection_data_vertical_layout.addWidget(self.referring_doctor_combo)

        category_referring_doctor_layout = QHBoxLayout()
        category_referring_doctor_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        category_referring_doctor_layout.setContentsMargins(0, 0, 0, 0)
        category_referring_doctor_layout.setSpacing(20)

        category_referring_doctor_layout.addLayout(category_selection_data_vertical_layout)
        category_referring_doctor_layout.addLayout(referring_doctor_selection_data_vertical_layout)
        # ----------------------------------------------------------------------

        self.rendered_templates_stack_widget = QStackedWidget(self)

        self.templates_layout = QVBoxLayout()
        self.templates_layout.addWidget(self.rendered_templates_stack_widget)

        central_widget = QWidget()

        main_vertical_layout = QVBoxLayout(central_widget)
        main_vertical_layout.setSpacing(30)

        main_vertical_layout.addLayout(category_referring_doctor_layout)
        main_vertical_layout.addLayout(self.templates_layout)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout.setContentsMargins(30, 30, 30, 0)

        layout.addWidget(central_widget)

        self.setLayout(layout)

        self.populate_categories()

    def set_currently_selected_template_name(self, template_name):
        self.current_selected_template_name = template_name

    def get_current_selected_template_name(self):
        return self.current_selected_template_name

    def set_current_selected_referring_doctor_id(self, referring_doctor_id):
        self.current_selected_referring_doctor_id = referring_doctor_id

    def get_current_selected_referring_doctor_id(self):
        return self.current_selected_referring_doctor_id

    @pyqtSlot(int)
    @asyncSlot()
    async def populate_categories(self):
        categories = await self.parent.category_controller.get_all_categories()
        if categories:
            for item in categories:
                standard_item = QStandardItem()
                standard_item.setData(item["name"], Qt.ItemDataRole.DisplayRole)
                standard_item.setData(item["category_id"], Qt.ItemDataRole.UserRole)
                self.category_model.appendRow(standard_item)

    @pyqtSlot(int)
    @asyncSlot()
    async def populate_referring_doctor(self):
        self.referring_doctor_combo.clear()
        category = self.category_combo.currentText()
        if category:
            doctors = await self.parent.referring_doctor_controller.get_all_referring_doctors_by_category(category)
            if doctors:
                for item in doctors:
                    standard_item = QStandardItem()
                    name = item["first_name"] + " " + item["last_name"]
                    standard_item.setData(name, Qt.ItemDataRole.DisplayRole)
                    standard_item.setData(item["doctor_id"], Qt.ItemDataRole.UserRole)
                    self.referring_doctor_model.appendRow(standard_item)

        self.referring_doctor_model.appendRow(QStandardItem("None"))

    @pyqtSlot(int)
    def on_categories_index_changed(self, index):
        category = self.category_combo.currentText()
        self.get_report_form_widget_by_category(category)
        self.populate_referring_doctor()

    @pyqtSlot(int)
    def on_referring_doctor_index_changed(self, index):
        model_index = self.referring_doctor_model.index(index, 0)
        doctor_id = self.referring_doctor_model.data(model_index, Qt.ItemDataRole.UserRole)
        self.set_current_selected_referring_doctor_id(doctor_id)

    @pyqtSlot(str)
    @asyncSlot()
    async def get_report_form_widget_by_category(self, category):
        self.signals.reportHeaderInternalLoaderSignal.emit(True)
        templates = await self.template_controller.get_all_templates_by_category(category)
        self.refresh_rendered_templates(templates)
        self.signals.reportHeaderInternalLoaderSignal.emit(False)

    def render_templates(self, templates):
        if templates:
            self.rendered_templates_widget_wrapper = RenderedTemplatesWidgets()

            content_widget = QWidget()
            content_widget.setStyleSheet("border:0;")

            content_layout = QVBoxLayout(content_widget)
            content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
            content_layout.setContentsMargins(0, 0, 0, 0)
            content_layout.setSpacing(20)

            scroll_area = CustomScrollArea(self)
            scroll_area.setContentsMargins(10, 10, 10, 10)
            scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            scroll_area.setWidget(content_widget)

            buttons_layout = FlowLayout(h_spacing=30, v_spacing=30)
            buttons_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            for template in templates:
                template_btn = TemplateButton(name=template["name"])
                template_btn.setProperty("template_id", template["template_id"])

                buttons_layout.addWidget(template_btn)

                self.rendered_templates_widget_wrapper.templates_button_group.addButton(template_btn,
                                                                                        id=template["template_id"])

            self.rendered_templates_widget_wrapper.templates_button_group.buttonClicked.connect(
                self.change_template_btn_style)

            content_layout.addLayout(buttons_layout)
            self.rendered_templates_widget_wrapper.wrapper_layout.addWidget(scroll_area)
            return self.rendered_templates_widget_wrapper

        else:
            return QLabel()

    def refresh_rendered_templates(self, templates):
        newly_rendered_templates = self.render_templates(templates)

        if self.rendered_templates is not None:
            self.templates_layout.removeWidget(self.rendered_templates)
            self.rendered_templates.deleteLater()

        # Update the reference to the new widget
        self.rendered_templates = newly_rendered_templates

        # Insert the new widget at the correct position
        if self.rendered_templates:
            self.rendered_templates_stack_widget.addWidget(self.rendered_templates)
            self.rendered_templates_stack_widget.setCurrentWidget(self.rendered_templates)

    @pyqtSlot(QAbstractButton)
    def change_template_btn_style(self, button: QPushButton):
        # Update styles
        for btn in self.rendered_templates_stack_widget.currentWidget().templates_button_group.buttons():
            if btn == button:
                btn.setChecked(True)
                btn.style().unpolish(btn)
                btn.style().polish(btn)
                btn.setStyleSheet("""
                    border:0;
                    border-radius:7px;
                    color:white;
                    background-color:#2563EB;
                    font-weight:bold;
                    padding:20px;
                """)
                btn.update()
                btn.repaint()
                self.set_currently_selected_template_name(button.objectName())
            else:
                btn.style().unpolish(btn)
                btn.setStyleSheet("""
                    border:1px solid #D5D5D5;
                    border-radius:7px;
                    color:#2C2D33;
                    background-color:white;
                    padding:20px;
                """)
                btn.style().polish(btn)
                btn.update()
        self.parent.header_widget.next_btn.setEnabled(True)
        self.parent.header_widget.enable_button_style(self.parent.header_widget.next_btn)


class RenderedTemplatesWidgets(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        wrapper_widget = QWidget()
        wrapper_widget.setObjectName("rendered_templates_widgets")
        wrapper_widget.setStyleSheet("""
        QWidget#rendered_templates_widgets {
            border:0;
            background-color:white;
            border-radius:7px;
        }
        """)

        category_available_templates = QLabel("Category Available Templates")
        category_available_templates.setStyleSheet("background-color:transparent;border:0;color:black;")

        font = category_available_templates.font()
        font.setWeight(QFont.Weight.Medium)
        font.setPointSize(16)
        category_available_templates.setFont(font)

        self.templates_button_group = QButtonGroup()

        self.wrapper_layout = QVBoxLayout(wrapper_widget)
        self.wrapper_layout.setContentsMargins(30, 30, 10, 10)
        self.wrapper_layout.setSpacing(30)
        self.wrapper_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.wrapper_layout.addWidget(category_available_templates)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(wrapper_widget)

        self.setLayout(layout)
        self.setStyleSheet("background-color:transparent;")


class TemplateButton(QPushButton):
    def __init__(self, name, parent=None):
        super().__init__(parent)

        font = self.font()
        font.setPointSize(12)
        font.setWeight(font.Weight.Medium)
        self.setFont(font)

        self.setText(name)

        self.setStyleSheet("""
            border:1px solid #D5D5D5;
            border-radius:7px;
            color:#2C2D33;
            background-color:#FAFAFA;
            padding:20px;
        """)

        self.setObjectName(name)

        # self.setMinimumSize(200, 50)
