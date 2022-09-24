import sys

from PySide2 import QtCore, QtWidgets
from shiboken2 import wrapInstance

import maya.OpenMayaUI as omui


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)


class BasicDialog(QtWidgets.QDialog):

    def __init__(self, parent=maya_main_window()):
        super(BasicDialog, self).__init__(parent)

        self.setWindowTitle("Title")
        self.setMinimumSize(300, 80)
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)

        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        pass

    def create_layout(self):
        pass

    def create_connections(self):
        pass


if __name__ == "__main__":

    try:
        basic_dialog.close()
        basic_dialog.deleteLater()
    except:
        pass

    basic_dialog = BasicDialog()
    basic_dialog.show()
