from datetime import datetime

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import QSize, Qt, QRect, QPoint, QDate
from PyQt6.QtGui import QIcon, QFont, QColor, QImage
from PyQt6.QtWidgets import QCalendarWidget, QDateEdit, QAbstractSpinBox, QDateTimeEdit

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


class CustomDateWidget(QDateEdit):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setDate(QtCore.QDate.currentDate())
        self.setDisplayFormat("ddd, MMMM dd, yyyy")
        self.setCalendarPopup(True)
        self.setFixedSize(QSize(160, 36))
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.setStyleSheet(Disabled_date_style)
        self.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)

        self.custom_calendar = CustomCalendarWidget()
        self.setCalendarWidget(self.custom_calendar)


class CustomCalendarWidget(QCalendarWidget):
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
            fmt.setFontPointSize(11)
            fmt.setForeground(QColor('#000'))
            fmt.setBackground(QColor('white'))
            fmt.setFontWeight(QFont.Weight.Medium)
            self.setWeekdayTextFormat(d, fmt)

        self.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)

        self.setStyleSheet(QSS)
        self.setHorizontalHeaderFormat(QCalendarWidget.HorizontalHeaderFormat.ShortDayNames)
        # self.setDateRange(QDate.currentDate(), QDate.currentDate().addYears(1))

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

        else:
            painter.fillRect(rect, QColor(255, 255, 255, 100))  # Light grey color
            painter.setPen(QColor('#2C2D33'))  # Dark grey text color
            painter.drawText(rect, QtCore.Qt.AlignmentFlag.AlignCenter, str(date.day()))
