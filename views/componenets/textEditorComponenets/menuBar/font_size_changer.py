from PyQt6.QtWidgets import QApplication, QWidget, QHBoxLayout, QPushButton, QTextEdit, QLineEdit, QMenu, QApplication
from PyQt6.QtGui import QFont, QPalette
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtCore import Qt

from PyQt6.QtCore import Qt, QRect, QPoint, QSize


class CustomLineEdit(QLineEdit):
    lineEditMenuActionTriggeredSignal = pyqtSignal(int)  # Define a custom signal

    def __init__(self, font_sizes, parent=None):
        super(CustomLineEdit, self).__init__(parent)
        self.parent = parent
        self.font_sizes = font_sizes
        self.setReadOnly(True)  # Make it not editable
        self.setCursorPosition(0)  # Set cursor position to the
        self.setFixedSize(60, 30)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.setToolTip("Font size")

        # Retrieve the base color from the palette
        # Set the base color of the palette for QTextEdit to the retrieved base color
        self.setStyleSheet(
            """QLineEdit {border:1px solid #DFE4E6;border-radius:7px; background-color:#F0F0F0; color:black;}""")

    def mousePressEvent(self, event):
        # When the line edit is clicked, show the dropdown menu
        menu = QMenu(self)
        menu.setStyleSheet("""
                      QMenu {
                            color:black;
                        }
                        QMenu::item {
                            padding-bottom:5px;
                            padding-top:5px;
                            padding-left: 20px;

                        }
                        QMenu::item:selected {
                            background-color:#ebf2f8;

                        }
        
        
        """)

        menu.setFixedSize(QSize(60, 350))
        for size in self.font_sizes:
            action = menu.addAction(str(size))
            action.triggered.connect(
                lambda _, s=size: self.lineEditMenuActionTriggeredSignal.emit(s))  # Emit the signal with font size

        menu_x = self.mapToGlobal(QPoint(0, 0)).x() + (self.width() - menu.width()) // 2
        menu_y = self.mapToGlobal(QPoint(0, 0)).y() + self.height()

        menu_global = QPoint(menu_x, menu_y)

        menu.move(menu_global)
        menu.exec()


class FontSizeView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setFixedSize(QSize(170, 50))

        self.font_sizes = [8, 9, 10, 11, 12, 14, 18, 24, 30, 36, 48, 60, 72, 96]  # Define custom font sizes

        # Create buttons for increasing and decreasing font size
        self.btnIncreaseFontSize = QPushButton('+')
        self.btnIncreaseFontSize.setToolTip("Increase font size")
        self.btnDecreaseFontSize = QPushButton('-')
        self.btnDecreaseFontSize.setToolTip("Decrease font size")
        self.btnIncreaseFontSize.setStyleSheet("QPushButton {background-color:white; font-size:18px;border:0;color:black;}")
        self.btnDecreaseFontSize.setStyleSheet("QPushButton {background-color:white; font-size:18px;border:0;color:black;}")
        self.btnIncreaseFontSize.setFixedWidth(20)
        self.btnDecreaseFontSize.setFixedWidth(20)

        # Create a QLineEdit to display and select font size
        self.lineEditFontSize = CustomLineEdit(self.font_sizes, self)
        self.lineEditFontSize.setText(str(16))  # Default display value

        # Add buttons and line edit to layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.btnIncreaseFontSize)
        layout.addWidget(self.lineEditFontSize)
        layout.addWidget(self.btnDecreaseFontSize)

        # Set the window's main layout
        self.setLayout(layout)
