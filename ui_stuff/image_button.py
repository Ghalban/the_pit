import os
from PySide2 import QtCore, QtWidgets, QtGui


class ImageButton(QtWidgets.QPushButton):
    """
    Creates an ImageButton object that is a QPushButton with an image icon inside.
    Size of icon is determined by size of image.

    Example:
        Place an icon and connect it to corresponding controller with maya cmds ::

            def add_img_btn(self, img, x, y):
                btn = ImageButton(img, x, y)
                btn.setParent(self.ctrl_wdg)
                name = btn.get_img_name(img)
                btn.clicked.connect(lambda: cmds.select(f'{name}', tgl=True))
    """
    def __init__(self, img, x=0, y=0):
        super(ImageButton, self).__init__()
        self.setup_img_btn(img, x, y)

    def setup_img_btn(self, img, x, y):
        """
        Takes image path and coordinates to place relative to parent widget with set dimensions.
        Toggles button on/off when selected or deselected.

        Args:
            img (str): Path to image
            x (float):  x pixel coordinate relative to parent widget
            y (float):  y pixel coordinate relative to parent widget

        """
        size = QtGui.QImageReader(img).size()

        self.setStyleSheet("QPushButton {"
                           "border: none;"
                           "background-color: transparent"
                           "}"
                           "QPushButton::hover"
                           "{"
                           "background-color : #444444;"
                           "}"
                           "QToolTip { "
                           "color: white; "
                           "background-color: black; "
                           "border: none; "
                           "}"
                           )

        self.setFixedSize(size.width(), size.height())
        self.move(x, y)
        self.setToolTip(self.get_img_name(img))

        # Two versions of icon, one for toggled state and one for not toggled
        icon = QtGui.QIcon()
        toggle_on = QtGui.QPixmap(img)
        icon.addPixmap(toggle_on, QtGui.QIcon.Normal, QtGui.QIcon.On)
        toggle_off = icon.pixmap(toggle_on.size(), QtGui.QIcon.Disabled, QtGui.QIcon.On)

        self.setIcon(toggle_off)
        self.setIconSize(QtCore.QSize(size))  # Button and icon have same dimensions

        self.setCheckable(True)

        def toggle_icon():
            if self.isChecked():
                self.setIcon(toggle_on)
            else:
                self.setIcon(toggle_off)

        self.toggled.connect(toggle_icon)

    def get_img_name(self, img):    # Icon name matches ctrl name
        """
        Args:
            img (str): Path to image

        Returns:
            str: clean name of image without path or extension
        """
        path = os.path.splitext(QtGui.QImageReader(img).fileName())[0]
        return os.path.basename(path)
