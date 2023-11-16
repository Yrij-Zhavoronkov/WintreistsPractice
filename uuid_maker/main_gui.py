import sys
from PyQt6 import QtGui
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QWidget, QLabel, QPushButton, QDialog, QVBoxLayout, QGridLayout, QMessageBox
from PyQt6.QtCore import pyqtSignal, Qt, QTimer, QEvent, QMimeData, QByteArray, pyqtBoundSignal
from PyQt6.QtGui import QPixmap, QCloseEvent, QMouseEvent, QEnterEvent, QDrag, QDragEnterEvent, QDropEvent
from functools import partial
import os
import typing
from pathlib import Path
import io
import cv2
import numpy as np
from threading import Lock
import pickle
import uuid
from dataclasses import dataclass

from MainWindow import Ui_MainWindow
from EjectedObject import Ui_Form_Ejected_Object
from combining_two_objects_to_one import Ui_combining_objects
from eject_objects_from_xgtf_and_video import eject_objects, make_change_uuid
from table_objects import Ui_Form_table_objects
from openEjectedObject import Ui_Form_open_ejected_object
from threading import Thread
import resources_file
# Константы


@dataclass
class EjectedObjectDataFileNameAndObjectID:
    file_name: str
    object_id: int

    def __eq__(self, other_object: object) -> bool:
        if isinstance(other_object, EjectedObjectDataFileNameAndObjectID):
            return self.file_name == other_object.file_name and self.object_id == other_object.object_id
        else:
            raise TypeError


@dataclass
class EjectedObjectDataImages:
    images: typing.List[io.BytesIO]


@dataclass
class EjectedObjectData(EjectedObjectDataImages, EjectedObjectDataFileNameAndObjectID):
    uuid: str
    position: typing.Tuple[int, int] = (0, 0)
    sorted: bool = False
    changed: bool = False

    def __eq__(self, other_object: object) -> bool:
        if isinstance(other_object, EjectedObjectData):
            return self.file_name == other_object.file_name and self.object_id == other_object.object_id
        else:
            raise TypeError

    def __ne__(self, other_object: object) -> bool:
        return not self.__eq__(other_object)


TYPE_EJECTED_OBJECT = typing.List[EjectedObjectData]

UUID_LENGTH = 32
#

class ThreadForEjectingObjects(Thread):
    def __init__(
            self, 
            xgtf_files: typing.List[os.PathLike],
            callback_signal: pyqtBoundSignal,
            on_finish_callback: typing.Optional[typing.Callable[[], None]] = None,
            on_start_callback: typing.Optional[typing.Callable[[], None]] = None,
        ):
        super().__init__()
        self.xgtf_files = xgtf_files
        self.callback_signal = callback_signal
        self.on_finish_callback = on_finish_callback
        self.on_start_callback = on_start_callback
        self.stop_work = False
        self.sorted = False
        self.end_files = False
        self.continue_work = True
        self.lock = Lock()
        pass

    def run(self) -> None:
        while True:
            if self.stop_work: 
                return
            if len(self.xgtf_files) == 0:
                self.end_files = True
                if self.on_finish_callback is not None:
                    self.on_finish_callback()
                return
            while not self.continue_work:
                self.lock.acquire(blocking=True)
            if self.on_start_callback is not None:
                self.on_start_callback()
            
            xgtf_file = self.xgtf_files.pop(0)
            for data in eject_objects(xgtf_file):
                if self.stop_work: 
                    return # Выход из thread
                self.send_data(data)
            if self.on_finish_callback is not None: # 
                self.on_finish_callback()
            self.continue_work = False
            
    def interinput(self):
        self.stop_work = True

    def notify(self):
        self.continue_work = True
        if self.lock.locked():
            self.lock.release()

    def send_data(self, data):
        self.callback_signal.emit(data, self.sorted)
        

