from PyQt6.QtCore import QSize
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QIcon, QAction
from PyQt6.QtWidgets import QPushButton, QMenu, QWidget, QHBoxLayout

from stylesheets.common_stylesheet import menu_stylesheet
from views.componenets.customsComponents.menus.drop_down_menu_component import CustomDropDownMenuComponent


class CustomViewOptionMenu(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.menu_button = QPushButton()

        self.menu_button.setStyleSheet("""
        QPushButton {
            border:0;
            background-color:transparent;
        }
        """)

        icon_pixmap = QPixmap(":resources/icons/vertical_menu.svg")
        icon = QIcon(icon_pixmap)

        self.menu_button.setIcon(icon)
        self.menu_button.setIconSize(QSize(20, 20))
        self.menu_button.setFixedSize(QSize(25, 25))

        self.menu_widget = QMenu()

        self.view_action = QAction(QIcon(':/resources/icons/eye.svg'), "View")
        self.menu_widget.addAction(self.view_action)

        self.menu_widget.setContentsMargins(0, 4, 0, 4)

        font = self.font()
        font.setPointSize(11)
        font.setWeight(font.Weight.Normal)
        self.setFont(font)

        self.setStyleSheet(menu_stylesheet)
        self.menu_widget.setFixedWidth(200)

        self.custom_drop_down_menu = CustomDropDownMenuComponent(menu_button=self.menu_button,
                                                                 menu_pos="left",
                                                                 menu_widget=self.menu_widget)

        filter_btn_layout = QHBoxLayout(self)
        filter_btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        filter_btn_layout.setContentsMargins(0, 0, 0, 0)
        filter_btn_layout.setSpacing(0)
        filter_btn_layout.addWidget(self.custom_drop_down_menu)

        self.setLayout(filter_btn_layout)
