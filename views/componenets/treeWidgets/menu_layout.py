from PyQt6.QtCore import QSize, Qt, pyqtSignal, QRegularExpression
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QFrame, QHBoxLayout, QPushButton, \
    QTreeWidgetItem, QTreeWidget, QSizePolicy

from views.componenets.customsComponents.table.form_componenets.custom_input import CustomLineEdit
from views.componenets.customsComponents.table.form_componenets.custom_label import CustomLabel
from views.componenets.treeWidgets.LineEdit import LineEditLayout
from PyQt6 import sip


class MenuLayout(QWidget):
    options_instance_counter = 2
    newOptionIsAdded = pyqtSignal(str, int)
    existingOptionIsRemoved = pyqtSignal(str, str)

    def __init__(self, parent_item: QTreeWidgetItem, tree: QTreeWidget, data=None, parent=None):
        super().__init__(parent)

        self.parent_item = parent_item
        self.parent_widget = parent
        self.tree = tree
        self.data = data

        size_policy = QSizePolicy()
        size_policy.setVerticalPolicy(QSizePolicy.Policy.Expanding)

        self.menu_header_layout = LineEditLayout(parent=self.parent_widget)
        self.menu_header_layout.name_input.setToolTip("Menu name")
        self.menu_header_layout.content_input.hide()
        self.menu_header_layout.content.hide()

        # Horizontal layout for line and '+' button
        self.line_layout = QHBoxLayout()
        self.line_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.line_layout.setSpacing(10)
        self.line_layout.setContentsMargins(15, 0, 0, 0)

        line = QFrame()
        line.setFixedWidth(610)
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)

        self.add_new_option_button = QPushButton()
        self.add_new_option_button.setFixedWidth(30)
        self.add_new_option_button.setIcon(QIcon(":/resources/icons/active_add.svg"))
        self.add_new_option_button.setIconSize(QSize(24, 24))  # Set the icon size here
        self.add_new_option_button.setStyleSheet("border:0;background-color:transparent")
        self.add_new_option_button.setToolTip("Create new option")
        self.add_new_option_button.clicked.connect(self.addNewOption)

        self.line_layout.addWidget(line, 1)
        self.line_layout.addWidget(self.add_new_option_button)

        self.option_1 = MenuOptionWidget(parent=self)
        self.option_1.option_label.setText(f"Option {1}")
        self.option_1.setObjectName(str(1))
        self.option_1.option_input.setObjectName(str(1))

        self.option_2 = MenuOptionWidget(parent=self)
        self.option_2.option_label.setText(f"Option {2}")
        self.option_2.setObjectName(str(2))
        self.option_2.option_input.setObjectName(str(2))

        self.options_widget = QWidget()
        self.options_widget.setStyleSheet("background-color:transparent;")

        self.options_layout = QVBoxLayout()
        self.options_layout.setSpacing(0)
        self.options_layout.setContentsMargins(0, 0, 0, 0)
        self.options_layout.setObjectName("options_layout")
        self.options_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.options_layout.addWidget(self.option_1)
        self.options_layout.addWidget(self.option_2)

        self.options_widget.setLayout(self.options_layout)

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        main_layout.addWidget(self.menu_header_layout)
        main_layout.addLayout(self.line_layout)
        main_layout.addWidget(self.options_widget, 1)

        self.setLayout(main_layout)

        self.setStyleSheet(f"""
        QLineEdit {{
            border:1px solid {self.menu_header_layout.random_color};
            padding-left:7px;
            border-radius:7px;
            }}
        QWidget#scroll_area_widget {{
            border:0;
        }}
        """)
        self.setSizePolicy(size_policy)

    def getData(self):
        return self.data

    def addNewOption(self):
        # Method to create and add a new QLineEdit
        self.options_instance_counter += 1
        new_option = MenuOptionWidget(parent=self)
        self.options_layout.addStretch(1)

        new_option.option_label.setText(f"Option {self.options_instance_counter}")
        new_option.setObjectName(str(self.options_instance_counter))
        new_option.option_input.setObjectName(str(self.options_instance_counter))
        new_option.option_actual_input.setObjectName("option_content")

        delete_btn = QPushButton()
        delete_btn.setIcon(QIcon(":/resources/icons/remove.svg"))
        delete_btn.setIconSize(QSize(16, 16))
        delete_btn.setStyleSheet("border:0;")
        delete_btn.setFixedWidth(30)

        h_layout = QHBoxLayout()
        h_layout.setContentsMargins(0, 0, 0, 0)
        h_layout.setSpacing(0)
        h_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        h_layout.addWidget(new_option)
        h_layout.addWidget(delete_btn)

        delete_btn.clicked.connect(lambda: self.removeLineEdit(h_layout, new_option.option_input.objectName()))

        self.options_layout.addLayout(h_layout)
        self.options_layout.invalidate()
        self.options_widget.updateGeometry()
        if self.tree is not None:
            if self.parent_item is not None:
                self.parent_item.setSizeHint(0, self.sizeHint() + QSize(0, 80))
                self.tree.scrollToItem(self.parent_item)
                self.tree.updateGeometries()
        parent_item_id = self.parent_item.data(0, Qt.ItemDataRole.UserRole)

        self.newOptionIsAdded.emit(parent_item_id, self.options_instance_counter)

    def generateMenuOption(self, option_id):
        new_option = MenuOptionWidget(parent=self)

        new_option.option_label.setText(f"Option {option_id}")
        new_option.setObjectName(str(option_id))
        new_option.option_input.setObjectName(str(option_id))

        delete_btn = QPushButton()
        delete_btn.setIcon(QIcon(":/resources/icons/remove.svg"))
        delete_btn.setIconSize(QSize(16, 16))
        delete_btn.setStyleSheet("border:0;")
        delete_btn.setFixedWidth(30)
        delete_btn.clicked.connect(lambda: self.removeLineEdit(h_layout, new_option.option_input.objectName()))

        h_layout = QHBoxLayout()
        h_layout.setContentsMargins(0, 0, 0, 0)
        h_layout.setSpacing(0)
        h_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        h_layout.addWidget(new_option)
        h_layout.addWidget(delete_btn)
        self.options_layout.addLayout(h_layout)
        self.options_layout.invalidate()
        self.options_widget.updateGeometry()
        if self.tree is not None:
            if self.parent_item is not None:
                self.parent_item.setSizeHint(0, self.sizeHint() + QSize(0, 80))
                self.tree.scrollToItem(self.parent_item)
                self.tree.updateGeometries()
        parent_item_id = self.parent_item.data(0, Qt.ItemDataRole.UserRole)

        self.newOptionIsAdded.emit(parent_item_id, option_id)

    def removeLineEdit(self, layout, widget_option_id=None):
        for i in reversed(range(layout.count())):
            widget = layout.itemAt(i).widget()
            if widget is not None:  # If it's a widget
                layout.removeWidget(widget)

        if layout is not None:
            # This will remove the layout from its parent layout (if it has one)
            sip.delete(layout)
            self.parent_item.setSizeHint(0, self.sizeHint() - QSize(0, 80))
            self.tree.updateGeometries()
            if self.options_instance_counter > 0:
                self.options_instance_counter -= 1
            self.updateGeometry()
        parent_item_id = self.parent_item.data(0, Qt.ItemDataRole.UserRole)
        self.existingOptionIsRemoved.emit(parent_item_id, widget_option_id)


class MenuOptionWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.parent = parent

        size = QSize(314, 30)

        self.option_label = CustomLabel(name="")

        self.option_input = CustomLineEdit(placeholder_text="", parent=self)
        self.option_input.setStyleSheet(f"""
        QLineEdit {{
            border:1px solid {self.parent.menu_header_layout.random_color};
            padding-left:7px;
            border-radius:2px;
            background-color:white;
            padding-left:10px;
            padding-right:5px;
            }}
        """)
        self.option_input.setFixedSize(size)

        self.name_label_input_layout = QVBoxLayout()
        self.name_label_input_layout.setContentsMargins(0, 0, 0, 0)
        self.name_label_input_layout.addWidget(self.option_label)
        self.name_label_input_layout.addWidget(self.option_input)

        self.option_actual_content_label = CustomLabel(name="Content")

        self.option_actual_input = CustomLineEdit(placeholder_text="", parent=self)
        self.option_actual_input.setStyleSheet(f"""
        QLineEdit {{
            border:1px solid {self.parent.menu_header_layout.random_color};
            padding-left:7px;
            border-radius:2px;
            background-color:white;
            padding-left:10px;
            padding-right:5px;
            }}
        """)
        self.option_actual_input.setObjectName("option_content")
        self.option_actual_input.setFixedSize(size)

        self.option_content_label_input_layout = QVBoxLayout()
        self.option_content_label_input_layout.setContentsMargins(0, 0, 0, 0)

        self.option_content_label_input_layout.addWidget(self.option_actual_content_label)
        self.option_content_label_input_layout.addWidget(self.option_actual_input)

        main_layout = QHBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        main_layout.addLayout(self.name_label_input_layout)
        main_layout.addLayout(self.option_content_label_input_layout)

        self.setLayout(main_layout)
