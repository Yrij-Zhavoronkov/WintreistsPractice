from PyQt6.QtWidgets import QDialog, QVBoxLayout, QGridLayout, QLabel, QPushButton, QSizePolicy, QGroupBox, QSpacerItem
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
        def toggle_hide_images(widget:QGroupBox, button:QPushButton):
            widget.setHidden(not widget.isHidden())
            button.setText('Показать изображения' if widget.isHidden() else 'Скрыть изображения')

        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        for object_data in objects_data:
            gridLayout_for_data = QGridLayout()
            widget = QGroupBox(self)
            widget.setLayout(gridLayout_for_data)

            # Наполняем полезной информацией
            gridLayout_for_data.addWidget(
                QLabel(object_data.file_name, widget), 
                0, 0,
                alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft
            )
            gridLayout_for_data.addWidget(
                QLabel(f"Object_ID: {object_data.object_id}", widget), 
                1, 0,
                alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft
            )
            gridLayout_for_data.addWidget(
                QLabel(f"UUID: {object_data.uuid}", widget), 
                2, 0,
                alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft
            )
            if len(objects_data) > 1 and objects_data[0] != object_data:
                pushButton_for_split_objects = QPushButton('Разделить')
                pushButton_for_split_objects.clicked.connect(
                    partial(self.pushButtonFunction, object_data))
                gridLayout_for_data.addWidget(
                    pushButton_for_split_objects, 1, 1,
                    alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
            # Наполняем картинками
            image_widget = QGroupBox(widget, title="Изображения")
            gridLayout_for_images = QGridLayout()
            image_widget.setLayout(gridLayout_for_images)
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
            pushButton_for_hide_images = QPushButton('Скрыть изображения')
            pushButton_for_hide_images.clicked.connect(partial(toggle_hide_images, image_widget, pushButton_for_hide_images))
            gridLayout_for_data.addWidget(
                pushButton_for_hide_images, 
                2, 1,
                alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
            gridLayout_for_data.addItem(
                QSpacerItem(
                    1, 1, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
                ),
                2, 2
            )
            gridLayout_for_data.addWidget(
                image_widget, 
                3, 0,
                alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
            layout.addWidget(widget)
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
