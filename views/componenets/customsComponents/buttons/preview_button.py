import os

from PyQt6.QtCore import QSize, pyqtSlot
from PyQt6.QtGui import QMovie, QIcon
from PyQt6.QtWidgets import QPushButton


class PreviewButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setGif()
        self.setStyleSheet("""
                QPushButton {
                    border:0;
                    border-radius:3px;
                    background-color:#EDEDEE;
                    color:#717171;
                }
                """)
        self.setFixedSize(QSize(100, 34))

        font = self.font()
        font.setPointSize(11)
        font.setWeight(font.Weight.Medium)
        self.setFont(font)

        self.eye_icon = QIcon(":resources/icons/eye.svg")
        self.setIcon(self.eye_icon)
        self.setIconSize(QSize(20, 20))
        self.setContentsMargins(5, 5, 5, 5)

        self.setText("Preview")

    @pyqtSlot()
    def start(self):
        self.setText("")
        self.setDisabled(True)
        if hasattr(self, "_movie"):
            self._movie.start()

    @pyqtSlot()
    def stop(self):
        self.setText("Preview")
        if hasattr(self, "_movie"):
            self.setIcon(QIcon(":resources/icons/eye.svg"))
            self._movie.stop()
            self.setDisabled(False)

    def setGif(self):
        if not hasattr(self, "_movie"):
            self._movie = QMovie(self)
            self._movie.setScaledSize(QSize(30, 30))
            self._movie.setFileName(":resources/images/loading.gif")
            self._movie.frameChanged.connect(self.on_frameChanged)
            if self._movie.loopCount() != -1:
                self._movie.finished.connect(self.start)
        self.stop()

    @pyqtSlot(int)
    def on_frameChanged(self, frame_umber):
        self.setIcon(QIcon(self._movie.currentPixmap()))
