from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QWidget, QPushButton, QHBoxLayout


class TextStyleChanger(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.text_styles_h_layout = None
        self.underline_btn = None
        self.italic_btn = None
        self.bold_btn = None
        self.initUI()

    def initUI(self):

        self.bold_btn = QPushButton()
        self.bold_btn.setObjectName("bold_btn")
        self.bold_btn.setText("B")
        self.bold_btn.setFixedSize(QSize(25, 30))
        self.bold_btn.setToolTip("Bold")
        self.bold_btn.setStyleSheet("""QPushButton#bold_btn:!checked {background-color:#F0F0F0;border-radius:2px;color:#354859;}
                                    QPushButton#bold_btn:checked {background-color: #354859;border-radius:2px; color:white font-weight:bold;}""")
        self.bold_btn.setCheckable(True)

        self.italic_btn = QPushButton()
        self.italic_btn.setText("I")
        self.italic_btn.setObjectName("italic_btn")
        self.italic_btn.setFixedSize(QSize(25, 30))
        self.italic_btn.setToolTip("Italic")

        self.italic_btn.setCheckable(True)
        self.italic_btn.setStyleSheet("""QPushButton:!checked {font-style:italic;background-color:#F0F0F0;border-radius:2px;color:#354859;}
                                    QPushButton:checked {font-style:italic;background-color: #354859;border-radius:2px;color:white;}""")

        self.underline_btn = QPushButton()
        self.underline_btn.setText("U")
        self.underline_btn.setObjectName("underline_btn")
        self.underline_btn.setFixedSize(QSize(25, 30))
        self.underline_btn.setToolTip("Underline")
        self.underline_btn.setCheckable(True)
        self.underline_btn.setStyleSheet("""QPushButton:!checked {background-color:#F0F0F0;border-radius:2px;text-decoration: underline;color:#354859;}
                                    QPushButton:checked {background-color: #354859;border-radius:2px;color:white;text-decoration: underline;}""")

        self.text_styles_h_layout = QHBoxLayout()
        self.text_styles_h_layout.setContentsMargins(0, 0, 0, 0)
        self.text_styles_h_layout.setSpacing(0)
        self.text_styles_h_layout.addWidget(self.bold_btn)
        self.text_styles_h_layout.addWidget(self.italic_btn)
        self.text_styles_h_layout.addWidget(self.underline_btn)

        self.setLayout(self.text_styles_h_layout)

    def update_button_style(self, button: QPushButton, checked):
        button_name = button.objectName()

        styles = {
            "bold_btn": (
                f"background-color: #354859; border-radius: 2px; color: white; font-weight: bold;",
                f"background-color: #F0F0F0; border-radius: 2px;color:#354859;"
            ),
            "italic_btn": (
                f"font-style: italic; background-color: #354859; border-radius: 2px; color: white;",
                f"background-color: #F0F0F0; border-radius: 2px; font-style: italic;color:#354859;"
            ),
            "underline_btn": (
                f"background-color: #354859; border-radius: 2px; color: white; text-decoration: underline;",
                f"background-color: #F0F0F0; border-radius: 2px; text-decoration: underline;color:#354859;"
            )
        }

        if checked:
            style_checked = styles.get(button_name, ("", ""))[0]
            button.setStyleSheet(f"QPushButton#{button_name} {{{style_checked}}}")
            button.setChecked(True)

        else:
            style_unchecked = styles.get(button_name, ("", ""))[1]
            button.setStyleSheet(f"QPushButton#{button_name} {{{style_unchecked}}}")
            button.setChecked(False)


class TextStyle:
    def __init__(self, font_size=None, bold=None, italic=None, underline=None, color=None, backgroundColor=None,
                 fontFamily=None):
        self.font_size = font_size
        self.bold = bold
        self.italic = italic
        self.underline = underline
        self.color = color
        self.backgroundColor = backgroundColor
        self.fontFamily = fontFamily


class HasDifferentAttributes:
    def __init__(self, has_different_font_size=None, has_different_font_weight=None, has_different_font_italic=None,
                 has_different_font_underline=None, has_different_font_color=None):
        self.has_different_font_size = has_different_font_size
        self.has_different_font_weight = has_different_font_weight
        self.has_different_font_italic = has_different_font_italic
        self.has_different_font_underline = has_different_font_underline
        self.has_different_font_color = has_different_font_color


class Option:
    def __init__(self, font_size=None, bold=None, italic=None, underline=None, color=None, backgroundColor=None,
                 font_family=None):
        self.font_size = font_size
        self.bold = bold
        self.italic = italic
        self.underline = underline
        self.color = color
        self.backgroundColor = backgroundColor
        self.font_family = font_family
