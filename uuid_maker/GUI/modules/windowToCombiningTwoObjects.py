from functools import partial
from math import ceil

from PyQt6 import QtGui
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QGridLayout, QLabel, QPushButton, QSizePolicy, QGroupBox, QSpacerItem, QWidget, QApplication
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QPixmap

from cv2 import imdecode
from numpy import frombuffer, uint8

from .QTForms.combining_two_objects_to_one import Ui_combining_objects
from .classes import (
    EjectedObjectData,
    TypeEjectedObject,
)
from .grid_container import GridContainer

class WindowToCombiningTwoObjects(QDialog, Ui_combining_objects):
    split_objects = pyqtSignal(EjectedObjectData)

    def __init__(self, parent, firts_object_data: TypeEjectedObject, second_object_data: TypeEjectedObject):
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

    def setUpObjectsImages(self, layout: QVBoxLayout, objects_data: TypeEjectedObject):
        def toggle_hide_images(widget:QGroupBox, button:QPushButton):
            widget.setHidden(not widget.isHidden())
            button.setText('Показать изображения' if widget.isHidden() else 'Скрыть изображения')

        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        
        for object_data in objects_data:
            widget = QGroupBox(self)
            widget_layout = QVBoxLayout()
            widget.setLayout(widget_layout)
            widget_for_data = QWidget(widget)
            gridLayout_for_data = QGridLayout()
            widget_for_data.setLayout(gridLayout_for_data)
            widget_layout.addWidget(widget_for_data)
            layout.addWidget(widget)
            

            # Наполняем полезной информацией
            gridLayout_for_data.addWidget(
                QLabel(object_data.file_name, widget), 
                0, 0,
            )
            gridLayout_for_data.addWidget(
                QLabel(f"Object_ID: {object_data.object_id}", widget), 
                1, 0,
            )
            if len(objects_data) > 1 and objects_data[0] != object_data:
                pushButton_for_split_objects = QPushButton('Разделить')
                pushButton_for_split_objects.clicked.connect(
                    partial(self.pushButtonFunction, object_data))
                gridLayout_for_data.addWidget(
                    pushButton_for_split_objects, 1, 2,
                )
            gridLayout_for_data.addWidget(
                QLabel(f"UUID: {object_data.uuid}", widget), 
                2, 0,
            )
            gridLayout_for_data.addItem(
                QSpacerItem(
                    1, 1, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
                ),
                2, 1
            )
            
            # Наполняем картинками
            image_widget = QGroupBox(widget, title="Изображения")
            gridLayout_for_images = GridContainer(image_widget)
            widget_layout.addWidget(image_widget)
            labels = []
            for image in object_data.images:
                pixmap = QPixmap()
                image_data = image.getvalue()
                pixmap.loadFromData(image_data)
                original_image_size = imdecode(
                    frombuffer(image_data, uint8), -1).shape
                width_ratio = (200) / original_image_size[0]
                height_ratio = (200) / original_image_size[1]
                scale_ratio = min(width_ratio, height_ratio)
                scaled_width = int(original_image_size[1] * scale_ratio)
                scaled_height = int(original_image_size[0] * scale_ratio)
                pixmap = pixmap.scaled(
                    scaled_width,
                    scaled_height
                )
                label = QLabel(image_widget)
                label.setPixmap(pixmap)
                labels.append(label)
            else:
                gridLayout_for_images.addObject(labels)
            pushButton_for_hide_images = QPushButton('Скрыть изображения')
            pushButton_for_hide_images.clicked.connect(partial(toggle_hide_images, image_widget, pushButton_for_hide_images))
            gridLayout_for_data.addWidget(
                pushButton_for_hide_images, 
                2, 2,
            )
        layout.addItem(
            QSpacerItem(
                1, 1, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
            )
        )

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
