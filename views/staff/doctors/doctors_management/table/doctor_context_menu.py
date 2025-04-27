from PyQt6.QtCore import pyqtSignal, pyqtSlot
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtWidgets import QMenu

from stylesheets.common_stylesheet import menu_stylesheet


class DoctorContextMenu(QMenu):
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

        edit_action = QAction(QIcon(':/resources/icons/edit.svg'), "Edit", self)
        edit_action.setData("edit")

        delete_action = QAction(QIcon(':/resources/icons/delete.svg'), "Delete", self)
        delete_action.setData("delete")

        service_management_action = QAction(QIcon(':/resources/icons/doctor_service.svg'), "Service Management", self)
        service_management_action.setData("service_management")

        self.addAction(view_action)
        self.addAction(edit_action)
        self.addAction(delete_action)
        self.addAction(service_management_action)
        self.triggered.connect(self.on_action_triggered)

    @pyqtSlot(QAction)
    def on_action_triggered(self, action: QAction):
        self.itemSelected.emit(action.data())
        self.close()
