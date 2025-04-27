from PyQt6.QtCore import pyqtSignal, pyqtSlot
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtWidgets import QMenu

from stylesheets.common_stylesheet import menu_stylesheet


class ContextMenu(QMenu):
    itemSelected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.parent = parent

        font = self.font()
        font.setPointSize(11)
        font.setWeight(font.Weight.Normal)
        self.setFont(font)

        self.setContentsMargins(5, 4, 5, 4)

        self.setStyleSheet(menu_stylesheet)
        self.setFixedWidth(200)

        view_action = QAction(QIcon(':/resources/icons/eye.svg'), "View", self)
        view_action.setData("view")

        self.delete_action = QAction(QIcon(':/resources/icons/delete.svg'), "Delete", self)

        self.delete_action.setData("delete")

        self.addAction(view_action)

        self.addSeparator()

        edit_menu = self.addMenu("Edit")
        edit_menu.setContentsMargins(10, 4, 10, 4)
        edit_menu.setFixedWidth(150)

        edit_menu.setStyleSheet(menu_stylesheet)
        edit_menu.setFont(font)

        edit_user_info_action = edit_menu.addAction(QIcon(":/resources/icons/info.svg"), "User info")
        edit_user_info_action.setData("edit_user_info")

        edit_password_data_action = edit_menu.addAction(QIcon(":/resources/icons/key.svg"), "Password")
        edit_password_data_action.setData("edit_password")

        self.addSeparator()
        self.addAction(self.delete_action)

        self.triggered.connect(self.on_action_triggered)

    @pyqtSlot(QAction)
    def on_action_triggered(self, action: QAction):
        self.itemSelected.emit(action.data())
        self.close()

