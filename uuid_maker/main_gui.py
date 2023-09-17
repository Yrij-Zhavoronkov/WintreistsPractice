import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QLineEdit, QWidget, QLabel
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QPixmap
from functools import partial
import os
import typing
from pathlib import Path
import time
import io
from threading import Lock

from MainWindow import Ui_MainWindow
from EjectedObject import Ui_Form_Ejected_Object
from eject_objects_from_xgtf_and_video import eject_objects


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

        # Предустановка свойств
        self.setup_properties()

        # Установка соединений между виджетами
        self.setup_connections()

        # Создание Lock
        self.sorted_lock = Lock()
        self.not_sorted_lock = Lock()

    def setup_properties(self):
        self.pushButton_load_next_objects.setVisible(False)
        pass

    def setup_connections(self):
        # Кнопки
        self.toolButton_select_work_dir.clicked.connect(
            partial(self.set_lineEdit_text_from_button, self.lineEdit_work_dir, "Выберите рабочую папку:"))
        self.pushButton_open_xgtf_files.clicked.connect(self.open_xgtf_files)
        self.pushButton_load_next_objects.clicked.connect(
            self.continue_ejecting_objects)
        pass

    def open_xgtf_files(self):
        self.pushButton_open_xgtf_files.setEnabled(False)
        self.pushButton_load_next_objects.setVisible(False)
        self.pushButton_load_next_objects.setEnabled(False)
        # Добавить код удаления всех объектов

        self.xgtf_file_name_generator = self.get_xgtf_file_name()
        self.thread_for_ejecting_sorted_objects = ThreadForEjectingObjects(
            next(self.xgtf_file_name_generator))
        self.thread_for_ejecting_sorted_objects.callback_signal.connect(
            self.create_new_sorted_object)
        self.thread_for_ejecting_sorted_objects.start()
        self.thread_ejecting_object = ThreadForEjectingObjects(
            next(self.xgtf_file_name_generator))
        self.thread_ejecting_object.callback_signal.connect(
            self.create_new_not_sorted_object)
        self.thread_ejecting_object.finished.connect(self.on_finish_thread)
        self.thread_ejecting_object.start()
        pass

    def continue_ejecting_objects(self):
        self.pushButton_open_xgtf_files.setEnabled(False)
        self.pushButton_load_next_objects.setEnabled(False)

        self.thread_ejecting_object = ThreadForEjectingObjects(
            next(self.xgtf_file_name_generator))
        self.thread_ejecting_object.callback_signal.connect(
            self.create_new_not_sorted_object)
        self.thread_ejecting_object.finished.connect(self.on_finish_thread)
        self.thread_ejecting_object.start()

    def on_finish_thread(self):
        self.pushButton_load_next_objects.setVisible(True)
        self.pushButton_load_next_objects.setEnabled(True)
        self.pushButton_open_xgtf_files.setEnabled(True)

    def create_new_sorted_object(self, object_data: dict):
        self.sorted_lock.acquire()
        grid_count = self.gridLayout_not_sorted_objects.count()
        widget = EjectedObject(object_data, self)
        print(grid_count, grid_count//2, grid_count % 2)
        self.gridLayout_sorted_objects.addWidget(
            widget, grid_count//2, grid_count % 2)
        self.sorted_lock.release()
        pass

    def create_new_not_sorted_object(self, object_data: dict):
        self.not_sorted_lock.acquire()
        grid_count = self.gridLayout_not_sorted_objects.count()
        widget = EjectedObject(object_data, self)

        self.gridLayout_not_sorted_objects.addWidget(
            widget, grid_count//2, grid_count % 2)
        self.not_sorted_lock.release()
        pass

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
    def __init__(self, ejected_object: dict, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.setGeometry(0, 0, 100, 200)
        self.object_file_name = ejected_object['file_name']
        self.object_id = ejected_object['object_id']
        self.object_images: typing.List[io.BytesIO] = ejected_object['images']

        self.generator_for_images = self.get_image()
        self.set_next_image()
        self.thread_for_change_images = EjectedObject._ThreadForChangeImages(
            self)
        self.thread_for_change_images.signal_for_changing.connect(
            self.set_next_image)
        self.thread_for_change_images.start()

    def set_next_image(self):
        pixmap = QPixmap()
        pixmap.loadFromData(next(self.generator_for_images).getvalue())
        pixmap = pixmap.scaled(100, 200)
        self.label_image.setPixmap(pixmap)
        pass

    def get_image(self):
        while True:
            for image in self.object_images:
                yield image

    class _ThreadForChangeImages(QThread):
        signal_for_changing = pyqtSignal()

        def __init__(self, parent=None):
            super(QThread, self).__init__(parent)

        def run(self):
            while True:
                time.sleep(3)
                self.signal_for_changing.emit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
