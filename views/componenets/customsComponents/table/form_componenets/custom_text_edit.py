from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QTextEdit


class CustomTextEdit(QTextEdit):
    def __init__(self, border_radius, placeholder_text, parent=None):
        super().__init__(parent)

        self.placeholder_text = placeholder_text
        self.border_radius = border_radius

        font = self.font()
        font.setPointSize(12)
        font.setWeight(font.Weight.Normal)
        self.setFont(font)

        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self.setPlaceholderText(self.placeholder_text)

        self.focus_in_stylesheet = f"""
        QTextEdit {{
            border:1px solid #8D8D8D;
            border-radius: {self.border_radius}px;
            background-color:white;
            color:black;
            padding:10px;
        }}
        QScrollBar:vertical {{
            background: transparent;
            width: 8px; 
             margin: 0px;
        }}
                
        QScrollBar::handle:vertical, QScrollBar::handle:horizontal {{
            background-color: rgba(0, 0, 0, 120); /* Semi-transparent handle */
            min-width: 20px; /* Minimum width for the handle */
            border-radius: 4px; /* Rounded corners for the handle */
        }}
                QScrollBar::handle:vertical:hover {{
            background-color: rgba(0, 0, 0, 140); /* Slightly darker on hover */
        }}
                   
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px; /* No buttons at the ends */
            border: none;
            background: none;
        }}
                
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
            background: none;
        }}
                
        QScrollBar:horizontal {{
            border: none;
            background: transparent;
            height: 8px; /* Thin horizontal scrollbar */
            margin: 0px;
        }}
                
        QScrollBar::handle:horizontal {{
            background-color: rgba(0, 0, 0, 120); /* Semi-transparent handle */
            min-width: 20px; /* Minimum width for the handle */
            border-radius: 4px; /* Rounded corners for the handle */
        }}
                
        QScrollBar::handle:horizontal:hover {{
            background-color: rgba(0, 0, 0, 140); /* Slightly darker on hover */
            min-width: 20px; /* Minimum width for the handle */
            border-radius: 4px; /* Rounded corners for the handle */
        }}
                
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0px; /* No buttons at the ends */
            border: none;
            background: none;
        }}
                
        QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
            background: none;
        }}
        """
        self.base_style_sheet = f"""
        QTextEdit {{
            border:1px solid #C7C7C7;
            border-radius: {self.border_radius}px;
            background-color:white;
            color:black;
            padding:10px;
        }}
              QScrollBar:vertical {{
            background: transparent;
            width: 8px; 
             margin: 0px;
        }}
                
        QScrollBar::handle:vertical, QScrollBar::handle:horizontal {{
            background-color: rgba(0, 0, 0, 120); /* Semi-transparent handle */
            min-width: 20px; /* Minimum width for the handle */
            border-radius: 4px; /* Rounded corners for the handle */
        }}
                QScrollBar::handle:vertical:hover {{
            background-color: rgba(0, 0, 0, 140); /* Slightly darker on hover */
        }}
                   
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px; /* No buttons at the ends */
            border: none;
            background: none;
        }}
                
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
            background: none;
        }}
                
        QScrollBar:horizontal {{
            border: none;
            background: transparent;
            height: 8px; /* Thin horizontal scrollbar */
            margin: 0px;
        }}
                
        QScrollBar::handle:horizontal {{
            background-color: rgba(0, 0, 0, 120); /* Semi-transparent handle */
            min-width: 20px; /* Minimum width for the handle */
            border-radius: 4px; /* Rounded corners for the handle */
        }}
                
        QScrollBar::handle:horizontal:hover {{
            background-color: rgba(0, 0, 0, 140); /* Slightly darker on hover */
            min-width: 20px; /* Minimum width for the handle */
            border-radius: 4px; /* Rounded corners for the handle */
        }}
                
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0px; /* No buttons at the ends */
            border: none;
            background: none;
        }}
                
        QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
            background: none;
        }}
        """

        self.setStyleSheet(self.base_style_sheet)

    def focusInEvent(self, event):
        self.setStyleSheet(self.focus_in_stylesheet)
        super().focusInEvent(event)

    def focusOutEvent(self, event):
        self.setStyleSheet(self.base_style_sheet)
        super().focusOutEvent(event)
