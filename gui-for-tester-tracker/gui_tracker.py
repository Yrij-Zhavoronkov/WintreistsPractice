import sys
import os
from functools import partial
from pathlib import Path
from typing import Callable
from PyQt6.QtWidgets import (
    QLineEdit, QToolButton, QCheckBox,
    QApplication, QMainWindow, QFileDialog,
    QHBoxLayout, QWidget, QListWidgetItem,
    QSpacerItem, QSizePolicy, QMessageBox
)
from PyQt6 import QtGui
from PyQt6.QtCore import QSettings, Qt, QSize
from tester import main as testerTrackerMain
from gui import Ui_MainWindow


class MainWindow(QMainWindow, Ui_MainWindow):
    # Сигналы
    # onProgressWork = pyqtSignal(int, int, str, str)
    # ~~~~~~~
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.add_class(lambda: "Human", True, False)
        # Меню
        # Конфиг
        self.action_save_config.triggered.connect(self.save_state)
        self.action_load_config.triggered.connect(self.load_state)
        # ~~~~~
        # Сигналы
        self.toolButton_select_markup_dir.clicked.connect(
            partial(self.open_file_explorer, self.lineEdit_to_markup_dir, "Выберите путь к папке с разметкой"))
        self.toolButton_select_networks_dir.clicked.connect(
            partial(self.open_file_explorer, self.lineEdit_to_networks_dir, "Выберите путь к папке с сетями"))
        self.toolButton_select_result_dir.clicked.connect(
            partial(self.open_file_explorer, self.lineEdit_to_result_dir, "Выберите путь к папке для сохранения результатов"))
        self.toolButton_select_path_to_siamese_neural_network.clicked.connect(
            partial(self.open_file_location, self.lineEdit_path_to_siamese_neural_network, "Выберите путь к сиамской нейронной сети"))
        self.toolButton_select_path_to_epf_file.clicked.connect(
            partial(self.open_file_location, self.lineEdit_path_to_epf_file, "Выберите путь к .epf файлу", "*.epf"))
        self.toolButton_add_class.clicked.connect(
            partial(self.add_class, self.lineEdit_add_new_class.text, True, True))

        self.lineEdit_add_new_class.returnPressed.connect(
            partial(self.add_class, self.lineEdit_add_new_class.text, True, True))
        self.lineEdit_to_networks_dir.textChanged.connect(
            self.all_needed_line_edits_are_not_empty)
        self.lineEdit_to_markup_dir.textChanged.connect(
            self.all_needed_line_edits_are_not_empty)

        self.pushButton_start_work.clicked.connect(self.start_work)

    def all_needed_line_edits_are_not_empty(self):
        allNeededLineEdits = [
            self.lineEdit_to_networks_dir,
            self.lineEdit_to_markup_dir,
        ]
        is_filled = all(lineEdit.text() for lineEdit in allNeededLineEdits)
        self.pushButton_start_work.setEnabled(is_filled)

    def open_file_explorer(self, input_directory: QLineEdit, text: str = None):
        text = text if text else "Выберите директорию"
        directory = QFileDialog.getExistingDirectory(self, text)
        if directory:
            input_directory.setText(directory)

    def open_file_location(self, lineEdit_file_location: QLineEdit, text: str = None, filter: str = None):
        text = text if text else "Выберите файл"
        filter = filter if filter else None
        file_location = QFileDialog.getOpenFileName(self, text, filter=filter)
        if file_location[0]:
            lineEdit_file_location.setText(file_location[0])

    def start_work(self):
        testing_classes = []
        for index in range(self.listWidget_list_classes.count()):
            item = self.listWidget_list_classes.item(index)
            widget: ListItemClass = self.listWidget_list_classes.itemWidget(
                item)
            if widget.checkbox.isChecked():
                testing_classes.append(widget.checkbox.text())
        if len(testing_classes) == 0:
            QMessageBox.critical(
                self, "Ошибка", "Вы пытаетесь запустить тестирование без активных классов!")
            return True
        self.hide()
        testerTrackerMain(
            netsDir=self.lineEdit_to_networks_dir.text(),
            videosDir=self.lineEdit_to_markup_dir.text(),
            resDir=self.lineEdit_to_result_dir.text(),
            targetClasses=testing_classes,
            path2Epf=self.lineEdit_path_to_epf_file.text(),
            useMot=self.checkBox_use_MOT.isChecked(),
            motIouThr=float(self.lineEdit_IOU_threshold.text()),
            framerate=int(self.lineEdit_fps.text()),
            hideStillObjects=self.checkBox_hide_stationary_objects.isChecked(),
            hideStillObjectsSensitivity=float(
                self.lineEdit_sensitivity_detector_stationary_objects.text()),
            minDetectionTriggers=int(
                self.lineEdit_minimum_number_of_triggers.text()),
            confThreshold=float(self.lineEdit_confidence_threshold.text()),
            siameseFile=self.lineEdit_path_to_siamese_neural_network.text(),
            # onProgressCallback=self.onProgressWork.emit,
        )
        self.show()

    def load_state(self):
        path_to_settings = QFileDialog.getOpenFileName(
            self, 'Выберите файл настроек')
        if path_to_settings[0]:
            self.settings = QSettings(
                path_to_settings[0], QSettings.Format.IniFormat)

            self.lineEdit_to_markup_dir.setText(
                self.settings.value(self.lineEdit_to_markup_dir.objectName(), ""))
            self.lineEdit_to_networks_dir.setText(
                self.settings.value(self.lineEdit_to_networks_dir.objectName(), ""))
            self.lineEdit_to_result_dir.setText(
                self.settings.value(self.lineEdit_to_result_dir.objectName(), "/results"))
            self.lineEdit_path_to_siamese_neural_network.setText(
                self.settings.value(self.lineEdit_path_to_siamese_neural_network.objectName(), ""))
            self.lineEdit_path_to_epf_file.setText(
                self.settings.value(self.lineEdit_path_to_epf_file.objectName(), ""))
            self.lineEdit_confidence_threshold.setText(
                self.settings.value(self.lineEdit_confidence_threshold.objectName(), "0.3"))
            self.lineEdit_minimum_number_of_triggers.setText(
                self.settings.value(self.lineEdit_minimum_number_of_triggers.objectName(), "6"))
            self.lineEdit_IOU_threshold.setText(
                self.settings.value(self.lineEdit_IOU_threshold.objectName(), "0.3"))
            self.lineEdit_sensitivity_detector_stationary_objects.setText(
                self.settings.value(self.lineEdit_sensitivity_detector_stationary_objects.objectName(), "0.5"))
            self.lineEdit_fps.setText(
                self.settings.value(self.lineEdit_fps.objectName(), "13"))

            self.checkBox_hide_stationary_objects.setChecked(
                bool(self.settings.value(self.checkBox_hide_stationary_objects.objectName(), False)))
            self.checkBox_use_MOT.setChecked(
                bool(self.settings.value(self.checkBox_use_MOT.objectName(), False)))

            self.listWidget_list_classes.clear()
            items = self.settings.value(self.listWidget_list_classes.objectName(), {
                "Human": True
            })
            for class_name, check_state in items.items():
                self.add_class(lambda: class_name, check_state)

    def save_state(self):
        path_to_settings = QFileDialog.getSaveFileName(
            self, "Выберите путь\файл настроек")
        if path_to_settings[0]:
            self.settings = QSettings(
                path_to_settings[0], QSettings.Format.IniFormat)
            self.settings.setValue(self.lineEdit_confidence_threshold.objectName(),
                                   self.lineEdit_confidence_threshold.text())
            self.settings.setValue(self.lineEdit_minimum_number_of_triggers.objectName(),
                                   self.lineEdit_minimum_number_of_triggers.text())
            self.settings.setValue(self.lineEdit_IOU_threshold.objectName(),
                                   self.lineEdit_IOU_threshold.text())
            self.settings.setValue(self.lineEdit_sensitivity_detector_stationary_objects.objectName(),
                                   self.lineEdit_sensitivity_detector_stationary_objects.text())
            self.settings.setValue(self.lineEdit_fps.objectName(),
                                   self.lineEdit_fps.text())
            self.settings.setValue(self.lineEdit_path_to_siamese_neural_network.objectName(),
                                   self.lineEdit_path_to_siamese_neural_network.text())
            self.settings.setValue(self.lineEdit_path_to_epf_file.objectName(),
                                   self.lineEdit_path_to_epf_file.text())
            self.settings.setValue(self.lineEdit_to_markup_dir.objectName(),
                                   self.lineEdit_to_markup_dir.text())
            self.settings.setValue(self.lineEdit_to_networks_dir.objectName(),
                                   self.lineEdit_to_networks_dir.text())
            self.settings.setValue(self.lineEdit_to_result_dir.objectName(),
                                   self.lineEdit_to_result_dir.text())
            self.settings.setValue(self.checkBox_hide_stationary_objects.objectName(),
                                   True if self.checkBox_hide_stationary_objects.checkState() == Qt.CheckState.Checked else '')
            self.settings.setValue(self.checkBox_use_MOT.objectName(),
                                   True if self.checkBox_use_MOT.checkState() == Qt.CheckState.Checked else '')
            classes = {}
            for index in range(self.listWidget_list_classes.count()):
                item = self.listWidget_list_classes.item(index)
                widget: ListItemClass = self.listWidget_list_classes.itemWidget(
                    item)
                classes[widget.checkbox.text()] = widget.checkbox.isChecked()
            self.settings.setValue(
                self.listWidget_list_classes.objectName(), classes)

    def add_class(self, class_name: Callable[[], str], check_state, isAddedFromLineEdit=False):
        if class_name():
            widget = ListItemClass(class_name(), check_state)
            list_item = QListWidgetItem()
            list_item.setFlags(list_item.flags() & ~
                               Qt.ItemFlag.ItemIsSelectable)
            list_item.setSizeHint(QSize(0, 40))
            self.listWidget_list_classes.addItem(list_item)
            self.listWidget_list_classes.setItemWidget(list_item, widget)
            widget.toolButton.clicked.connect(
                partial(self.remove_class, list_item))
            if isAddedFromLineEdit:
                self.lineEdit_add_new_class.setText("")

    def remove_class(self, item):
        self.listWidget_list_classes.takeItem(
            self.listWidget_list_classes.row(item))


class ListItemClass(QWidget):
    def __init__(self, class_name, check_state):
        super().__init__()
        self.layout = QHBoxLayout(self)
        self.checkbox = QCheckBox(class_name)
        self.checkbox.setChecked(check_state)
        self.toolButton = QToolButton()
        self.toolButton.setText('-')
        self.spacer = QSpacerItem(
            0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.layout.addWidget(self.checkbox)
        self.layout.addItem(self.spacer)
        self.layout.addWidget(self.toolButton)


if __name__ == '__main__':
    _path = Path(__file__).parent
    app = QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon(_path.joinpath('icon.png').__str__()))
    window = MainWindow()
    window.setWindowTitle("GUI for tester tracker")
    window.show()
    app.exec()
