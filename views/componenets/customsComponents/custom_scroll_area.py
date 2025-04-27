
from PyQt6.QtWidgets import QScrollArea


class CustomScrollArea(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWidgetResizable(True)
        self.baseStyle = """
                QScrollArea {
                    border:0;
                    border-radius:7px;
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
                    border: none;
                    background: transparent;
                    height: 8px; /* Thin horizontal scrollbar */
                    margin: 0px;
                }

                QScrollBar::handle:horizontal {
                    background-color: rgba(0, 0, 0, 140); /* Semi-transparent handle */
                    min-width: 20px; /* Minimum width for the handle */
                    border-radius: 4px; /* Rounded corners for the handle */
                }

                QScrollBar::handle:horizontal:hover {
                    background-color: rgba(0, 0, 0, 140); /* Slightly darker on hover */
                }

                QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                    width: 0px; /* No buttons at the ends */
                    border: none;
                    background: none;
                }

                QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
                    background: none;
                }
             """
        self.setStyleSheet(self.baseStyle)



