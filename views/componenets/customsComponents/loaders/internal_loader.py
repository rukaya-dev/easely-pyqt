import os

from PyQt6 import QtCore, QtGui
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QLabel, QSizePolicy


class InternalLoader(QLabel):
    def __init__(self, height, parent=None):
        super().__init__(parent)

        self.height = height
        self.is_spinning = False  # Add an attribute to track the running state

        self.setGif()
        self.setFixedSize(self.height, self.height)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.setStyleSheet("""
        QLabel {
            border:0;
            border-radius:0;
            background-color:transparent;
            color:black;
        }

        """)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)

        self.raise_()

    @QtCore.pyqtSlot()
    def start(self):
        self.setText("")
        self.setDisabled(True)
        self.is_spinning = True
        if hasattr(self, "_movie"):
            self._movie.start()

    @QtCore.pyqtSlot()
    def stop(self):
        if hasattr(self, "_movie"):
            self._movie.stop()
            self.is_spinning = False
            self.setPixmap(QPixmap())
            self.setDisabled(False)

    def setGif(self):
        if not hasattr(self, "_movie"):
            self._movie = QtGui.QMovie(self)
            self._movie.setScaledSize(QSize(self.height, self.height))
            self._movie.setFileName(":resources/images/loading.gif")
            self._movie.frameChanged.connect(self.on_frameChanged)
            if self._movie.loopCount() != -1:
                self._movie.finished.connect(self.start)
        self.stop()

    @QtCore.pyqtSlot(int)
    def on_frameChanged(self, frame_umber):
        self.setPixmap(QPixmap(self._movie.currentPixmap()))

    def isSpinning(self):
        return self.is_spinning
