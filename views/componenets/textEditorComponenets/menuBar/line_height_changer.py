from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import QVBoxLayout, QMenu, QWidget, QPushButton
from PyQt6.QtGui import QAction, QActionGroup, QPixmap, QIcon
from views.componenets.customsComponents.menus.drop_down_menu_component import CustomDropDownMenuComponent


class LineHeightChangerComponent(QMenu):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowFlags(Qt.WindowType.Widget)

        self.single_action = QAction("Single", self)
        self.addAction(self.single_action)

        self.one_point_15_action = QAction("1.15", self)
        self.addAction(self.one_point_15_action)

        self.one_point_5_action = QAction("1.5", self)
        self.addAction(self.one_point_5_action)

        self.double_action = QAction("Double", self)
        self.addAction(self.double_action)

        self.addAction(self.single_action)
        self.addAction(self.one_point_15_action)
        self.addAction(self.one_point_5_action)
        self.addAction(self.double_action)

        self.setStyleSheet("""
                         QMenu {
                             border: 0;
                             padding:0;
                         }
                         QMenu::item {
                             padding-bottom:10px;
                             padding-top:10px;
                             padding-left:30px;
                         }
                         QMenu::icon {
                             padding-left: 30px;  /* Add padding to the left of the icon */
                         }
                         QMenu::item:selected {
                             background-color: #0082FC; /* blue */
                         }
                        QMenu::separator {
                             height: 1px;
                             background: #A1AEB4; /* Gray color */

                         }
                         
                        QMenu::indicator {
                            padding-left:20px;
                        } 
                     """)
        self.setContentsMargins(0, 0, 0, 0)
        self.setFixedSize(QSize(200, 170))

        actions_group = QActionGroup(self)
        for action in self.actions():
            action.setCheckable(True)
            actions_group.addAction(action)

        actions_group.setExclusive(True)
        actions_group.triggered.connect(self.update_current_checked_action)

    def update_current_checked_action(self, action):
        action.setChecked(True)


class LineHeightChanger(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.menu = LineHeightChangerComponent(parent=self)

        self.filter_toggle_menu_button = QPushButton()

        self.filter_toggle_menu_button.setStyleSheet("""
            QPushButton {
                border:0;
                background-color:transparent;
            }
        """)

        icon_pixmap = QPixmap(":resources/icons/line_height.svg")
        icon = QIcon(icon_pixmap)

        self.filter_toggle_menu_button.setIcon(icon)
        self.filter_toggle_menu_button.setIconSize(QSize(22, 22))
        self.filter_toggle_menu_button.setFixedSize(QSize(50, 38))

        self.drop_down_menu = CustomDropDownMenuComponent(menu_button=self.filter_toggle_menu_button,
                                                          menu_pos="right",
                                                          menu_widget=self.menu
                                                          )
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.drop_down_menu)
        self.setLayout(self.layout)
