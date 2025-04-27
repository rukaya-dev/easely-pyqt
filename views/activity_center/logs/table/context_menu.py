from PyQt6.QtCore import pyqtSignal, pyqtSlot
from PyQt6.QtGui import QIcon,  QAction
from PyQt6.QtWidgets import QMenu

from stylesheets.common_stylesheet import menu_stylesheet


class LogsContextMenu(QMenu):
    itemSelected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        font = self.font()
        font.setPointSize(11)
        font.setWeight(font.Weight.Normal)
        self.setFont(font)

        self.setContentsMargins(0, 4, 0, 4)

        self.setFixedWidth(200)

        self.setStyleSheet(menu_stylesheet)

        view_action = QAction(QIcon(':/resources/icons/eye.svg'), "View", self)
        view_action.setData("view")

        self.addAction(view_action)
        self.triggered.connect(self.on_action_triggered)

    @pyqtSlot(QAction)
    def on_action_triggered(self, action: QAction):
        self.itemSelected.emit(action.data())
        self.close()