class MainWindow(QMainWindow, Ui_MainWindow):
    make_widget_from_data = pyqtSignal(dict, bool)
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)

        # Создание виджетов
        self.creating_widgets()
        # Предустановка свойств
        self.setup_properties()

        # Установка соединений между виджетами
        self.setup_connections()

        # Финальное завершение вида окна
        self.showMaximized()

        # Создание Lock
        self.sorted_lock = Lock()
        self.not_sorted_lock = Lock()
        # Список виджетов
        self.ejected_objects_widgets_list: typing.List[EjectedObject] = []

        # Константа количества объектов в ряду
        self.EJECTED_OBJECTS_IN_ROW = 3 #self.spinBox_ejectedObjects_in_row.value()
        # Debug
        # self.work_dir = r'C:\Users\smeta\source\repos\WintreistsPractice\xgtf_video'
        # self.open_xgtf_files()

    def setup_properties(self):
        self.pushButtons_set = [
            self.pushButton_set_1,
            self.pushButton_set_2,
            self.pushButton_set_3,
            self.pushButton_set_4,
        ]
        self.gridLayout_sorted_objects.setSpacing(15)
        self.gridLayout_not_sorted_objects.setSpacing(15)
        pass

    def setup_connections(self):
        # Кнопки
        self.pushButton_open_xgtf_files_and_load.clicked.connect(
            partial(
                self.open_work_folder, "Выберите рабочую папку:"
            )
        )
        self.pushButton_save_results.clicked.connect(self.save_results)
        # self.spinBox_ejectedObjects_in_row.valueChanged.connect(
        #     self.spinBox_valueChanged)
        for index, button in enumerate(self.pushButtons_set):
            button.clicked.connect(
                partial(
                    self.ejected_objects_in_row_valueChanged,
                    index + 1,
                    button,
                )
            )
        self.make_widget_from_data.connect(self.func_for_creating_widgets)
        pass

    def ejected_objects_in_row_valueChanged(self, value:int, from_button: QPushButton):
        self.EJECTED_OBJECTS_IN_ROW = value
        for button in self.pushButtons_set:
            if button != from_button:
                button.setChecked(False)
        self.updateGridLayout(sorted=False, just_update=True)
        self.updateGridLayout(sorted=True, just_update=True)
        pass

    def creating_widgets(self):
        self.sorted_table = TableObjects(self.groupBox, True)
        self.sorted_table.move_notSorted_to_Sorted.connect(
            self.move_notSorted_to_Sorted)
        self.groupBox.layout().addWidget(self.sorted_table)
        self.gridLayout_sorted_objects = self.sorted_table.gridLayout
        self.not_sorted_table = TableObjects(self.groupBox_2, False)
        self.groupBox_2.layout().addWidget(self.not_sorted_table)
        self.gridLayout_not_sorted_objects = self.not_sorted_table.gridLayout

        self.thread_for_ejecting_sorted_objects = None
        self.thread_ejecting_object = None
        pass

    def split_objects(self, object_data: EjectedObjectData):
        self.create_new_not_sorted_object(object_data)
        pass

    def move_notSorted_to_Sorted(self, object_data: TYPE_EJECTED_OBJECT):
        self.updateGridLayout(object_data[0].position, object_data[0].sorted)
        self.deleteCombinedObject(EjectedObjectDataFileNameAndObjectID(
            object_data[0].file_name, object_data[0].object_id))
        for object in object_data:
            object.changed = True
            self.create_new_sorted_object(object)

        pass

    def save_results(self):
        self.disable_buttons()
        save_data: typing.Dict[typing.List] = {}
        for widget in self.ejected_objects_widgets_list:
            for object in widget.self_object_data:
                if object.changed:
                    if object.file_name in save_data:
                        save_data[object.file_name].append({
                            'object_id': object.object_id,
                            'uuid': object.uuid
                        })
                    else:
                        save_data[object.file_name] = [{
                            'object_id': object.object_id,
                            'uuid': object.uuid
                        }]
        for file_name in save_data:
            path_to_xgtf_file = Path(self.work_dir).joinpath(
                file_name.rpartition(".")[0]+".xgtf")
            make_change_uuid(
                path_to_xgtf_file, save_data[file_name])
        QMessageBox.information(self, "Сохранение", "Результаты сохранены")
        self.enable_buttons()
        pass

    def deleteCombinedObject(self, deleting_object: EjectedObjectDataFileNameAndObjectID):
        for widget in self.ejected_objects_widgets_list:
            widget_version = EjectedObjectDataFileNameAndObjectID(
                widget.self_object_data[0].file_name,
                widget.self_object_data[0].object_id
            )
            if widget_version == deleting_object:
                self.ejected_objects_widgets_list.remove(widget)
                widget.deleteLater()
                return None
        pass

    def open_xgtf_files(self):
        self.show_buttons()
        self.disable_buttons()
        for widget in self.ejected_objects_widgets_list:
            widget.deleteLater()
        self.ejected_objects_widgets_list.clear()
        if self.thread_for_ejecting_sorted_objects is not None:
            self.thread_for_ejecting_sorted_objects.interinput()
            self.thread_for_ejecting_sorted_objects.join()
        if self.thread_ejecting_object is not None:
            self.thread_ejecting_object.interinput()
            self.thread_ejecting_object.join()
        while self.gridLayout_not_sorted_objects.count():
            item = self.gridLayout_not_sorted_objects.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        while self.gridLayout_sorted_objects.count():
            item = self.gridLayout_sorted_objects.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        #

        self.xgtf_file_names = self.get_xgtf_file_name()
        self.thread_for_ejecting_sorted_objects = ThreadForEjectingObjects(
            xgtf_files=[self.xgtf_file_names.pop(0)],
            callback_signal=self.make_widget_from_data,
        )
        self.thread_for_ejecting_sorted_objects.sorted = True
        self.thread_ejecting_object = ThreadForEjectingObjects(
            xgtf_files=self.xgtf_file_names,
            callback_signal=self.make_widget_from_data,
            on_finish_callback=self.on_finish_thread,
            on_start_callback=self.on_start_thread,
        )
        self.thread_for_ejecting_sorted_objects.start()
        self.thread_ejecting_object.start()
        pass

    def on_start_thread(self):
        self.disable_buttons()
    def on_finish_thread(self):
        self.enable_buttons()
        self.activateWindow()

    def show_buttons(self):
        self.pushButton_save_results.setVisible(True)

    def enable_buttons(self):
        if not self.pushButton_save_results.isHidden():
            self.pushButton_save_results.setEnabled(True)

    def disable_buttons(self):
        self.pushButton_save_results.setEnabled(False)

    def create_new_sorted_object(self, object_data: typing.Union[typing.Dict, EjectedObjectData]):
        self.sorted_lock.acquire()
        grid_count = self.gridLayout_sorted_objects.count()
        widget = EjectedObject(
            object_data, self, (grid_count//self.EJECTED_OBJECTS_IN_ROW, grid_count % self.EJECTED_OBJECTS_IN_ROW), sorted=True)
        widget.updateGridLayout.connect(self.updateGridLayout)
        widget.deleteCombinedObject.connect(self.deleteCombinedObject)
        widget.split_objects.connect(self.split_objects)
        self.gridLayout_sorted_objects.addWidget(
            widget, 
            grid_count//self.EJECTED_OBJECTS_IN_ROW, 
            grid_count % self.EJECTED_OBJECTS_IN_ROW,
            Qt.AlignmentFlag.AlignTop,
        )
        for exist_widget in self.ejected_objects_widgets_list:
            if widget.self_object_data[0].uuid == exist_widget.self_object_data[0].uuid:
                exist_widget.combine_objects(widget.self_object_data)
                self.sorted_lock.release()
                return None
        self.ejected_objects_widgets_list.append(widget)
        self.sorted_lock.release()
        pass

    def create_new_not_sorted_object(self, object_data: typing.Union[typing.Dict, EjectedObjectData]):
        self.not_sorted_lock.acquire()
        grid_count = self.gridLayout_not_sorted_objects.count()
        if isinstance(object_data, dict):
            if len(object_data['uuid']) == UUID_LENGTH:
                self.create_new_sorted_object(object_data)
                self.not_sorted_lock.release()
                return None
        widget = EjectedObject(
            object_data, self, (grid_count//self.EJECTED_OBJECTS_IN_ROW, grid_count % self.EJECTED_OBJECTS_IN_ROW), sorted=False)
        for exist_widget in self.ejected_objects_widgets_list:
            if widget.self_object_data[0].uuid == exist_widget.self_object_data[0].uuid:
                exist_widget.combine_objects(widget.self_object_data)
                self.not_sorted_lock.release()
                return None

        widget.updateGridLayout.connect(self.updateGridLayout)
        widget.deleteCombinedObject.connect(self.deleteCombinedObject)
        widget.split_objects.connect(self.split_objects)
        self.gridLayout_not_sorted_objects.addWidget(
            widget, 
            grid_count//self.EJECTED_OBJECTS_IN_ROW, 
            grid_count % self.EJECTED_OBJECTS_IN_ROW,
            Qt.AlignmentFlag.AlignTop,
        )
        self.ejected_objects_widgets_list.append(widget)
        self.not_sorted_lock.release()
        pass

    def updateGridLayout(self, position: typing.Tuple[int, int] = (0, 0), sorted: bool = False, just_update: bool = False):
        gridLayout = self.gridLayout_sorted_objects if sorted else self.gridLayout_not_sorted_objects
        widget_index = position[0] * self.EJECTED_OBJECTS_IN_ROW + position[1]
        if not just_update:
            widget = gridLayout.takeAt(widget_index).widget()
            gridLayout.removeWidget(widget)
            widget.deleteLater()
            if not sorted and gridLayout.count() < self.EJECTED_OBJECTS_IN_ROW*2:
                self.thread_ejecting_object.notify()
        for index in range(widget_index, gridLayout.count()):
            widget: EjectedObject = gridLayout.takeAt(widget_index).widget()
            gridLayout.removeWidget(widget)
            widget.self_object_data[0].position = (
                index//self.EJECTED_OBJECTS_IN_ROW, index % self.EJECTED_OBJECTS_IN_ROW)
            gridLayout.addWidget(
                widget, 
                index//self.EJECTED_OBJECTS_IN_ROW, 
                index % self.EJECTED_OBJECTS_IN_ROW,
                Qt.AlignmentFlag.AlignTop)
        pass

    def closeEvent(self, event: QCloseEvent):
        if self.thread_ejecting_object is not None:
            self.thread_for_ejecting_sorted_objects.interinput()
            self.thread_for_ejecting_sorted_objects.join()
        if self.thread_for_ejecting_sorted_objects is not None:
            self.thread_ejecting_object.interinput()
            self.thread_ejecting_object.join()
        event.accept()

    def get_xgtf_file_name(self) -> typing.List[str]:
        return list(Path(self.work_dir).glob("*.xgtf"))

    def open_work_folder(self, caption):
        directory = QFileDialog.getExistingDirectory(self, caption, os.getcwd())
        if directory:
            self.work_dir = directory
            self.open_xgtf_files()
    
    def func_for_creating_widgets(self, object_data:dict, sorted:bool):
        self.create_new_sorted_object(object_data) if sorted else self.create_new_not_sorted_object(object_data)


class EjectedObject(QWidget, Ui_Form_Ejected_Object):
    updateGridLayout = pyqtSignal(tuple, bool)
    deleteCombinedObject = pyqtSignal(EjectedObjectDataFileNameAndObjectID)
    split_objects = pyqtSignal(EjectedObjectData)

    def __init__(self, ejected_object: typing.Union[typing.Dict, EjectedObjectData], parent=None, position=(0, 0), sorted=False):
        super().__init__(parent)
        self.setupUi(self)

        self.setAcceptDrops(True)
        self.setFixedSize(300, 300)

        if isinstance(ejected_object, dict):
            ejected_object_data = EjectedObjectData(
                ejected_object['file_name'],
                ejected_object['object_id'],
                ejected_object['images'],
                ejected_object['uuid']
            )
        elif isinstance(ejected_object, EjectedObjectData):
            ejected_object_data = ejected_object

        ejected_object_data.sorted = sorted
        ejected_object_data.position = position

        self.self_object_data: TYPE_EJECTED_OBJECT = [ejected_object_data]
        self.objects_data: typing.List[EjectedObjectDataFileNameAndObjectID] = [
            EjectedObjectDataFileNameAndObjectID(
                object.file_name,
                object.object_id
            ) for object in self.self_object_data]
        self.object_images: EjectedObjectDataImages = [
            image for object in self.self_object_data for image in object.images]
        if len(self.self_object_data[0].uuid) != UUID_LENGTH:
            self.self_object_data[0].uuid = self.createUUID()
            if self.self_object_data[0].sorted:
                self.self_object_data[0].changed = True

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
        self.object_images: typing.List[io.BytesIO] = [
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
        original_image_size = cv2.imdecode(
            np.frombuffer(self.image_data, np.uint8), -1).shape
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
        return uuid.uuid4().hex

    def split_objects_function(self, object_data: EjectedObjectData):
        self.self_object_data.remove(object_data)
        object_data.changed = True
        object_data.uuid = ""
        self.updateSelfObjectData()
        self.split_objects.emit(object_data)
        pass


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
                original_image_size = cv2.imdecode(
                    np.frombuffer(image_data, np.uint8), -1).shape
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
                    label, gridLayout_for_images.count()//4, gridLayout_for_images.count() % 4,
                )  # Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop
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


class TableObjects(QWidget, Ui_Form_table_objects):
    move_notSorted_to_Sorted = pyqtSignal(list)

    def __init__(self, parent=None, sorted=True):
        super().__init__(parent)
        self.setupUi(self)

        self.setAcceptDrops(True)

        self.sorted = sorted

    def dragEnterEvent(self, event: QDragEnterEvent = None) -> None:
        if self.sorted:
            if event.mimeData().hasFormat("EjectedObject"):
                data: TYPE_EJECTED_OBJECT = pickle.loads(
                    event.mimeData().data("EjectedObject"))
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
            if event.mimeData().hasFormat("EjectedObject"):
                event.accept()
                data: TYPE_EJECTED_OBJECT = pickle.loads(
                    event.mimeData().data("EjectedObject"))

                dialog = QMessageBox.question(
                    self, 'Объект', 'Добавить объект в отсортированное?')
                if dialog == QMessageBox.StandardButton.Yes:
                    self.move_notSorted_to_Sorted.emit(data)
            else:
                event.ignore()
        else:
            event.ignore()


class OpenEjectedObject(QDialog, Ui_Form_open_ejected_object):
    split_objects = pyqtSignal(EjectedObjectData)

    def __init__(self, parent, object_data: TYPE_EJECTED_OBJECT):
        super().__init__(parent)
        self.setupUi(self)

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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
