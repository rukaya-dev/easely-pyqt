from PyQt6.QtCore import pyqtSignal, pyqtSlot
from PyQt6.QtGui import QIcon,  QAction
from PyQt6.QtWidgets import QMenu

from stylesheets.common_stylesheet import menu_stylesheet


class ContextMenu(QMenu):
    itemSelected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setContentsMargins(0, 4, 0, 4)

        font = self.font()
        font.setPointSize(11)
        font.setWeight(font.Weight.Normal)
        self.setFont(font)

        self.setStyleSheet(menu_stylesheet)
        self.setFixedWidth(200)

        view_action = QAction(QIcon(':/resources/icons/eye.svg'), "View", self)
        view_action.setData("view")

        put_back_action = QAction(QIcon(':/resources/icons/revert.svg'), "Put Back", self)
        put_back_action.setData("revert")

        self.addAction(view_action)
        self.addAction(put_back_action)
        self.triggered.connect(self.on_action_triggered)

    @pyqtSlot(QAction)
    def on_action_triggered(self, action: QAction):
        self.itemSelected.emit(action.data())
        self.close()
