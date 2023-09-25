import sys
from PyQt6 import QtGui
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QLineEdit, QWidget, QLabel, QLayout, QDialog, QVBoxLayout, QGridLayout, QMessageBox
from PyQt6.QtCore import QThread, QTimerEvent, pyqtSignal, Qt, QTimer, QEvent, QMimeData, QByteArray
from PyQt6.QtGui import QPixmap, QCloseEvent, QMouseEvent, QEnterEvent, QDrag, QDragEnterEvent, QDropEvent
from functools import partial
import os
import typing
from pathlib import Path
import time
import io
import cv2
import copy
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


class ThreadForEjectingObjects(QThread):
    callback_signal = pyqtSignal(dict)

    def __init__(self, path_to_xgtf_file: os.PathLike, parent=None):
        super(QThread, self).__init__(parent)
        self.path_to_xgtf_file = path_to_xgtf_file

    def run(self):
        eject_objects(self.path_to_xgtf_file, self.callback_signal.emit)
        pass


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.showMaximized()

        # Создание виджетов
        self.creating_widgets()
        # Предустановка свойств
        self.setup_properties()

        # Установка соединений между виджетами
        self.setup_connections()

        # Создание Lock
        self.sorted_lock = Lock()
        self.not_sorted_lock = Lock()
        # Список виджетов
        self.ejected_objects_widgets_list: typing.List[EjectedObject] = []

        # Константа количества объектов в ряду
        self.EJECTED_OBJECTS_IN_ROW = 4

        # Debug
        self.lineEdit_work_dir.setText(
            r'C:\Users\smeta\source\repos\WintreistsPractice\xgtf_video')
        self.pushButton_open_xgtf_files.setEnabled(True)
        self.pushButton_open_xgtf_files.click()

    def creating_widgets(self):
        self.sorted_table = TableObjects(self.groupBox, True)
        self.sorted_table.move_notSorted_to_Sorted.connect(
            self.move_notSorted_to_Sorted)
        self.groupBox.layout().addWidget(self.sorted_table)
        self.gridLayout_sorted_objects = self.sorted_table.gridLayout
        self.not_sorted_table = TableObjects(self.groupBox_2, False)
        self.groupBox_2.layout().addWidget(self.not_sorted_table)
        self.gridLayout_not_sorted_objects = self.not_sorted_table.gridLayout
        pass

    def move_notSorted_to_Sorted(self, object_data: TYPE_EJECTED_OBJECT):
        self.updateGridLayout(object_data[0].position, object_data[0].sorted)
        self.deleteCombinedObject(EjectedObjectDataFileNameAndObjectID(
            object_data[0].file_name, object_data[0].object_id))
        for object in object_data:
            self.create_new_sorted_object({
                'file_name': object.file_name,
                'object_id': object.object_id,
                'uuid': object.uuid,
                'images': object.images
            })

        pass

    def mousePressEvent(self, a0: QMouseEvent = None) -> None:
        print('По главному окну было нажатие')
        return super().mousePressEvent(a0)

    def setup_properties(self):
        self.pushButton_load_next_objects.setVisible(False)
        self.pushButton_save_results.setVisible(False)
        pass

    def setup_connections(self):
        # Кнопки
        self.toolButton_select_work_dir.clicked.connect(
            partial(self.set_lineEdit_text_from_button, self.lineEdit_work_dir, "Выберите рабочую папку:"))
        self.pushButton_open_xgtf_files.clicked.connect(self.open_xgtf_files)
        self.pushButton_load_next_objects.clicked.connect(
            self.continue_ejecting_objects)
        self.pushButton_save_results.clicked.connect(self.save_results)
        pass

    def save_results(self):
        self.disable_buttons()
        save_data = {}
        for widget in self.ejected_objects_widgets_list:
            if widget.self_object_data[0].sorted:
                for object in widget.self_object_data:
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
            path_to_xgtf_file = Path(self.lineEdit_work_dir.text()).joinpath(
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
        self.disable_buttons()
        self.hide_buttons()
        self.ejected_objects_widgets_list.clear()
        # Добавить код удаления всех объектов
        if self.gridLayout_not_sorted_objects.count():
            self.thread_ejecting_object.quit()
        if self.gridLayout_sorted_objects.count():
            self.thread_for_ejecting_sorted_objects.quit()
        while self.gridLayout_not_sorted_objects.count():
            item = self.gridLayout_not_sorted_objects.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.close()
        while self.gridLayout_sorted_objects.count():
            item = self.gridLayout_sorted_objects.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.close()
        #

        self.xgtf_file_name_generator = self.get_xgtf_file_name()
        self.thread_for_ejecting_sorted_objects = ThreadForEjectingObjects(
            next(self.xgtf_file_name_generator))
        self.thread_for_ejecting_sorted_objects.callback_signal.connect(
            self.create_new_sorted_object, Qt.ConnectionType.QueuedConnection)
        self.thread_for_ejecting_sorted_objects.start()
        self.thread_ejecting_object = ThreadForEjectingObjects(
            next(self.xgtf_file_name_generator))
        self.thread_ejecting_object.callback_signal.connect(
            self.create_new_not_sorted_object)
        self.thread_ejecting_object.finished.connect(self.on_finish_thread)
        self.thread_ejecting_object.start()
        pass

    def continue_ejecting_objects(self):
        self.disable_buttons()

        self.thread_ejecting_object = ThreadForEjectingObjects(
            next(self.xgtf_file_name_generator))
        self.thread_ejecting_object.callback_signal.connect(
            self.create_new_not_sorted_object)
        self.thread_ejecting_object.finished.connect(self.on_finish_thread)
        self.thread_ejecting_object.start()

    def on_finish_thread(self):
        self.enable_buttons()
        self.show_buttons()
        self.activateWindow()
        pass

    def show_buttons(self):
        self.pushButton_load_next_objects.setVisible(True)
        self.pushButton_save_results.setVisible(True)

    def hide_buttons(self):
        self.pushButton_load_next_objects.setVisible(False)
        self.pushButton_save_results.setVisible(False)

    def enable_buttons(self):
        self.pushButton_load_next_objects.setEnabled(True)
        self.pushButton_open_xgtf_files.setEnabled(True)
        self.pushButton_save_results.setEnabled(True)

    def disable_buttons(self):
        self.pushButton_load_next_objects.setEnabled(False)
        self.pushButton_open_xgtf_files.setEnabled(False)
        self.pushButton_save_results.setEnabled(False)

    def create_new_sorted_object(self, object_data: dict):
        self.sorted_lock.acquire()
        grid_count = self.gridLayout_sorted_objects.count()
        widget = EjectedObject(
            object_data, self, (grid_count//self.EJECTED_OBJECTS_IN_ROW, grid_count % self.EJECTED_OBJECTS_IN_ROW), sorted=True)
        widget.updateGridLayout.connect(self.updateGridLayout)
        widget.deleteCombinedObject.connect(self.deleteCombinedObject)
        self.gridLayout_sorted_objects.addWidget(
            widget, grid_count//self.EJECTED_OBJECTS_IN_ROW, grid_count % self.EJECTED_OBJECTS_IN_ROW,
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        for exist_widget in self.ejected_objects_widgets_list:
            if widget.self_object_data[0].uuid == exist_widget.self_object_data[0].uuid:
                exist_widget.combine_objects(widget.self_object_data)
                self.sorted_lock.release()
                return None
        self.ejected_objects_widgets_list.append(widget)
        self.sorted_lock.release()
        pass

    def create_new_not_sorted_object(self, object_data: dict):
        self.not_sorted_lock.acquire()
        grid_count = self.gridLayout_not_sorted_objects.count()
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
        self.gridLayout_not_sorted_objects.addWidget(
            widget, grid_count//self.EJECTED_OBJECTS_IN_ROW, grid_count % self.EJECTED_OBJECTS_IN_ROW,
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.ejected_objects_widgets_list.append(widget)
        self.not_sorted_lock.release()
        pass

    def updateGridLayout(self, position: typing.Tuple[int, int], sorted: bool):
        gridLayout = self.gridLayout_sorted_objects if sorted else self.gridLayout_not_sorted_objects
        widget_index = position[0] * self.EJECTED_OBJECTS_IN_ROW + position[1]
        widget = gridLayout.takeAt(widget_index).widget()
        gridLayout.removeWidget(widget)
        widget.deleteLater()
        for index in range(widget_index, gridLayout.count()):
            widget: EjectedObject = gridLayout.takeAt(widget_index).widget()
            gridLayout.removeWidget(widget)
            widget.self_object_data[0].position = (
                index//self.EJECTED_OBJECTS_IN_ROW, index % self.EJECTED_OBJECTS_IN_ROW)
            gridLayout.addWidget(
                widget, index//self.EJECTED_OBJECTS_IN_ROW, index % self.EJECTED_OBJECTS_IN_ROW,
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        pass

    def closeEvent(self, event: QCloseEvent):
        self.thread_for_ejecting_sorted_objects.quit()
        self.thread_ejecting_object.quit()
        event.accept()

    def get_xgtf_file_name(self):
        work_dir = Path(self.lineEdit_work_dir.text())
        for files in work_dir.glob("*.xgtf"):
            yield files

    def set_lineEdit_text_from_button(self, lineEdit: QLineEdit, caption: str):
        directory = self.open_explorer_folder(caption)
        if directory:
            self.pushButton_open_xgtf_files.setEnabled(True)
            lineEdit.setText(directory)

    def open_explorer_folder(self, caption):
        return QFileDialog.getExistingDirectory(self, caption, os.getcwd())


class EjectedObject(QWidget, Ui_Form_Ejected_Object):
    updateGridLayout = pyqtSignal(tuple, bool)
    deleteCombinedObject = pyqtSignal(EjectedObjectDataFileNameAndObjectID)

    def __init__(self, ejected_object: dict, parent=None, position=(0, 0), sorted=False):
        super().__init__(parent)
        self.setupUi(self)

        self.setAcceptDrops(True)

        ejected_object_data = EjectedObjectData(
            ejected_object['file_name'],
            ejected_object['object_id'],
            ejected_object['images'],
            ejected_object['uuid']
        )
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
            combining_objects_window.setWindowTitle(
                'Соединение двух объектов')
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
        self.self_object_data[-1].uuid = self.self_object_data[0].uuid
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
        dialog.exec()
        pass

    def set_next_image(self):
        pixmap = QPixmap()
        image_data = next(self.generator_for_images).getvalue()
        photo = cv2.imdecode(np.frombuffer(image_data, np.uint8), -1)
        pixmap.loadFromData(image_data)
        pixmap = pixmap.scaled(100, 300)
        self.label_image.setPixmap(pixmap)
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


class WindowToCombiningTwoObjects(QDialog, Ui_combining_objects):
    def __init__(self, parent, firts_object_data: TYPE_EJECTED_OBJECT, second_object_data: TYPE_EJECTED_OBJECT):
        super().__init__(parent)
        self.setupUi(self)
        self.showMaximized()

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
        for object_data in objects_data:
            widget = QWidget(self)
            new_layout = QVBoxLayout()
            object_file_name = QLabel(object_data.file_name, widget)
            object_id = QLabel(f"Object_ID: {object_data.object_id}", widget)
            object_uuid = QLabel(f"UUID: {object_data.uuid}", widget)
            gridLayout = QGridLayout()
            for image in object_data.images:
                pixmap = QPixmap()
                image_data = image.getvalue()
                pixmap.loadFromData(image_data)
                pixmap = pixmap.scaled(100, 300)
                label = QLabel()
                label.setPixmap(pixmap)
                gridLayout.addWidget(
                    label, gridLayout.count()//4, gridLayout.count() % 4,
                )  # Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop
                pass
            new_layout.addWidget(object_file_name)
            new_layout.addWidget(object_id)
            new_layout.addWidget(object_uuid)
            new_layout.addLayout(gridLayout)
            widget.setLayout(new_layout)
            layout.addWidget(widget)

    def acceptCombining(self):
        self.combining = True
        self.close()

    def rejectCombining(self):
        self.combining = False
        self.close()


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
                event.accept()
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
    def __init__(self, parent, object_data: TYPE_EJECTED_OBJECT):
        super().__init__(parent)
        self.setupUi(self)

        self.pushButton.clicked.connect(self.close)
        self.setWindowTitle('Открытый объект')

        # Определение переменных
        self.object_data = object_data
        # Заполнить виджет
        WindowToCombiningTwoObjects.setUpObjectsImages(
            self, self.verticalLayout_main, object_data)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
