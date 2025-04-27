from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QVariantAnimation, pyqtProperty, QEasingCurve
from PyQt6.QtGui import QColor, QPainter


class PlaceholderLoadingAnimation(QWidget):
    def __init__(self, start_color =QColor("white"), end_color =QColor("gray"), duration=1000):
        super().__init__()
        self._start_color  = start_color 
        self._end_color  = end_color 
        self._duration = duration
        self._color = start_color 
        self.setupAnimation()

    def setupAnimation(self):
        self.animation = QVariantAnimation(self)
        self.animation.setDuration(self._duration)
        self.animation.setStartValue(self._start_color )
        self.animation.setEndValue(self._end_color )
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.animation.setDirection(QVariantAnimation.Forward)
        self.animation.finished.connect(self.toggleAnimationDirection)
        self.animation.valueChanged.connect(self.updateColor)
        self.animation.start()

    def toggleAnimationDirection(self):
        if self.animation.direction() == QVariantAnimation.Forward:
            self.animation.setDirection(QVariantAnimation.Backward)
        else:
            self.animation.setDirection(QVariantAnimation.Forward)
        self.animation.start()

    def updateColor(self, color):
        self._color = color
        self.update()

    @pyqtProperty(QColor)
    def color(self):
        return self._color


    def setColors(self, start_color , end_color ):
        self._start_color  = start_color 
        self._end_color  = end_color 
        self.setupAnimation()

    def setDuration(self, duration):
        self._duration = duration
        self.setupAnimation()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), self._color)
