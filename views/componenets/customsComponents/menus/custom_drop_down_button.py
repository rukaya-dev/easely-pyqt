from PyQt6.QtWidgets import QPushButton, QStylePainter, QStyleOptionButton, QStyle
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize, Qt


class CustomAddButton(QPushButton):

    def __init__(self, icon_path, icon_size, text, object_name, style, btn_width, btn_height, alignment, parent=None):
        super().__init__(text, parent)

        self.setIcon(QIcon(icon_path))
        self.setIconSize(icon_size)
        self.setFixedSize(QSize(btn_width, btn_height))
        self.setText(text)
        self.setObjectName(object_name)
        self.m_spacing = 0.0
        self.setStyleSheet(style)
        self.alignment = alignment

    def spaceRatio(self):
        return self.m_spacing

    def setSpaceRatio(self, ratio):
        self.m_spacing = ratio
        self.update()

    def minimumSizeHint(self):
        sz = super().minimumSizeHint()
        offset = self.iconSize().width() * self.m_spacing
        return QSize(int(sz.width() + offset), int(sz.height()))

    def paintEvent(self, event):
        painter = QStylePainter(self)
        option = QStyleOptionButton()
        option.initFrom(self)
        painter.drawControl(QStyle.ControlElement.CE_PushButton, option)

        icon = self.icon().pixmap(self.iconSize())
        rect = self.rect()

        # Calculate the width required by the text
        text_width = painter.fontMetrics().maxWidth()

        # Calculate the total width required by both the icon and the text (including spacing)
        total_width = icon.width() + int(self.m_spacing * self.width()) + text_width

        # Calculate the starting position for the icon
        icon_start = (rect.width() - total_width) // 2
        painter.drawPixmap(icon_start, (rect.height() - icon.height()) // 2, icon)

        # Adjust the starting point of the text based on the icon's position + icon width + spacing
        text_start = icon_start + icon.width() + int(self.m_spacing * self.width())
        painter.drawText(text_start, 0, rect.width() - text_start, rect.height(), Qt.AlignmentFlag.AlignVCenter,
                         self.text())

    def sizeHint(self):
        sz = super().sizeHint()
        offset = self.iconSize().width() * self.m_spacing
        return QSize(int(sz.width() + offset), int(sz.height()))
