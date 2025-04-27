from PyQt6.QtCore import Qt
from PyQt6.QtGui import QTextCursor, QTextDocument, QColor

from PyQt6.QtWidgets import QHBoxLayout, QWidget, QVBoxLayout, QSpacerItem, \
    QSizePolicy, QStackedWidget

from utils.utlis import string_to_slug
from views.componenets.customsComponents.custom_scroll_area import CustomScrollArea
# Components

from views.componenets.textEditorComponenets.menuBar.format_bar import FormatBar
from views.componenets.textEditorComponenets.zeusEditor.zeus_editor import ZeusTextBox


class MainReportEditorView(QWidget):
    def __init__(self, view_type, data, parent=None):
        super().__init__(parent)

        self.parent = parent
        self.data = data
        self.category = ""

        self.view_type = view_type

        self.zeus_editor_text_box = ZeusTextBox(self)

        self.format_bar = FormatBar(self.zeus_editor_text_box, self)

        self.rendered_templates_stack_widget = QStackedWidget(self)

        central_widget = QWidget()

        zeus_editor_scroll_area = CustomScrollArea(self)
        zeus_editor_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        zeus_editor_scroll_area.setWidget(central_widget)

        wrapper_widget = QWidget()
        wrapper_widget.setMaximumWidth(1320)
        wrapper_widget.setObjectName("template_editor_view_central_widget")
        wrapper_widget.setStyleSheet("""
                          QWidget#template_editor_view_central_widget {
                              background-color:#FAFAFA;;
                          }
                      """)

        self.editor_layout = QHBoxLayout(central_widget)
        self.editor_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.editor_layout.setSpacing(10)

        self.editor_layout.addWidget(self.zeus_editor_text_box)
        self.editor_layout.addWidget(self.rendered_templates_stack_widget)

        main_layout = QVBoxLayout(wrapper_widget)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(20)

        main_layout.addWidget(self.format_bar)
        main_layout.addWidget(zeus_editor_scroll_area)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 50)
        layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        layout.addWidget(wrapper_widget, 1)

        self.setLayout(layout)

    def add_option_to_editor(self, option_data):
        if option_data["option_name"]:
            option_name = string_to_slug(option_data['option_name'])
            if option_data["option_check_state"]:
                if option_name not in self.zeus_editor_text_box.options_list:
                    self.zeus_editor_text_box.options_list.append(option_name)

                    cursor = self.zeus_editor_text_box.textCursor()
                    option_html = option_name
                    cursor.insertText(" ")
                    start_pos = cursor.position()
                    cursor.insertText(option_html)
                    cursor.insertText(" ")

                    cursor.setPosition(start_pos)
                    cursor.movePosition(cursor.MoveOperation.Right, cursor.MoveMode.KeepAnchor, len(option_html))

                    option_char_format = cursor.charFormat()
                    option_char_format.setBackground(QColor("#edebfc"))
                    option_char_format.setForeground(QColor("black"))
                    cursor.setCharFormat(option_char_format)
            else:
                if option_name in self.zeus_editor_text_box.options_list:
                    self.zeus_editor_text_box.options_list.remove(option_name)
                    self.remove_option_from_editor(option_name)

    def remove_option_from_editor(self, option_name):

        self.zeus_editor_text_box.textCursor().beginEditBlock()
        doc = self.zeus_editor_text_box.document()
        cursor = QTextCursor(doc)
        while True:
            cursor = doc.find(option_name, cursor, QTextDocument.FindFlag.FindCaseSensitively)
            if cursor.isNull():
                break
            cursor.insertText("")
            cursor.setCharFormat(self.zeus_editor_text_box.currentCharFormat())
        self.zeus_editor_text_box.textCursor().endEditBlock()
