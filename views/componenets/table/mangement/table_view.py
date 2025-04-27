from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QTableView, QAbstractItemView, QHeaderView, QSizePolicy, QStyledItemDelegate


class TableView(QTableView):
    def __init__(self):
        super().__init__()

        font = self.font()
        font.setPointSize(12)
        font.setWeight(font.Weight.Normal)
        self.setFont(font)

        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.setItemDelegate(ElidedItemDelegate())
        self.setShowGrid(False)
        self.resizeColumnToContents(True)
        self.setWordWrap(False)
        self.setContentsMargins(0, 0, 0, 0)

        self.baseStyle = """
                 QTableView {
                     border: 0;
                     padding:10px;
                     color:#27272a;
                     background-color:white;
                     outline:none;
                 }
                 QTableView::item {
                     padding: 5px;
                     border-bottom: 1px solid #DCE0E3;

                 }
                 QTableView::item:selected {
                    background-color: #ebf2f8;
                    padding: 5px;
                    border:0;
                    border-bottom: 1px solid #DCE0E3;
                    color:#375F6C;
                 }
                QHeaderView:section:first {
                  border-top-left-radius:3px;
                  border-bottom-left-radius:3px;
                }
                QHeaderView:section:last {
                  border-top-right-radius:3px;
                  border-top-left-radius:3px;
                }
                 QHeaderView::section {
                  color: #4B4E58;
                  font-size:11pt;
                  border:0;
                  padding:10px;
                  background-color:#F6F8FA;
                }
                QScrollBar:vertical {
                    background: transparent;
                    width: 8px; 
                    margin: 0px;
                }
                
                QScrollBar::handle:vertical {
                    background-color: rgba(0, 0, 0, 50); /* Semi-transparent handle */
                    min-height: 20px; /* Minimum height for the handle */
                    border-radius: 4px; /* Rounded corners for the handle */
                }
                QScrollBar::handle:vertical:hover {
                    background-color: rgba(0, 0, 0, 50); /* Slightly darker on hover */
                }
                   
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    height: 0px; /* No buttons at the ends */
                    border: none;
                    background: none;
                }
                
                QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                    background: none;
                }
                
                QScrollBar:horizontal {
                    background: transparent;
                    width: 8px; 
                    margin: 0px;
                }
                
                QScrollBar::handle:horizontal {
                    background-color: rgba(0, 0, 0, 50); /* Semi-transparent handle */
                    min-height: 20px; /* Minimum height for the handle */
                    border-radius: 4px; /* Rounded corners for the handle */
                }
                
                QScrollBar::handle:horizontal:hover {
                    background-color: rgba(0, 0, 0, 50); /* Slightly darker on hover */
                }
                
                QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                    height: 0px; /* No buttons at the ends */
                    border: none;
                    background: none;
                }
                
                QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
                    background: none;
                }
             """
        self.setStyleSheet(self.baseStyle)

        self.table_header = HeaderView(Qt.Orientation.Horizontal, self)
        self.table_header.setDefaultAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.table_header.setDefaultSectionSize(160)
        self.table_header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.setHorizontalHeader(self.table_header)

        self.v_header = self.verticalHeader()
        self.v_header.setDefaultAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.v_header.setDefaultSectionSize(57)
        self.v_header.setVisible(False)
        self.v_header.setStyleSheet("padding:50px;")

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setSortingEnabled(False)


class ElidedItemDelegate(QStyledItemDelegate):
    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        option.textElideMode = Qt.TextElideMode.ElideRight
        option.wrapText = False


class HeaderView(QHeaderView):
    def __init__(self, orientation, parent=None):
        super(HeaderView, self).__init__(orientation, parent)

    def paintSection(self, painter, rect, logical_index):
        super(HeaderView, self).paintSection(painter, rect, logical_index)
