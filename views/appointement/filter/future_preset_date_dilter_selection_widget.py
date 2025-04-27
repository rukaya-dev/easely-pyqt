from PyQt6.QtCore import QSize, Qt, pyqtSignal
from PyQt6.QtGui import QActionGroup, QAction, QPixmap
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QMenu, QPushButton, QHBoxLayout, QLabel

from stylesheets.common_stylesheet import menu_stylesheet
from views.componenets.customsComponents.menus.drop_down_menu_component import CustomDropDownMenuComponent


class FuturePresetDateFilterSelectionWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.current_filter = None

        self.menu = PresetDateFilterMenuComponent(self)

        self.preset_date_menu_button = PresetCustomDateMenuButton(self)

        self.drop_down_menu = CustomDropDownMenuComponent(menu_button=self.preset_date_menu_button,
                                                          menu_pos="bottom-right",
                                                          menu_widget=self.menu)
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.layout.addWidget(self.drop_down_menu)
        self.setLayout(self.layout)

    def get_current_filter(self):
        return self.current_filter

    def set_current_filter(self, new_filter_value):
        self.current_filter = new_filter_value


# Menu
class PresetDateFilterMenuComponent(QMenu):
    presetFilterActionTriggered = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.parent = parent

        next_24_hours_text = "Next 24 hours"

        self.Next_24_hours = QAction(next_24_hours_text, self)
        self.Next_24_hours.setData({"id": "next_24_hours", "name": next_24_hours_text, "type": "preset_filter"})
        self.addAction(self.Next_24_hours)

        self.Next_7_days = QAction("Next 7 days", self)
        self.Next_7_days.setData({"id": "next_7_days", "name": "Next 7 days", "type": "preset_filter"})
        self.addAction(self.Next_7_days)

        self.Next_14_days = QAction("Next 14 days", self)
        self.Next_14_days.setData({"id": "next_14_days", "name": "Next 14 days", "type": "preset_filter"})
        self.addAction(self.Next_14_days)

        self.Next_30_days = QAction("Next 30 days", self)
        self.Next_30_days.setData({"id": "next_30_days", "name": "Next 30 days", "type": "preset_filter"})
        self.addAction(self.Next_30_days)

        self.actions_group = QActionGroup(self)
        for action in self.actions():
            action.setCheckable(True)
            self.actions_group.addAction(action)

        self.actions_group.setExclusive(True)
        self.actions_group.triggered.connect(self.update_current_checked_action)

        font = self.font()
        font.setPointSize(11)
        font.setWeight(font.Weight.Normal)
        self.setFont(font)

        self.setStyleSheet(menu_stylesheet)
        self.setContentsMargins(0, 0, 0, 0)
        self.setFixedSize(QSize(227, 150))

    def update_current_checked_action(self, action):
        action.setChecked(True)
        action_data = action.data()
        self.parent.preset_date_menu_button.button.setText(action_data["name"])
        self.parent.set_current_filter(action_data)
        self.presetFilterActionTriggered.emit()


# Button
class PresetCustomDateMenuButton(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.icon_label = QLabel(self)
        self.icon_label.setFixedSize(QSize(15, 15))

        self.button = QPushButton(self)
        self.button.setObjectName("preset_date_menu_button")
        self.button.setFixedWidth(100)

        self.button.setText("Next 24 hours")

        font = self.button.font()
        font.setPointSize(10)
        font.setWeight(font.Weight.Normal)
        self.button.setFont(font)

        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(0)

        layout.addWidget(self.icon_label)
        layout.addWidget(self.button)

        self.de_active_style_sheet = """
            QWidget {
                border:1px solid #E2E2E2;
                border-radius:3px;
                border-top-right-radius:0px;
                border-bottom-right-radius:0px;
                background-color:white;
                border-right:0px;
            }
            QWidget::hover {
                background-color:#ededed;
            }
            """
        self.active_style_sheet = """
            QWidget {
                border:1px solid #E2E2E2;
                border-radius:3px;
                border-top-right-radius:0px;
                border-bottom-right-radius:0px;
                background-color:#2563EB;
                border-right:0px;
                color:white;
            }
            QWidget::hover {
                color:#ededed;
            }
            """

        self.central_widget = QWidget()
        self.central_widget.setLayout(layout)
        self.central_widget.setStyleSheet(self.de_active_style_sheet)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self.central_widget)

        self.setLayout(main_layout)
        self.setFixedSize(QSize(135, 35))
        self.set_de_active_widget_style()

    def set_active_widget_style(self):
        self.central_widget.setStyleSheet(self.active_style_sheet)

        self.icon_label.setStyleSheet("""
            QLabel {
                border:0;
                background-color:transparent;
            }
            """)

        self.button.setStyleSheet("""
        QPushButton {
            border:0;
            color:white;
            background-color:transparent;
        }
        """)

        icon_pixmap = QPixmap(":resources/icons/white_clock.svg")
        self.icon_label.setPixmap(icon_pixmap)

    def set_de_active_widget_style(self):

        self.central_widget.setStyleSheet(self.de_active_style_sheet)

        self.icon_label.setStyleSheet("""
            QLabel {
                border:0;
                background-color:transparent;
            }
            """)
        self.button.setStyleSheet("""
        QPushButton {
            border:0;
            color:#343434;
            background-color:transparent;
        }
        """)

        icon_pixmap = QPixmap(":resources/icons/clock.svg")
        self.icon_label.setPixmap(icon_pixmap)
