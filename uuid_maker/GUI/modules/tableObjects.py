from PyQt6.QtWidgets import QWidget, QMessageBox
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QDragEnterEvent, QDropEvent

import pickle

from .QTForms.table_objects import Ui_Form_table_objects
from .ejectedObject import EjectedObject
from .classes import (
    TypeEjectedObject,
)

class TableObjects(QWidget, Ui_Form_table_objects):
    move_notSorted_to_Sorted = pyqtSignal(list)

    def __init__(self, parent=None, sorted=True):
        super().__init__(parent)
        self.setupUi(self)

        self.setAcceptDrops(True)

        self.sorted = sorted

    def dragEnterEvent(self, event: QDragEnterEvent = None) -> None:
        if self.sorted:
            if event.mimeData().hasFormat(EjectedObject.__name__):
                data: TypeEjectedObject = pickle.loads(
                    event.mimeData().data(EjectedObject.__name__))
                if not data[0].sorted:
                    event.accept()
                else:
                    event.ignore()
            else:
                event.ignore()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent = None) -> None:
        if self.sorted:
            if event.mimeData().hasFormat(EjectedObject.__name__):
                event.accept()
                data: TypeEjectedObject = pickle.loads(
                    event.mimeData().data(EjectedObject.__name__))

                dialog = QMessageBox.question(
                    self, 'Объект', 'Добавить объект в отсортированное?')
                if dialog == QMessageBox.StandardButton.Yes:
                    self.move_notSorted_to_Sorted.emit(data)
            else:
                event.ignore()
        else:
            event.ignore()
