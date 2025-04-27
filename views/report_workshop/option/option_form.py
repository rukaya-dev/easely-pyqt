from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItem, QStandardItemModel
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QFrame, QHBoxLayout

from views.componenets.customsComponents.custom_combobox import CustomComboBox
from views.componenets.customsComponents.custom_scroll_area import CustomScrollArea
from views.componenets.customsComponents.table.form_componenets.custom_input import CustomLineEdit
from views.componenets.customsComponents.table.form_componenets.custom_label import CustomLabel
from views.componenets.customsComponents.table.form_componenets.custom_text_edit import CustomTextEdit
from views.report_workshop.option.option_tree_structure import OptionTreeStructure


class OptionForm(QWidget):
    def __init__(self,parent=None):
        super().__init__(parent)

        self.parent = parent

        option_name_label = CustomLabel(name="Name")

        self.option_name_input = CustomLineEdit(placeholder_text="", parent=self)
        self.option_name_input.setObjectName("option_name")

        option_name_vertical_layout = QVBoxLayout()
        option_name_vertical_layout.setSpacing(10)
        option_name_vertical_layout.addWidget(option_name_label)
        option_name_vertical_layout.addWidget(self.option_name_input)

        category_label = CustomLabel(name="Category")

        self.category_model = QStandardItemModel()

        self.category_combo = CustomComboBox(parent=self)
        self.category_combo.setMinimumWidth(400)

        self.category_combo.setModel(self.category_model)

        category_selection_data_vertical_layout = QVBoxLayout()
        category_selection_data_vertical_layout.setSpacing(10)

        category_selection_data_vertical_layout.addWidget(category_label)
        category_selection_data_vertical_layout.addWidget(self.category_combo)

        name_category_layout = QHBoxLayout()
        name_category_layout.setSpacing(20)
        name_category_layout.setContentsMargins(0, 0, 0, 0)

        name_category_layout.addLayout(option_name_vertical_layout)
        name_category_layout.addLayout(category_selection_data_vertical_layout)

        desc_label = CustomLabel(name="Description")

        self.desc_input = CustomTextEdit(border_radius=2, placeholder_text="", parent=self)
        self.desc_input.setMaximumHeight(100)

        desc_vertical_layout = QVBoxLayout()
        desc_vertical_layout.setSpacing(10)

        desc_vertical_layout.addWidget(desc_label, 0)
        desc_vertical_layout.addWidget(self.desc_input, 0)

        clinic_info_line_seperator = QFrame()
        clinic_info_line_seperator.setFrameShape(QFrame.Shape.HLine)
        clinic_info_line_seperator.setFrameShadow(QFrame.Shadow.Plain)
        clinic_info_line_seperator.setLineWidth(1)

        # Option Tree Structure
        self.treeWidget = OptionTreeStructure()

        central_widget = QWidget()

        main_vertical_layout = QVBoxLayout(central_widget)
        main_vertical_layout.setContentsMargins(0, 0, 30, 0)
        main_vertical_layout.setSpacing(32)

        main_vertical_layout.addLayout(name_category_layout)
        main_vertical_layout.addLayout(desc_vertical_layout)
        main_vertical_layout.addWidget(self.treeWidget)

        scroll_area = CustomScrollArea(self)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setWidget(central_widget)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout.setContentsMargins(30, 30, 3, 0)
        layout.addWidget(scroll_area)

        self.setLayout(layout)
        self.setStyleSheet("""
            QFrame {
                color:#dfdfdf;
            }
        """)

        self.setMinimumWidth(1000)
        self.populate_categories()

    def populate_categories(self):
        categories = self.parent.category_controller.store.get_data()
        if categories:
            for item in categories:
                standardItem = QStandardItem()
                standardItem.setData(item["name"], Qt.ItemDataRole.DisplayRole)
                standardItem.setData(item["category_id"], Qt.ItemDataRole.UserRole)
                self.category_model.appendRow(standardItem)
