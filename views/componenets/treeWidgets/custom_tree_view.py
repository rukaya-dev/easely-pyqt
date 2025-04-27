from PyQt6.QtWidgets import QTreeWidget, QAbstractItemView, QApplication


class CustomTreeWidget(QTreeWidget):
    def __init__(self):
        super().__init__()

        self.expandAll()
        self.setRootIsDecorated(False)
        self.expandToDepth(0)
        self.setItemsExpandable(False)

        self.setStyleSheet("""
           QTreeWidget {
            background-color : white;
            border:0;
            show-decoration-selected: 0;
           }
           QTreeWidget::branch {
             border-image: url(none.png); 
            }


           """)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.viewport().setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragEnabled(True)
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.setHeaderHidden(True)
        self.setColumnCount(1)
        self.setIndentation(50)
        self.setAutoScroll(True)

    def mousePressEvent(self, event):
        self.clearSelection()
        self.setCurrentItem(None)
        QTreeWidget.mousePressEvent(self, event)
