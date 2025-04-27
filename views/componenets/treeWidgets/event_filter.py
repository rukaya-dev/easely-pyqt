from PyQt6.QtCore import QObject, QPointF, QEvent, pyqtSignal
from PyQt6.QtWidgets import QApplication, QTreeWidget, QTreeWidgetItem
from PyQt6.QtGui import QMouseEvent


class PageEventFilter(QObject):
    itemClicked = pyqtSignal(QTreeWidgetItem, int)

    def __init__(self, parent=None, item=None):
        super().__init__(parent)
        if not isinstance(item, QTreeWidgetItem):
            raise TypeError("item must be a QTreeWidgetItem")
        self.mItem = item

        # Assuming mItem.treeWidget() returns a QTreeWidget, and it has a signal 'itemClicked'
        self.itemClicked.connect(self.mItem.treeWidget().itemClicked)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.MouseButtonPress:
            self.itemClicked.emit(self.mItem, 0)
            return False
        else:
            return super().eventFilter(obj, event)
