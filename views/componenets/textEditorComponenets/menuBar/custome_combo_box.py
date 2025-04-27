from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtWidgets import QStyledItemDelegate, QComboBox, QAbstractItemDelegate, QStyle, QListView, QApplication
from PyQt6 import QtGui, QtCore


class CustomComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.addItems(
            ["Normal Text", "Heading 1", "Heading 2", "Heading 3", "Heading 4", "Heading 5", "Heading 6"])

        self.setStyleSheet("""
            QComboBox {
                border: 0;
                padding: 1px 18px 1px 10px;
                min-width: 6em;
                min-height:30px;

            }

            QComboBox:editable {
                background: white;
            }

            /* QComboBox gets a blue border when focused */
            QComboBox:focus {
                border: 2px solid red;
            }

            /* The drop-down button */
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 15px;
                border-left-color: darkgray;
                border-left-style: solid; /* just a single line */
                border-top-right-radius: 3px; /* same radius as the QComboBox */
                border-bottom-right-radius: 3px;
            }

            /* The arrow in the drop-down button */
            QComboBox::down-arrow {
                image: url(:resources/icons/expand_more.svg);
                padding-right:10px;
            }

            /* The items in the drop-down */
            QComboBox QAbstractItemView {
                selection-background-color: lightblue;
            }

            /* Set the spacing between items in the drop-down */
            QComboBox QAbstractItemView::item {
                min-height: 30px;
                padding:5px 20px;
            }
        """)
        self.setItemDelegate(CustomDelegate(self))


class CustomDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.styleCache = {}  # Cache for storing style

    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        option.displayAlignment = Qt.AlignmentFlag.AlignVCenter
        item_text = index.data()

        if item_text in self.styleCache:
            # Use cached style
            cached_style = self.styleCache[item_text]
            option.font.setPointSize(cached_style['pointSize'])
            option.font.setBold(cached_style['isBold'])
        else:
            if item_text == "Heading 1":
                option.font.setPointSize(18)
                option.font.setBold(True)
            elif item_text == "Heading 2":
                option.font.setPointSize(16)
                option.font.setBold(True)
            elif item_text == "Heading 3":
                option.font.setPointSize(14)
                option.font.setBold(True)
            elif item_text == "Heading 4":
                option.font.setPointSize(12)
                option.font.setBold(True)
            elif item_text == "Heading 5":
                option.font.setPointSize(11)
                option.font.setBold(True)
            elif item_text == "Heading 6":
                option.font.setPointSize(10)
                option.font.setBold(True)
            elif item_text == "Normal Text":
                option.font.setPointSize(12)
                option.font.setBold(False)

            self.styleCache[item_text] = {
                'pointSize': option.font.pointSize(),
                'isBold': option.font.bold()
            }
