from PyQt6 import QtCore
from PyQt6.QtWidgets import QWidget, QVBoxLayout

from views.componenets.textEditorComponenets.menuBar.custome_combo_box import CustomComboBox


class TextTypeChanger(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.combo_box = CustomComboBox()
        self.combo_box.setCurrentIndex(0)
        self.combo_box.setCurrentText('Normal Text')
        self.old_index = self.combo_box.currentIndex()

        # Connect the signal to the slot method
        self.combo_box.currentIndexChanged.connect(self.on_current_index_changed)

        layout = QVBoxLayout()
        layout.addWidget(self.combo_box)
        self.setLayout(layout)

    def on_current_index_changed(self, index):
        self.currentIndexChanged.emit(index)
        self.old_index = index

    # Define a signal that can be connected to a slot in the parent widget

    currentIndexChanged = QtCore.pyqtSignal(int)

