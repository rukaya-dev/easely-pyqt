from PyQt6.QtCore import pyqtSignal, pyqtSlot
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtWidgets import QMenu

from stylesheets.common_stylesheet import menu_stylesheet


class ContextMenu(QMenu):
    itemSelected = pyqtSignal(str)

    def __init__(self, controller, parent=None):
        super().__init__(parent)

        self.parent = parent
        self.controller = controller

        self.active_tab = self.controller.store.get_active_report_tab()

        self.setContentsMargins(5, 4, 5, 4)

        font = self.font()
        font.setPointSize(11)
        font.setWeight(font.Weight.Normal)
        self.setFont(font)

        self.setStyleSheet(menu_stylesheet)
        self.setFixedWidth(200)

        view_action = QAction(QIcon(':/resources/icons/eye.svg'), "View", self)
        view_action.setData("view")

        delete_action = QAction(QIcon(':/resources/icons/delete.svg'), "Delete", self)
        delete_action.setData("delete")

        print_action = QAction(QIcon(':/resources/icons/make_report.svg'), "Print", self)
        print_action.setData("print")

        self.addAction(view_action)

        self.addSeparator()

        edit_menu = self.addMenu("Edit")
        edit_menu.setContentsMargins(10, 4, 10, 4)
        edit_menu.setStyleSheet(menu_stylesheet)
        edit_menu.setFixedWidth(150)
        edit_menu.setFont(font)

        edit_report_status_action = edit_menu.addAction(QIcon(), "Status")
        edit_report_status_action.setData("edit_status")
        edit_report_status_action.setToolTip("Edit Report Status")

        edit_report_content_action = edit_menu.addAction(QIcon(), "Report Content")
        edit_report_content_action.setData("edit_report_content")
        edit_report_content_action.setToolTip("Edit Report Content")

        self.addSeparator()
        self.addAction(delete_action)
        self.addAction(print_action)

        self.triggered.connect(self.on_action_triggered)

    @pyqtSlot(QAction)
    def on_action_triggered(self, action: QAction):
        self.itemSelected.emit(action.data())
        self.close()
