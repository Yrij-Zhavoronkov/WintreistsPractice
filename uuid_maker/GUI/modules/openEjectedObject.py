from PyQt6.QtWidgets import QDialog
from PyQt6.QtCore import pyqtSignal

from .QTForms.openEjectedObject import Ui_Form_open_ejected_object
from .windowToCombiningTwoObjects import WindowToCombiningTwoObjects
from .classes import (
    EjectedObjectData,
    TypeEjectedObject,
)



class OpenEjectedObject(QDialog, Ui_Form_open_ejected_object):
    split_objects = pyqtSignal(EjectedObjectData)

    def __init__(self, parent, object_data: TypeEjectedObject):
        super().__init__(parent)
        self.setupUi(self)
        self.showMaximized()

        self.pushButton.clicked.connect(self.close)
        self.setWindowTitle('Открытый объект')

        # Определение переменных
        self.object_data = object_data
        # Заполнить виджет
        WindowToCombiningTwoObjects.setUpObjectsImages(
            self, self.verticalLayout_main, self.object_data)

    def recreateWindowData(self):
        WindowToCombiningTwoObjects.setUpObjectsImages(
            self, self.verticalLayout_main, self.object_data)

    def pushButtonFunction(self, object_data: EjectedObjectData):
        self.split_objects.emit(object_data)
        self.recreateWindowData()
