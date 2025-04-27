import os

from PyQt6 import QtCore, QtGui
from PyQt6.QtWidgets import QPushButton


class ButtonWithLoader(QPushButton):
    def __init__(self, text, size, parent=None):
        super().__init__(parent)

        self.size = size
        self.textd = text
        self.setText(text)

        font = self.font()
        font.setPointSize(12)
        font.setWeight(font.Weight.Normal)
        self.setFont(font)

        self.setGif()
        self.setFixedSize(size)
        self.setStyleSheet("""
            QPushButton {
                border:0;
                border-radius:3px;
                background-color:#2563EB;
                color:#F5F5F5;
            }
            QPushButton:pressed {
                border:0;
                border-radius:3px;
                font-size:13pt;
                color:#F5F5F5;
                padding-top: 2px;
                padding-left: 2px;
            }
        
        """)

    @QtCore.pyqtSlot()
    def start(self):
        self.setText("Loading")
        self.setDisabled(True)
        if hasattr(self, "_movie"):
            self._movie.start()

    @QtCore.pyqtSlot()
    def stop(self):
        if hasattr(self, "_movie"):
            self._movie.stop()
            self.setIcon(QtGui.QIcon())
            self.setDisabled(False)
            self.setText(self.textd)

    def setGif(self):
        if not hasattr(self, "_movie"):
            self._movie = QtGui.QMovie(self)
            self._movie.setFileName(":resources/images/loading.gif")
            self._movie.frameChanged.connect(self.on_frameChanged)
            if self._movie.loopCount() != -1:
                self._movie.finished.connect(self.start)
        self.stop()

    @QtCore.pyqtSlot(int)
    def on_frameChanged(self, frame_umber):
        self.setIcon(QtGui.QIcon(self._movie.currentPixmap()))
