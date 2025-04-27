from datetime import datetime, date

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import QSize, QRect, QPoint, QDate
from PyQt6.QtGui import QIcon, QFont, QColor, QImage, QPixmap
from PyQt6.QtWidgets import QCalendarWidget, QLabel, QPushButton

from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout

from views.componenets.customsComponents.buttons.button_with_loader import ButtonWithLoader
from views.componenets.customsComponents.custom_checkbox import CustomCheckBox
from views.appointement.filter.future_preset_date_dilter_selection_widget import \
    FuturePresetDateFilterSelectionWidget
from views.componenets.customsComponents.menus.drop_down_menu_component import CustomDropDownMenuComponent


class FutureDateFilterWidgetWithCheckBox(QWidget):
    def __init__(self, name, parent=None):
        super().__init__(parent)

        self.filter_data = None

        central_widget = QWidget()
        central_widget.setFixedWidth(300)

        self.check_box = CustomCheckBox(name)
        self.check_box.stateChanged.connect(self.handle_checkbox_state_changed)

        self.preset_date_filter_selection_widget = FuturePresetDateFilterSelectionWidget(self)

        self.preset_date_filter_selection_widget.menu.presetFilterActionTriggered.connect(
            self.handle_preset_filter_style)

        self.custom_date_range_selection_widget = CustomDateFilterSelectionWidget(self)
        self.custom_date_range_selection_widget.selection_widget.apply_btn.clicked.connect(
            self.handle_custom_filter_style)

        self.preset_date_filter_selection_widget.setDisabled(True)
        self.custom_date_range_selection_widget.setDisabled(True)

        self.main_layout = QHBoxLayout()
        self.main_layout.setContentsMargins(27, 0, 10, 10)
        self.main_layout.setSpacing(0)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        self.main_layout.addWidget(self.preset_date_filter_selection_widget)
        self.main_layout.addWidget(self.custom_date_range_selection_widget)

        central_widget.setLayout(self.main_layout)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        layout.addWidget(self.check_box)
        layout.addWidget(central_widget)
        self.setLayout(layout)

        self.setFixedWidth(300)

    @pyqtSlot(int)
    def handle_checkbox_state_changed(self, state):
        if state == 2:
            self.preset_date_filter_selection_widget.setDisabled(False)
            self.custom_date_range_selection_widget.setDisabled(False)
        else:
            self.preset_date_filter_selection_widget.setDisabled(True)
            self.custom_date_range_selection_widget.setDisabled(True)

    @pyqtSlot()
    def handle_preset_filter_style(self):

        self.preset_date_filter_selection_widget.preset_date_menu_button.set_active_widget_style()

        self.custom_date_range_selection_widget.custom_date_menu_button.set_de_active_widget_style()

    def handle_custom_filter_style(self):
        self.preset_date_filter_selection_widget.preset_date_menu_button.set_de_active_widget_style()
        if self.preset_date_filter_selection_widget.menu.actions_group.checkedAction():
            self.preset_date_filter_selection_widget.menu.actions_group.checkedAction().setChecked(False)

        self.custom_date_range_selection_widget.custom_date_menu_button.set_active_widget_style()


QSS = '''
QCalendarWidget QMenu {
        width: 150px;
        left: 20px;
        color: #2C2D33;
        font-size: 16px;
        background-color: #F6F8FA;
}

QCalendarWidget QSpinBox { 
        width: 50px;
        font-size: 18px;
        font-weight:bold;
        color: #4B4E58; 
        background-color: white; 
        selection-background-color:white ;
        selection-color: #2C2D33;
}
QCalendarWidget QSpinBox::up-button { subcontrol-origin: border;  subcontrol-position: top right;  width:16px; border:0; }
QCalendarWidget QSpinBox::down-button {subcontrol-origin: border; subcontrol-position: bottom right;  width:16px; border:0;}
QCalendarWidget QSpinBox::up-arrow { width:20px;  height:20px; image: url(:/resources/icons/spin_up.svg); }
QCalendarWidget QSpinBox::down-arrow { width:20px;  height:20px; image: url(:/resources/icons/spin_down.svg);}

QCalendarWidget QAbstractItemView
{ 
        selection-background-color: transparent;
        border:0;
}

QCalendarWidget QTableView
{
    border-width:0px;
    background-color:white;
    color:#2C2D33;
    font-size:14px;
    selection-background-color: white;
}
#qt_calendar_prevmonth {
     background-color:transparent;
     margin-left:20px;
}

#qt_calendar_prevmonth:hover {
     border:0;
}

#qt_calendar_nextmonth{
     background:#2563EB;
     margin-right:20px;
}

#qt_calendar_nextmonth:hover{
     border:0;
}

#qt_calendar_navigationbar {
    background: #2563EB;
    border:0;
    border-radius:7px;
    font-size:14px;
}
QCalendarWidget QToolButton#qt_calendar_monthbutton {
    /* General button properties */
    background-color: #2563EB;
    border: 0;
    padding: 5px;
    color:white;
    margin-right: 10px;  /* Adjust as needed */

}

QCalendarWidget QToolButton#qt_calendar_monthbutton:hover {
    /* Styling when button is hovered */
    background-color: #2563EB;
}

QCalendarWidget QToolButton#qt_calendar_monthbutton:pressed {
    /* Styling when button is pressed */
    background-color: #2563EB;
}

QCalendarWidget QToolButton#qt_calendar_monthbutton::menu-indicator {
    /* Hide the menu indicator (down arrow) if desired */
    image: none;
}
QCalendarWidget QToolButton#qt_calendar_yearbutton {
    background-color: #2563EB;
    border: 0;
    padding: 5px;
    color:white;
    margin-left: 10px;  /* Adjust as needed */
}

QCalendarWidget QToolButton#qt_calendar_yearbutton:hover {
    background-color:  #2563EB;
}

QCalendarWidget QToolButton#qt_calendar_yearbutton:pressed {
        background-color:  #2563EB;
}

QCalendarWidget QToolButton#qt_calendar_yearbutton::menu-indicator {
    image: none;
}
'''

