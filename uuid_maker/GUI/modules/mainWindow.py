from PyQt6.QtWidgets import QMainWindow, QFileDialog, QPushButton, QMessageBox
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QCloseEvent, QAction

from threading import Lock
from typing import List
from pathlib import Path
from functools import partial
from typing import List, Dict, Union, Tuple

import os

from .QTForms.MainWindow import Ui_MainWindow
from .classes import (
    ObjectData,
    EjectedObjectData,
    EjectedObjectDataFileNameAndObjectID,
    TYPE_EJECTED_OBJECT,
    UUID_LENGTH,
)
from .ejectedObject import EjectedObject
from .tableObjects import TableObjects
from .threadForEjectingObjects import ThreadForEjectingObjects
from ..eject_objects_from_xgtf_and_video import make_change_uuid
from ..resources import resources_file

class MainWindow(QMainWindow, Ui_MainWindow):
    make_widget_from_data = pyqtSignal(bool, ObjectData)
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
        self.ejected_objects_widgets_list: List[EjectedObject] = []

        # Константа количества объектов в ряду
        self.EJECTED_OBJECTS_IN_ROW = 3 #self.spinBox_ejectedObjects_in_row.value()
        # Debug
        if Path(__file__).parent.parent.parent.joinpath("debug").is_file():
            self.work_dir = r'C:\Users\smeta\source\repos\WintreistsPractice\xgtf_video'
            self.open_xgtf_files()

    def setup_properties(self):
        self.pushButtons_set = [
            self.pushButton_set_1,
            self.pushButton_set_2,
            self.pushButton_set_3,
            self.pushButton_set_4,
        ]
        self.gridLayout_sorted_objects.setSpacing(10)
        self.gridLayout_not_sorted_objects.setSpacing(10)
        self.setStyleSheet(Path(__file__).parent.parent.joinpath("resources", "css", "Обычная тема.css").read_text())
        pass

    def setup_connections(self):
        # Кнопки
        self.pushButton_open_xgtf_files_and_load.clicked.connect(
            partial(
                self.open_work_folder, "Выберите рабочую папку:"
            )
        )
        self.pushButton_save_results.clicked.connect(self.save_results)
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
                button.setEnabled(True)
            if button == from_button:
                button.setEnabled(False)
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

        for style in Path(__file__).parent.parent.joinpath("resources", "css").glob("*.css"):
            action = QAction(
                parent=self.menu_styles,
                text=style.stem
            )
            action.triggered.connect(
                partial(
                    lambda style: self.setStyleSheet(style.read_text()),
                    style,
                )
            )
            self.menu_styles.addAction(action)
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
        save_data: Dict[List] = {}
        for widget in self.ejected_objects_widgets_list:
            for object in widget.self_object_data:
                if object.changed:
                    data = {
                        'object_id': object.object_id,
                        'uuid': object.uuid
                    }
                    if object.file_name in save_data:
                        save_data[object.file_name].append(data)
                    else:
                        save_data[object.file_name] = [data]
        for file_name in save_data:
            path_to_xgtf_file = Path(self.work_dir).joinpath(file_name.rpartition(".")[0]+".xgtf")
            make_change_uuid(path_to_xgtf_file, save_data[file_name])
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
        if self.thread_for_ejecting_sorted_objects:
            self.thread_for_ejecting_sorted_objects.interinput()
            self.thread_for_ejecting_sorted_objects.join()
        if self.thread_ejecting_object:
            self.thread_ejecting_object.interinput()
            self.thread_ejecting_object.join()
        while self.gridLayout_not_sorted_objects.count() or self.gridLayout_sorted_objects.count():
            if self.gridLayout_not_sorted_objects.count():
                widget = self.gridLayout_not_sorted_objects.takeAt(0).widget()
                if widget:
                    widget.deleteLater()
            if self.gridLayout_sorted_objects.count():
                widget = self.gridLayout_sorted_objects.takeAt(0).widget()
                if widget:
                    widget.deleteLater()
        self.ejected_objects_widgets_list.clear()
        #

        self.xgtf_file_names = self.get_xgtf_file_name()
        self.thread_for_ejecting_sorted_objects = ThreadForEjectingObjects(
            xgtf_files=[self.xgtf_file_names[0]],
            callback=partial(self.make_widget_from_data.emit, True),
        )
        self.thread_for_ejecting_sorted_objects.start()
        self.thread_ejecting_object = ThreadForEjectingObjects(
            xgtf_files=self.xgtf_file_names[1:],
            callback=partial(self.make_widget_from_data.emit, False),
            on_finish_callback=self.on_finish_thread,
        )
        self.thread_ejecting_object.start()

    def on_finish_thread(self):
        self.activateWindow()

    def show_buttons(self):
        self.pushButton_save_results.setVisible(True)

    def enable_buttons(self):
        if not self.pushButton_save_results.isEnabled():
            self.pushButton_save_results.setEnabled(True)

    def disable_buttons(self):
        self.pushButton_save_results.setEnabled(False)

    def create_new_sorted_object(self, object_data: Union[ObjectData, EjectedObjectData]):
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
                return
        self.ejected_objects_widgets_list.append(widget)
        self.sorted_lock.release()
        pass

    def create_new_not_sorted_object(self, object_data: Union[ObjectData, EjectedObjectData]):
        self.not_sorted_lock.acquire()
        grid_count = self.gridLayout_not_sorted_objects.count()
        if isinstance(object_data, ObjectData):
            if len(object_data.uuid) == UUID_LENGTH:
                self.create_new_sorted_object(object_data)
                self.not_sorted_lock.release()
                return
        widget = EjectedObject(
            object_data, self, (grid_count//self.EJECTED_OBJECTS_IN_ROW, grid_count % self.EJECTED_OBJECTS_IN_ROW), sorted=False)
        for exist_widget in self.ejected_objects_widgets_list:
            if widget.self_object_data[0].uuid == exist_widget.self_object_data[0].uuid:
                exist_widget.combine_objects(widget.self_object_data)
                self.not_sorted_lock.release()
                return

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

    def updateGridLayout(self, position: Tuple[int, int] = (0, 0), sorted: bool = False, just_update: bool = False):
        gridLayout = self.gridLayout_sorted_objects if sorted else self.gridLayout_not_sorted_objects
        widget_index = position[0] * self.EJECTED_OBJECTS_IN_ROW + position[1]
        if not just_update:
            widget = gridLayout.takeAt(widget_index).widget()
            gridLayout.removeWidget(widget)
            widget.deleteLater()
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

    def get_xgtf_file_name(self) -> List[Path]:
        return list(Path(self.work_dir).glob("*.xgtf"))

    def open_work_folder(self, caption):
        directory = QFileDialog.getExistingDirectory(self, caption, os.getcwd())
        if directory:
            self.work_dir = directory
            self.open_xgtf_files()
    
    def func_for_creating_widgets(self, sorted:bool, object_data:ObjectData):
        self.create_new_sorted_object(object_data) if sorted else self.create_new_not_sorted_object(object_data)
