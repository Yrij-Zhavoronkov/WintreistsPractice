from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import pyqtSignal, QTimer, Qt, QMimeData, QByteArray, QEvent
from PyQt6.QtGui import QMouseEvent, QDrag, QDragEnterEvent, QDropEvent, QEnterEvent, QPixmap

from typing import Union, List
import pickle
from io import BytesIO
from cv2 import imdecode
from numpy import frombuffer, uint8
from uuid import uuid4

from .QTForms.EjectedObject import Ui_Form_Ejected_Object
from .classes import (
    EjectedObjectDataFileNameAndObjectID, 
    EjectedObjectData, 
    ObjectData,
    EjectedObjectDataImages,
    UUID_LENGTH,
    TYPE_EJECTED_OBJECT,
)
from .openEjectedObject import OpenEjectedObject
from .windowToCombiningTwoObjects import WindowToCombiningTwoObjects


class EjectedObject(QWidget, Ui_Form_Ejected_Object):
    updateGridLayout = pyqtSignal(tuple, bool)
    deleteCombinedObject = pyqtSignal(EjectedObjectDataFileNameAndObjectID)
    split_objects = pyqtSignal(EjectedObjectData)

    def __init__(self, ejected_object: Union[ObjectData, EjectedObjectData], parent=None, position=(0, 0), sorted=False):
        super().__init__(parent)
        self.setupUi(self)

        self.setAcceptDrops(True)
        self.setFixedSize(300, 300)

        if isinstance(ejected_object, ObjectData):
            ejected_object_data = EjectedObjectData(
                ejected_object.file_name,
                ejected_object.object_id,
                ejected_object.images,
                ejected_object.uuid
            )
        elif isinstance(ejected_object, EjectedObjectData):
            ejected_object_data = ejected_object

        ejected_object_data.sorted = sorted
        ejected_object_data.position = position

        if len(ejected_object_data.uuid) != UUID_LENGTH:
            ejected_object_data.uuid = self.createUUID()
            if ejected_object_data.sorted:
                ejected_object_data.changed = True

        self.self_object_data: TYPE_EJECTED_OBJECT = [ejected_object_data]
        self.objects_data: List[EjectedObjectDataFileNameAndObjectID] = [
            EjectedObjectDataFileNameAndObjectID(
                ejected_object_data.file_name,
                ejected_object_data.object_id
            )]
        self.object_images: EjectedObjectDataImages = ejected_object_data.images
        

        self.mouse_in_widget = False
        self.generator_for_images = self.get_image()
        self.set_next_image()
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.setInterval(1500)
        self.timer.setTimerType(Qt.TimerType.VeryCoarseTimer)
        self.timer.timeout.connect(self.timerEvent)

    def mouseMoveEvent(self, event: QMouseEvent = None) -> None:
        if event.buttons() == Qt.MouseButton.LeftButton:
            drag = QDrag(self)
            mime = QMimeData()
            mime.setData("EjectedObject", QByteArray(
                pickle.dumps(self.self_object_data)))
            drag.setMimeData(mime)
            drag.exec(Qt.DropAction.MoveAction)
            pass
        return super().mouseMoveEvent(event)

    def dragEnterEvent(self, event: QDragEnterEvent = None) -> None:
        if event.mimeData().hasFormat("EjectedObject"):
            data: TYPE_EJECTED_OBJECT = pickle.loads(
                event.mimeData().data("EjectedObject"))
            for objects_data in data:
                temp_data = EjectedObjectDataFileNameAndObjectID(
                    objects_data.file_name, objects_data.object_id)
                if temp_data in self.objects_data:
                    event.ignore()
                    return None

            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent = None) -> None:
        if event.mimeData().hasFormat("EjectedObject"):
            data: TYPE_EJECTED_OBJECT = pickle.loads(
                event.mimeData().data("EjectedObject"))
            for objects_data in data:
                temp_data = EjectedObjectDataFileNameAndObjectID(
                    objects_data.file_name, objects_data.object_id)
                if temp_data in self.objects_data:
                    event.ignore()
                    return None
            event.accept()
            combining_objects_window = WindowToCombiningTwoObjects(
                self, self.self_object_data, data)
            combining_objects_window.split_objects.connect(
                self.split_objects_function)
            combining_objects_window.exec()
            if combining_objects_window.combining:
                self.combine_objects(data)
                pass
            return None
        else:
            event.ignore()

    def combine_objects(self, other_object: TYPE_EJECTED_OBJECT):
        self.updateGridLayout.emit(
            other_object[0].position, other_object[0].sorted)
        self.deleteCombinedObject.emit(EjectedObjectDataFileNameAndObjectID(
            other_object[0].file_name, other_object[0].object_id))
        if self.self_object_data[0].sorted:
            for object in other_object:
                object.sorted = True
        self.self_object_data = self.self_object_data+other_object
        if self.self_object_data[-1].uuid != self.self_object_data[0].uuid:
            self.self_object_data[-1].uuid = self.self_object_data[0].uuid
            self.self_object_data[-1].changed = True
        self.updateSelfObjectData()
        pass

    def updateSelfObjectData(self):
        self.objects_data: EjectedObjectDataFileNameAndObjectID = [
            EjectedObjectDataFileNameAndObjectID(
                object.file_name,
                object.object_id
            )
            for object in self.self_object_data
        ]
        self.object_images: List[BytesIO] = [
            image for object in self.self_object_data for image in object.images]
        self.generator_for_images = self.get_image()

    def enterEvent(self, event: QEnterEvent = None) -> None:
        self.mouse_in_widget = True
        self.timerEvent()
        return super().enterEvent(event)

    def leaveEvent(self, event: QEvent = None) -> None:
        self.mouse_in_widget = False
        self.timer.stop()
        return super().leaveEvent(event)

    def mouseDoubleClickEvent(self, event: QMouseEvent = None) -> None:
        dialog = OpenEjectedObject(self, self.self_object_data)
        dialog.split_objects.connect(self.split_objects_function)
        dialog.exec()
        pass
    
    def mousePressEvent(self, event: QMouseEvent = None) -> None:
        self.set_next_image()

    def set_next_image(self):
        self.image_data = next(self.generator_for_images).getvalue()
        pixmap = QPixmap()
        pixmap.loadFromData(self.image_data)
        original_image_size = imdecode(
            frombuffer(self.image_data, uint8), -1).shape
        width_ratio = (self.width()-38) / original_image_size[1]
        height_ratio = (self.height()-38) / original_image_size[0]
        scale_ratio = min(width_ratio, height_ratio)
        pixmap = pixmap.scaled(
            int(original_image_size[1] * scale_ratio),
            int(original_image_size[0] * scale_ratio)
        )
        self.label_image.setPixmap(pixmap)
        self.label_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pass

    def get_image(self):
        while True:
            for image in self.object_images:
                yield image

    def timerEvent(self):
        self.set_next_image()
        if self.mouse_in_widget:
            self.timer.start()

    def createUUID(self):
        return uuid4().hex

    def split_objects_function(self, object_data: EjectedObjectData):
        self.self_object_data.remove(object_data)
        object_data.changed = True
        object_data.uuid = ""
        self.updateSelfObjectData()
        self.split_objects.emit(object_data)
        pass