Enabled_date_style = '''
    QDateEdit {
        border:1px solid #8D8D8D;
        color:#112C41;
        background-color:white;
        border-radius:3px;
    }
    QDateEdit::drop-down {
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width: 15px;
        padding-right: 5px;
        border: none;
        image: url(:/resources/icons/calendar.svg);
    }
'''

Disabled_date_style = '''
    QDateEdit {
        border:1px solid #CACACA;
        border-radius:3px;
        color:#2C2D33;
        background-color:white;
    }
    QDateEdit::drop-down {
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width: 15px;
        padding-right: 5px;
        border: none;
        image: url(:/resources/icons/calendar.svg);
    }
'''


class CustomDateFilterSelectionWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName("custom_date_filter_selection_widget")

        self.selection_widget = self.CustomDateRangeSelection(self)
        self.selection_widget.apply_btn.clicked.connect(self.update_custom_filter_btn_text)

        self.custom_date_menu_button = self.CustomDateMenuButton(self)

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
            font.setWeight(font.Weight.Normal)
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
            self.setFixedSize(QSize(115, 35))
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

    class CustomDateRangeSelection(QWidget):
        def __init__(self, parent=None):
            super().__init__(parent)

            self.parent = parent

            self.custom_date_calendar = self.FutureCustomCalendarWidget()

            self.date_range_h_layout = QHBoxLayout()
            self.date_range_h_layout.setContentsMargins(20, 20, 20, 20)
            self.date_range_h_layout.setSpacing(30)
            self.date_range_h_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

            self.date_range_h_layout.addWidget(self.custom_date_calendar)

            self.apply_btn = ButtonWithLoader(text="Apply", size=QSize(95, 34))

            apply_btn_layout = QHBoxLayout()
            apply_btn_layout.setContentsMargins(20, 20, 20, 20)
            apply_btn_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
            apply_btn_layout.addWidget(self.apply_btn)

            layout = QVBoxLayout()
            layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(10)

            layout.addLayout(self.date_range_h_layout, Qt.AlignmentFlag.AlignLeft)
            layout.addLayout(apply_btn_layout)
            self.setLayout(layout)

        class FutureCustomCalendarWidget(QCalendarWidget):
            def __init__(self, parent=None):
                super().__init__(parent)

                self.setFixedHeight(350)
                self.setFixedWidth(450)

                self.prev_button = self.findChild(QtWidgets.QToolButton, "qt_calendar_prevmonth")
                self.next_button = self.findChild(QtWidgets.QToolButton, "qt_calendar_nextmonth")

                # Create QIcon instances for your icons
                prev_icon = QIcon(":resources/icons/arrow_back.svg")
                next_icon = QIcon(":resources/icons/arrow_forward.svg")

                # Set the icons to the buttons
                self.prev_button.setIcon(prev_icon)
                self.next_button.setIcon(next_icon)

                navigation = self.findChild(QtWidgets.QWidget, "qt_calendar_navigationbar")
                navigation.setFixedHeight(45)
                navigation.setContentsMargins(10, 10, 10, 10)

                for btn in (self.prev_button, self.next_button):
                    btn.setIconSize(QtCore.QSize(15, 15))

                for d in (
                        Qt.DayOfWeek.Saturday, Qt.DayOfWeek.Sunday, Qt.DayOfWeek.Monday,
                        Qt.DayOfWeek.Tuesday, Qt.DayOfWeek.Wednesday, Qt.DayOfWeek.Thursday, Qt.DayOfWeek.Friday):
                    fmt = self.weekdayTextFormat(d)
                    fmt.setFontPointSize(14)
                    fmt.setForeground(QColor('#000'))
                    fmt.setBackground(QColor('white'))
                    fmt.setFontWeight(QFont.Weight.Medium)
                    self.setWeekdayTextFormat(d, fmt)

                self.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)

                self.setStyleSheet(QSS)
                self.setHorizontalHeaderFormat(QCalendarWidget.HorizontalHeaderFormat.ShortDayNames)
                self.setDateRange(QDate.currentDate(), QDate.currentDate().addYears(1))

            def paintCell(self, painter, rect, date, index=0):
                rect.adjust(0, 5, 0, -5)  # Add padding between rows by adjusting the rect
                if date == self.selectedDate():
                    painter.save()
                    r = QRect(QPoint(), QSize(min(rect.width(), rect.height()), min(rect.width(), rect.height())))
                    r.moveCenter(rect.center())
                    img = QImage(":resources/icons/selected_date.svg")
                    scaled_img = img.scaled(34, 34, Qt.AspectRatioMode.KeepAspectRatio,
                                            Qt.TransformationMode.SmoothTransformation)
                    painter.drawImage(r, scaled_img)
                    painter.setPen(QtGui.QPen(QtGui.QColor("white")))

                    painter.drawText(rect, QtCore.Qt.AlignmentFlag.AlignCenter, str(date.day()))
                    painter.restore()
                elif date.month() != self.monthShown():
                    pass

                else:
                    painter.fillRect(rect, QColor(255, 255, 255, 100))  # Light grey color
                    painter.setPen(QColor('#2C2D33'))  # Dark grey text color
                    painter.drawText(rect, QtCore.Qt.AlignmentFlag.AlignCenter, str(date.day()))
