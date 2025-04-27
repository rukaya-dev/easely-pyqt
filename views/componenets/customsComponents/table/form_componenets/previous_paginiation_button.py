import os

from PyQt6 import QtCore, QtGui
from PyQt6.QtCore import QSize
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QPushButton


class PreviousPaginationButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setGif()
        self.setStyleSheet("""
                QPushButton {
                    border:1px solid #C3C3C3;
                    border-radius:5px;
                    font-size:13pt;
                    background-color:#F6F8FA;
                    color:#F5F5F5;
                }
                """)
        self.setFixedSize(QSize(35, 30))

        self.next_icon = QIcon(":resources/icons/pagination_arrow_back.svg")
        self.setIcon(self.next_icon)
        self.setIconSize(QSize(24, 24))

    @QtCore.pyqtSlot()
    def start(self):
        self.setText("")
        self.setDisabled(True)
        if hasattr(self, "_movie"):
            self._movie.start()

    @QtCore.pyqtSlot()
    def stop(self):
        if hasattr(self, "_movie"):
            self.setIcon(QIcon(":resources/icons/pagination_arrow_back.svg"))
            self._movie.stop()
            self.setDisabled(False)

    def setGif(self):
        if not hasattr(self, "_movie"):
            self._movie = QtGui.QMovie(self)
            self._movie.setScaledSize(QSize(30, 30))
            self._movie.setFileName(":resources/images/loading.gif")
            self._movie.frameChanged.connect(self.on_frameChanged)
            if self._movie.loopCount() != -1:
                self._movie.finished.connect(self.start)
        self.stop()

    @QtCore.pyqtSlot(int)
    def on_frameChanged(self, frame_umber):
        self.setIcon(QtGui.QIcon(self._movie.currentPixmap()))
