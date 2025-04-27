
from PyQt6.QtWidgets import QTreeWidget, QAbstractItemView,  QAbstractScrollArea,  QHeaderView


class CustomTreeWidget(QTreeWidget):
    def __init__(self):
        super().__init__()

        self.expandAll()
        self.setRootIsDecorated(True)
        self.expandToDepth(0)
        self.setItemsExpandable(True)

        self.setStyleSheet("""
            QTreeWidget {
                 border:0;
                 background-color:white;
                 show-decoration-selected: 0;
                 color:black;

            }
            QTreeWidget::item:selected {
                 color:black;
             } 
             QTreeWidget::item:selected {
                 background:#edf2fa;
                 color:black;
             }
             QTreeWidget::item:selected:active {
                 background:#edf2fa;
                color:black;
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

        self.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.verticalScrollBar().setSingleStep(10)
        self.horizontalScrollBar().setContentsMargins(50, 50, 50, 50)
        self.horizontalScrollBar().setEnabled(True)
        self.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)

        self.header().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

    def mousePressEvent(self, event):
        self.clearSelection()
        self.setCurrentItem(None)
        QTreeWidget.mousePressEvent(self, event)

    def dragMoveEvent(self, event):
        target_item = self.itemAt(int(event.position().x()), int(event.position().y()))
        if target_item is not None and target_item.parent() is None:
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        target_item = self.itemAt(int(event.position().x()), int(event.position().y()))
        if target_item is None:
            source_item = self.currentItem()
            source_item_parent = source_item.parent()
            if source_item_parent is None:
                source_item = self.takeTopLevelItem(self.indexOfTopLevelItem(source_item))
            else:
                source_item = source_item_parent.takeChild(source_item_parent.indexOfChild(source_item))

            self.addTopLevelItem(source_item)
            event.accept()
        else:
            event.ignore()
