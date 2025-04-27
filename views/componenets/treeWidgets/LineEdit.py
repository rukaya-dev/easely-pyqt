from PyQt6.QtCore import QRegularExpression, Qt
from PyQt6.QtGui import QRegularExpressionValidator
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QComboBox, QHBoxLayout, QLineEdit

from utils.utlis import random_color_generator
from utils.validator import normal_input_validator
from views.componenets.customsComponents.custom_checkbox import CustomCheckBox
from views.componenets.customsComponents.custom_combobox import CustomComboBox
from views.componenets.customsComponents.table.form_componenets.custom_input import CustomLineEdit
from views.componenets.customsComponents.table.form_componenets.custom_label import CustomLabel


class LineEditLayout(QWidget):
    def __init__(self, data=None, parent=None):
        super().__init__(parent)

        regex = QRegularExpression("[A-Za-z0-9_][A-Za-z0-9_ ,+={}()]*[A-Za-z0-9_]")

        validator = QRegularExpressionValidator(regex)
        self.parent = parent
        # Retrieve the base color from the palette
        self.data = data

        self.random_color = random_color_generator()
        line_edit_style_sheet = f"""
            QLineEdit {{
                border:1px solid {self.random_color};
                border-radius:2px;
                border-radius:2px;
                background-color:white;
                padding-left:5;
                padding-right:5px;
            }}
        """

        self.name_label = CustomLabel(name="Name")

        self.name_input = QLineEdit(self)
        self.name_input.setStyleSheet(line_edit_style_sheet)

        self.name_input.setValidator(validator)
        self.name_input.setObjectName("name")
        self.name_input.setFixedHeight(30)
        self.name_input.setFixedWidth(314)

        name_label_input_layout = QVBoxLayout()
        name_label_input_layout.setSpacing(10)
        name_label_input_layout.setContentsMargins(0, 0, 0, 0)
        name_label_input_layout.addWidget(self.name_label)
        name_label_input_layout.addWidget(self.name_input)
        # -----------------------------------------------------
        self.content = CustomLabel(name="Content")

        self.content_input = QLineEdit(self)
        self.content_input.setStyleSheet(line_edit_style_sheet)
        self.content_input.setObjectName("content")
        self.content_input.setFixedHeight(30)
        self.content_input.setFixedWidth(314)
        self.content_input.setValidator(validator)

        content_label_input_layout = QVBoxLayout()
        content_label_input_layout.setSpacing(10)
        content_label_input_layout.setContentsMargins(0, 0, 0, 0)

        content_label_input_layout.addWidget(self.content)
        content_label_input_layout.addWidget(self.content_input)
        # -----------------------------------------------------
        self.depends_on_label = CustomLabel(name="Depends On")

        self.depends_on_input = CustomComboBox(parent=self)
        self.depends_on_input.setStyleSheet(f"""
        QComboBox {{
            border:1px solid {self.random_color};
            border-radius:2px;
            background-color:white;
            color:black;
            padding-left:10px;
            padding-right:5px;
        }}
        QComboBox QAbstractItemView 
        {{
            min-width: 150px;
            color:black;
        }}
        QComboBox::drop-down {{
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 15px;
            border-left-width: 0px;
            padding-right:5px;
        }}
        QComboBox::down-arrow {{
            image: url(:resources/icons/expand_more.svg);
        }}
        
        QComboBox::down-arrow:on {{ /* shift the arrow when popup is open */
            top: 1px;
            left: 1px;
        }}
        """)

        self.depends_on_input.setFixedHeight(30)
        self.depends_on_input.setFixedWidth(314)

        depend_on_layout = QVBoxLayout()
        depend_on_layout.setSpacing(10)
        depend_on_layout.setContentsMargins(0, 0, 0, 0)

        depend_on_layout.addWidget(self.depends_on_label)
        depend_on_layout.addWidget(self.depends_on_input)

        # -----------------------------------------------------
        self.depends_on_input_label = CustomLabel(name="Depends on Value")

        self.depends_on_input_value = QLineEdit(self)
        self.depends_on_input_value.setStyleSheet(line_edit_style_sheet)

        self.depends_on_input_value.setFixedHeight(30)
        self.depends_on_input_value.setFixedWidth(314)

        depends_on_input_value_layout = QVBoxLayout()
        depends_on_input_value_layout.setSpacing(10)
        depends_on_input_value_layout.setContentsMargins(0, 0, 0, 0)

        depends_on_input_value_layout.addWidget(self.depends_on_input_label)
        depends_on_input_value_layout.addWidget(self.depends_on_input_value)

        depend_and_depends_on_value_layout = QHBoxLayout()
        depend_and_depends_on_value_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        depend_and_depends_on_value_layout.setSpacing(10)
        depend_and_depends_on_value_layout.setContentsMargins(0, 0, 0, 0)

        depend_and_depends_on_value_layout.addLayout(depend_on_layout)
        depend_and_depends_on_value_layout.addLayout(depends_on_input_value_layout)

        # -----------------------------------------------------
        self.place_holder_label = CustomLabel(name="Placeholder")

        self.place_holder_input = QLineEdit(self)
        self.place_holder_input.setStyleSheet(line_edit_style_sheet)

        self.place_holder_input.setValidator(normal_input_validator)
        self.place_holder_input.setFixedHeight(30)
        self.place_holder_input.setFixedWidth(314)

        place_holder_label_input_layout = QVBoxLayout()
        place_holder_label_input_layout.setSpacing(10)
        place_holder_label_input_layout.setContentsMargins(0, 0, 0, 0)

        place_holder_label_input_layout.addWidget(self.place_holder_label)
        place_holder_label_input_layout.addWidget(self.place_holder_input)
        # -----------------------------------------------------
        self.tool_tip_label = CustomLabel(name="Tooltip")

        self.tool_tip_input = QLineEdit(self)
        self.tool_tip_input.setStyleSheet(line_edit_style_sheet)
        self.tool_tip_input.setValidator(normal_input_validator)
        self.tool_tip_input.setFixedHeight(30)
        self.tool_tip_input.setFixedWidth(314)

        self.required = CustomCheckBox("Required", parent=self)
        self.required.setObjectName("required_check_box")
        self.required.setFixedHeight(30)

        tool_tip_label_input_layout = QVBoxLayout()

        tool_tip_label_input_layout.addWidget(self.tool_tip_label)
        tool_tip_label_input_layout.addWidget(self.tool_tip_input)
        # -------------------------------------------------------------

        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)

        main_layout.addLayout(name_label_input_layout)
        main_layout.addLayout(content_label_input_layout)
        main_layout.addLayout(place_holder_label_input_layout)
        main_layout.addLayout(tool_tip_label_input_layout)
        main_layout.addLayout(depend_and_depends_on_value_layout)
        main_layout.addWidget(self.required)

        self.setLayout(main_layout)

        self.setStyleSheet(line_edit_style_sheet)

        self.update_combobox()
        self.parent.currentItemIsChangedSignal.connect(self.update_combobox)

    def update_combobox(self):
        # Add new items
        if self.data:
            extract_array = self.extract_type_name_and_name(self.data)
            for i, item in enumerate(extract_array):
                # Clear existing items
                get_combo = self.find_child(item['depends_on_dropdown_id'])
                if get_combo is not None:
                    get_combo.clear()
                    for extracted_item in extract_array:
                        get_combo.addItem(str(extracted_item["type_name"] + "--" + extracted_item['name']))

                    if len(extract_array) > 0:
                        get_combo.setCurrentText(item["trigger_id"])

    def extract_type_name_and_name(self, items):
        if items:
            result = []
            def process_items(data):
                for item in data:
                    type_name = item.get('type_name', '')
                    name = item.get('name', '')
                    uuid = item.get('uuid', '')
                    depends_on_dropdown_id = item.get('depends_on_dropdown_id', '')
                    depends_on = item.get('depends_on', '')

                    # Add the tuple to the result list
                    result.append({
                        "type_name": type_name,
                        "name": name,
                        "uuid": uuid,
                        "depends_on_dropdown_id": depends_on_dropdown_id,
                        "trigger_id": depends_on["trigger_id"]
                    })

                    # Process children if they exist
                    if 'children' in item and isinstance(item['children'], list):
                        process_items(item['children'])

            process_items(items)
            return result

    def find_child(self, name):
        for child in self.parent.findChildren(QComboBox):
            if child.objectName() == name:
                return child
        return None

    def setData(self, new_data):
        self.data = new_data
        self.update_combobox()
