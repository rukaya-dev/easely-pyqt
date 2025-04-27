from PyQt6 import QtCore
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QFont, QPalette, QColor
from PyQt6.QtWidgets import QVBoxLayout, QFontComboBox, QStyledItemDelegate, QFontComboBox, QListView

from configs.app_config import get_font_family


class FontFamilyChanger(QFontComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFixedSize(QSize(150, 30))
        self.setStyleSheet("""
            QFontComboBox {
                border: 0;
                padding: 1px 18px 1px 10px;
                min-width: 6em;
                color:black;
                combobox-popup: 0;
                background: white;

            }

            QFontComboBox:editable {
                background: white;
            }

            /* QFontComboBox gets a blue border when focused */
            QFontComboBox:focus {
                border: 2px solid darkgray;
            }

            /* The drop-down button */
            QFontComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 15px;
                border-left-width: 0px;
                padding-right:5px;
                }

            /* The arrow in the drop-down button */
            QFontComboBox::down-arrow {
                image: url(:resources/icons/expand_more.svg);
                padding-right:10px;
            }

            /* The items in the drop-down */
            QFontComboBox QAbstractItemView {
                selection-background-color: lightblue;
            }

            /* Set the spacing between items in the drop-down */
            QFontComboBox QAbstractItemView::item {
                min-height: 30px;
                padding: 5px 20px;
            }


        """)
        self.setEditable(False)



