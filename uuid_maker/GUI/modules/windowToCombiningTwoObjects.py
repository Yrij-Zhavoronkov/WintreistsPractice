from PyQt6.QtWidgets import QDialog, QVBoxLayout, QGridLayout, QWidget, QLabel, QPushButton
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QPixmap

from functools import partial
from cv2 import imdecode
from numpy import frombuffer, uint8

from .QTForms.combining_two_objects_to_one import Ui_combining_objects
from .classes import (
    EjectedObjectData,
    TYPE_EJECTED_OBJECT,
)

class WindowToCombiningTwoObjects(QDialog, Ui_combining_objects):
    split_objects = pyqtSignal(EjectedObjectData)

    def __init__(self, parent, firts_object_data: TYPE_EJECTED_OBJECT, second_object_data: TYPE_EJECTED_OBJECT):
        super().__init__(parent)
        self.setupUi(self)
        self.showMaximized()
        self.setWindowTitle('Соединение двух объектов')

        self.first_object_data = firts_object_data
        self.second_object_data = second_object_data
        self.combining = False
        self.buttonBox.accepted.connect(self.acceptCombining)
        self.buttonBox.rejected.connect(self.rejectCombining)

        self.setUpObjectsImages(
            self.verticalLayout_first_object, self.first_object_data)
        self.setUpObjectsImages(
            self.verticalLayout_second_object, self.second_object_data)

    def setUpObjectsImages(self, layout: QVBoxLayout, objects_data: TYPE_EJECTED_OBJECT):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        for object_data in objects_data:
            widget = QWidget(self)
            widget_layout = QVBoxLayout()
            gridLayout_for_data = QGridLayout()
            gridLayout_for_images = QGridLayout()

            # Наполняем полезной информацией
            gridLayout_for_data.addWidget(
                QLabel(object_data.file_name, widget), 0, 0
            )
            gridLayout_for_data.addWidget(
                QLabel(f"Object_ID: {object_data.object_id}", widget), 1, 0
            )
            gridLayout_for_data.addWidget(
                QLabel(f"UUID: {object_data.uuid}", widget), 2, 0
            )
            if len(objects_data) > 1 and objects_data[0] != object_data:
                pushButton_for_split_objects = QPushButton('Разделить')
                pushButton_for_split_objects.clicked.connect(
                    partial(self.pushButtonFunction, object_data))
                gridLayout_for_data.addWidget(
                    pushButton_for_split_objects, 1, 1)
            # Наполняем картинками
            for image in object_data.images:
                pixmap = QPixmap()
                image_data = image.getvalue()
                pixmap.loadFromData(image_data)
                original_image_size = imdecode(
                    frombuffer(image_data, uint8), -1).shape
                width_ratio = (200) / original_image_size[0]
                height_ratio = (200) / original_image_size[1]
                scale_ratio = min(width_ratio, height_ratio)
                pixmap = pixmap.scaled(
                    int(original_image_size[1] * scale_ratio),
                    int(original_image_size[0] * scale_ratio)
                )
                label = QLabel()
                label.setPixmap(pixmap)
                gridLayout_for_images.addWidget(
                    label, 
                    gridLayout_for_images.count()//4, 
                    gridLayout_for_images.count() % 4,
                    Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop
                )
                pass

            widget_layout.addLayout(gridLayout_for_data)
            widget_layout.addLayout(gridLayout_for_images)
            widget.setLayout(widget_layout)
            layout.addWidget(widget)

    def acceptCombining(self):
        self.combining = True
        self.close()

    def rejectCombining(self):
        self.combining = False
        self.close()

    def recreateWindowData(self):
        self.setUpObjectsImages(
            self.verticalLayout_first_object, self.first_object_data)
        self.setUpObjectsImages(
            self.verticalLayout_second_object, self.second_object_data)

    def pushButtonFunction(self, object_data: EjectedObjectData):
        self.split_objects.emit(object_data)
        self.recreateWindowData()
