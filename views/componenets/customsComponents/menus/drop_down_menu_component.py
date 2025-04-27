from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PyQt6.QtCore import Qt, QRect, QPoint


class DropDownMenu(QWidget):
    def __init__(self, widget):
        super().__init__()

        self.setWindowFlags(Qt.WindowType.Popup)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(widget)


class CustomDropDownMenuComponent(QWidget):
    def __init__(self, menu_button, menu_pos, menu_widget):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.custom_date_menu_button = menu_button

        if isinstance(self.custom_date_menu_button, QPushButton):
            self.custom_date_menu_button.clicked.connect(lambda: self.toggle_dropdown(float_direction=menu_pos))
        else:
            self.custom_date_menu_button.button.clicked.connect(lambda: self.toggle_dropdown(float_direction=menu_pos))

        layout.addWidget(self.custom_date_menu_button)

        self.menu = DropDownMenu(menu_widget)

    def toggle_dropdown(self, position=None, float_direction="bottom-center"):
        menu_height = self.menu.sizeHint().height()
        menu_width = self.menu.sizeHint().width()
        main_window_bottom = 768
        button = self.custom_date_menu_button
        # if position provided
        if position:
            button_geometry = button.geometry()
            position = button.mapToGlobal(QPoint(0, button_geometry.height()))

            if position.y() + menu_height > main_window_bottom:
                position.setY(
                    position.y() - menu_height - button.geometry().height())  # adjust upwards by the menu height and the button height

        # if no position provided
        button_pos = button.mapToGlobal(QPoint(0, 0))  # Top-left corner in global coordinates

        # Calculate center position of the button
        button_geometry = button.geometry()
        center_x = int(button_geometry.x() + button.width() / 2)
        center_y = int(button_geometry.y() + button.height() / 2)

        # Convert to global coordinates if needed
        center_global = button.mapToGlobal(QPoint(center_x, center_y))
        # Default Menu pos is bottom-center
        menu_pos = center_global - QPoint(int(menu_width / 2), -button.height())

        if float_direction:
            if float_direction == "right":
                menu_pos = button_pos + QPoint(button.width(), 0)
            elif float_direction == "left":
                menu_pos = button_pos - QPoint(menu_width, 0)
            elif float_direction == "top-right":
                menu_pos = button_pos + QPoint(button.width(), -menu_height)
            elif float_direction == "top-left":
                menu_pos = button_pos - QPoint(menu_width, menu_height)
            elif float_direction == "bottom-right":
                menu_pos = button_pos + QPoint(0, button.height())
            elif float_direction == "bottom-left":
                menu_pos = button_pos - QPoint(menu_width, -button.height())
            elif float_direction == "bottom-center":
                # Calculate center position of the button
                button_geometry = button.geometry()
                center_x = int(button_geometry.x() + button.width() / 2)
                center_y = int(button_geometry.y() + button.height() / 2)

                # Convert to global coordinates if needed
                center_global = button.mapToGlobal(QPoint(center_x, center_y))
                menu_pos = center_global - QPoint(int(menu_width / 2), -button.height())

        if self.menu.isVisible():
            self.menu.hide()
        else:
            if position:
                self.menu.setGeometry(
                    QRect(position.x() - 0 + 0,
                          button.geometry().width(),
                          menu_height))
            else:
                self.menu.move(menu_pos)  # Move the menu to the calculated position

            self.menu.show()
