from datetime import datetime

from PyQt6.QtWidgets import QPushButton, QLabel, QHBoxLayout
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtWidgets import QWidget, QVBoxLayout

from views.componenets.customsComponents.dates_and_times.custom_date_range_selection import CustomDateRangeSelection
from views.componenets.customsComponents.menus.drop_down_menu_component import CustomDropDownMenuComponent

from datetime import date


class CustomDateFilterSelectionWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName("custom_date_filter_selection_widget")

        self.selection_widget = CustomDateRangeSelection(self)
        self.selection_widget.apply_btn.clicked.connect(self.update_custom_filter_btn_text)

        self.custom_date_menu_button = CustomDateMenuButton(self)

        self.drop_down_menu = CustomDropDownMenuComponent(menu_button=self.custom_date_menu_button,
                                                          menu_pos="right",
                                                          menu_widget=self.selection_widget)
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.layout.addWidget(self.drop_down_menu)
        self.setLayout(self.layout)

    def update_custom_filter_btn_text(self):
        self.drop_down_menu.menu.close()
        q_date = self.selection_widget.custom_date_calendar.selectedDate()
        pydate = date(q_date.year(), q_date.month(), q_date.day())
        formatted_date = f"{pydate.day} {pydate.strftime('%B')}"
        self.custom_date_menu_button.button.setText(formatted_date)


class CustomDateMenuButton(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.icon_label = QLabel(self)
        self.icon_label.setFixedSize(QSize(15, 15))

        self.button = QPushButton(datetime.now().strftime("%d %B"))
        self.button.setObjectName("custom_date_menu_button")

        font = self.button.font()
        font.setPointSize(10)
        font.setWeight(font.Weight.Medium)
        self.button.setFont(font)

        self.button.setFixedSize(75, 15)

        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(0)

        layout.addWidget(self.icon_label)
        layout.addWidget(self.button)

        self.de_active_style_sheet = """
         QWidget {
                border:0;
                background-color:white;
                border-top-right-radius:3px;
                border-bottom-right-radius:3px;
                color:#343434;
        }
        """

        self.active_style_sheet = """
        QWidget {
                border:1px solid #E2E2E2;
                background-color:#2563EB;
                border-top-right-radius:3px;
                border-bottom-right-radius:3px;
                color:white;
        }
        """

        self.central_widget = QWidget()
        self.central_widget.setLayout(layout)

        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self.central_widget)

        self.setLayout(main_layout)
        self.setFixedSize(QSize(110, 35))
        self.set_active_widget_style()

    def set_de_active_widget_style(self):
        self.central_widget.setStyleSheet(self.de_active_style_sheet)

        self.icon_label.setStyleSheet("""
        QLabel {
            border:0;
            background-color:transparent;
        }
        """)

        font = self.button.font()
        # font.setPointSizeF(12)
        font.setWeight(QFont.Weight.Normal)
        self.button.setFont(font)
        self.button.setStyleSheet("""
            QPushButton {
                border:0;
                border-radius:0;
                background-color:transparent;
                color:#343434;
            }
        """)

        icon_pixmap = QPixmap(":resources/icons/calendar.svg")
        self.icon_label.setPixmap(icon_pixmap)

    def set_active_widget_style(self):
        self.central_widget.setStyleSheet(self.active_style_sheet)

        self.icon_label.setStyleSheet("""
        QLabel {
            border:0;
            background-color:transparent;
        }
        """)

        font = self.button.font()
        # font.setPointSizeF(12)
        font.setWeight(QFont.Weight.Bold)
        self.button.setFont(font)
        self.button.setStyleSheet("""
                 QPushButton {
                     border:0;
                     border-radius:0;
                     background-color:transparent;
                 }
             """)
        icon_pixmap = QPixmap(":resources/icons/white_calendar.svg")
        self.icon_label.setPixmap(icon_pixmap)
