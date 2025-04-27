from PyQt6 import QtCore
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPalette, QColor
from PyQt6.QtWidgets import QStyledItemDelegate, QComboBox, QSizePolicy, QListView


class CustomComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)

        font = self.font()
        font.setPointSize(11)
        self.setFont(font)

        self.setItemDelegate(ComboBoxDelegate())
        self.base_style_sheet = """
            QComboBox {
                border:1px solid #C7C7C7;
                border-radius:2px;
                background-color:white;
                color:black;
                padding-left:10px;
                padding-right:5px;
            }
            QComboBox QAbstractItemView 
            {
                min-width: 150px;
                color:black;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 15px;
                border-left-width: 0px;
                padding-right:5px;
            }
            QComboBox::down-arrow {
                image: url(:resources/icons/expand_more.svg);
            }
            
            QComboBox::down-arrow:on { /* shift the arrow when popup is open */
                top: 1px;
                left: 1px;
            }
        """

        self.setStyleSheet(self.base_style_sheet)
        self.setFixedHeight(40)

        self.setAttribute(Qt.WidgetAttribute.WA_AlwaysStackOnTop)
        self.raise_()

    def wheelEvent(self, e):
        pass

class ComboBoxDelegate(QStyledItemDelegate):
    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        option.displayAlignment = QtCore.Qt.AlignmentFlag.AlignVCenter
        option.textElideMode = Qt.TextElideMode.ElideRight

        # Add Margin
        option.rect.adjust(0, 0, 0, 0)
        # Adjust font size
        font = option.font
        font.setWeight(QFont.Weight.Medium)
        font.setPointSize(12)
        option.font = font
        option.palette.setColor(QPalette.ColorRole.Text, QColor('black'))

    def sizeHint(self, option, index):
        original_hint = super().sizeHint(option, index)
        min_height = 30  # Set your desired minimum height here
        width = 400
        height = max(original_hint.height(), min_height)
        return QtCore.QSize(width, height)
