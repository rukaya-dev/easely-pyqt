from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QStandardItem, QStandardItemModel
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from qasync import asyncSlot

from services.supabase.controllers.report_workshop.category_controller import CategoryController
from services.supabase.controllers.report_workshop.option_controller import OptionController
from signals import SignalRepositorySingleton
from views.componenets.customsComponents.custom_combobox import CustomComboBox
from views.componenets.customsComponents.table.form_componenets.custom_input import CustomLineEdit
from views.componenets.customsComponents.table.form_componenets.custom_label import CustomLabel
from views.componenets.customsComponents.table.form_componenets.custom_text_edit import CustomTextEdit


class TemplateForm(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Signals
        self.signals = SignalRepositorySingleton.instance()

        self.parent = parent
        self.category_options = None

        self.options_controller = OptionController()
        self.category_controller = CategoryController()

        template_name_label = CustomLabel(name="Name")

        self.template_name_input = CustomLineEdit(placeholder_text="", parent=self)
        self.template_name_input.setText("Normal Abdominal Ultrasound")
        self.template_name_input.textChanged.connect(self.template_name_text_changed)

        template_name_vertical_layout = QVBoxLayout()
        template_name_vertical_layout.setSpacing(10)
        template_name_vertical_layout.addWidget(template_name_label)
        template_name_vertical_layout.addWidget(self.template_name_input)

        category_label = CustomLabel(name="Category")

        self.category_model = QStandardItemModel()

        self.category_combo = CustomComboBox(parent=self)
        self.category_combo.currentIndexChanged.connect(self.on_categories_index_changed)

        self.category_combo.setModel(self.category_model)

        category_selection_data_vertical_layout = QVBoxLayout()
        category_selection_data_vertical_layout.setSpacing(10)

        category_selection_data_vertical_layout.addWidget(category_label)
        category_selection_data_vertical_layout.addWidget(self.category_combo)

        desc_label = CustomLabel(name="Description")

        self.desc_input = CustomTextEdit(border_radius=2, placeholder_text="", parent=self)

        desc_vertical_layout = QVBoxLayout()
        desc_vertical_layout.setSpacing(10)

        desc_vertical_layout.addWidget(desc_label)
        desc_vertical_layout.addWidget(self.desc_input)

        central_widget = QWidget()

        main_vertical_layout = QVBoxLayout(central_widget)
        main_vertical_layout.setSpacing(30)

        main_vertical_layout.addLayout(template_name_vertical_layout)
        main_vertical_layout.addLayout(category_selection_data_vertical_layout)
        main_vertical_layout.addLayout(desc_vertical_layout)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout.setContentsMargins(30, 30, 30, 0)

        layout.addWidget(central_widget)

        self.setLayout(layout)

        self.setFixedSize(500, 600)

    def set_category_options(self, options):
        self.category_options = options

    def get_category_options(self):
        return self.category_options

    async def populate_categories(self):
        categories = await self.category_controller.get_all_categories()
        print(categories)
        if categories:
            for item in categories:
                standard_item = QStandardItem()
                standard_item.setData(item["name"], Qt.ItemDataRole.DisplayRole)
                standard_item.setData(item["category_id"], Qt.ItemDataRole.UserRole)
                self.category_model.appendRow(standard_item)

    @pyqtSlot(int)
    def on_categories_index_changed(self, index):
        category = self.category_combo.currentText()
        self.get_category_options_by_category(category)

    @pyqtSlot(str)
    @asyncSlot()
    async def get_category_options_by_category(self, category):
        self.signals.templateHeaderInternalLoaderSignal.emit(True)
        options = await self.options_controller.get_options_by_category(category)
        if options:
            self.set_category_options(options)
        else:
            self.set_category_options(None)
        self.signals.templateHeaderInternalLoaderSignal.emit(False)

    def template_name_text_changed(self):
        if len(self.template_name_input.text()) > 0:
            self.parent.header_widget.next_btn.setEnabled(True)
            self.parent.header_widget.enable_button_style(self.parent.header_widget.next_btn)
        else:
            self.parent.header_widget.next_btn.setEnabled(False)
            self.parent.header_widget.disable_button_style(self.parent.header_widget.next_btn)

        if not self.category_combo.currentText():
            self.parent.header_widget.disable_button_style(self.parent.header_widget.next_btn)


