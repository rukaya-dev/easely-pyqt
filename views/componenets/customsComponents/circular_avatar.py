from PyQt6.QtGui import QPixmap, QImage, QPainter, QBrush, QWindow, QPen, QColor
from PyQt6.QtCore import Qt, QRect, QRectF


def mask_image(imgdata, img_type='jpg', size=64, border=False, border_color="black"):
    if not imgdata:
        pixmap = QPixmap(":resources/images/placeholder.jpg")
        image = pixmap.toImage()
    else:

        image = QImage.fromData(imgdata, img_type)

    # Convert image to 32-bit ARGB (adds an alpha channel ie transparency factor):
    image.convertToFormat(QImage.Format.Format_ARGB32)

    # Crop image to a square:
    imgsize = min(image.width(), image.height())
    rect = QRect(
        int((image.width() - imgsize) / 2),
        int((image.height() - imgsize) / 2),
        imgsize,
        imgsize,
    )
    image = image.copy(rect)

    # Create the output image with the same dimensions and an alpha channel and make it completely transparent:
    out_img = QImage(imgsize, imgsize, QImage.Format.Format_ARGB32)
    out_img.fill(Qt.GlobalColor.transparent)

    # Create a texture brush and paint a circle with the original image onto the output image:
    brush = QBrush(image)

    # Paint the output image
    painter = QPainter(out_img)
    painter.setBrush(brush)

    # Draw the ellipse (circle)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(0, 0, imgsize, imgsize)

    # Draw the border if requested
    if border:
        pen = QPen(QColor(border_color))
        pen.setWidth(15)  # Adjust the width as needed
        pen.setCosmetic(True)  # Make the pen width constant regardless of scale
        painter.setPen(pen)
        painter.drawEllipse(pen.width() // 2, pen.width() // 2, imgsize - pen.width(), imgsize - pen.width())

    # Close the painter event
    painter.end()

    # Convert the image to a pixmap and rescale it.
    pr = QWindow().devicePixelRatio()
    pm = QPixmap.fromImage(out_img)
    pm.setDevicePixelRatio(pr)
    size *= pr
    pm = pm.scaled(int(size), int(size), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

    # Return back the pixmap data
    return pm
