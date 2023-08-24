from PyQt6.QtWidgets import (
    QPushButton, 
    QLineEdit, 
    QToolButton,
    QCheckBox, 
    QApplication, 
    QMainWindow, 
    QFileDialog,
    QListWidget,
    QHBoxLayout,
    QWidget,
    QListWidgetItem,
    QSpacerItem,
    QSizePolicy,)
from PyQt6 import uic, QtGui
from PyQt6.QtCore import QSettings, Qt, QSize, pyqtSignal
import sys
import os
from functools import partial
import sys
from typing import Callable
from tester import main as testerTrackerMain
from gui import Ui_MainWindow

class MainWindow(QMainWindow):
    # Сигналы
    onProgressWork = pyqtSignal(int, int, str, str)
    # ~~~~~~~
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        # Меню
        # Конфиг
        self.ui.action_save_config = self.findChild(QtGui.QAction, 'action_save_config')
        self.ui.action_save_config.triggered.connect(self.saveState)
        self.ui.action_load_config = self.findChild(QtGui.QAction, 'action_load_config')
        self.ui.action_load_config.triggered.connect(self.loadState)
        # ~~~~~
        # Сигналы
        self.ui.toolButton_select_markup_dir.clicked.connect(partial(self.openFileExplorer, self.ui.lineEdit_to_markup_dir, "Выберите путь к папке с разметкой"))
        self.ui.toolButton_select_networks_dir.clicked.connect(partial(self.openFileExplorer, self.ui.lineEdit_to_networks_dir, "Выберите путь к папке с сетями"))
        self.ui.toolButton_select_result_dir.clicked.connect(partial(self.openFileExplorer, self.ui.lineEdit_to_result_dir, "Выберите путь к папке для сохранения результатов"))
        self.ui.toolButton_select_path_to_siamese_neural_network.clicked.connect(partial(self.openFileLocation, self.ui.lineEdit_path_to_siamese_neural_network, "Выберите путь к сиамской нейронной сети"))
        self.ui.toolButton_select_path_to_epf_file.clicked.connect(partial(self.openFileLocation, self.ui.lineEdit_path_to_epf_file, "Выберите путь к .epf файлу", "*.epf"))
        self.ui.toolButton_add_class.clicked.connect(partial(self.addClass, self.ui.lineEdit_add_new_class.text, True, True))

        self.ui.lineEdit_add_new_class.returnPressed.connect(partial(self.addClass, self.ui.lineEdit_add_new_class.text, True, True))
        self.ui.lineEdit_to_networks_dir.textChanged.connect(self.allNeededLineEditsAreNotEmpty)
        self.ui.lineEdit_to_markup_dir.textChanged.connect(self.allNeededLineEditsAreNotEmpty)

        self.ui.pushButton_start_work.clicked.connect(self.startWork)
        pass
    def allNeededLineEditsAreNotEmpty(self):
        allNeededLineEdits = [
            self.ui.lineEdit_to_networks_dir,
            self.ui.lineEdit_to_markup_dir,
        ]
        is_filled = all(lineEdit.text() for lineEdit in allNeededLineEdits)
        self.ui.pushButton_start_work.setEnabled(is_filled)
        pass
    def openFileExplorer(self, input_directory:QLineEdit, text:str=None):
        text = text if text else "Выберите директорию"
        directory = QFileDialog.getExistingDirectory(self, text)
        if directory:
            input_directory.setText(directory)
        pass
    def openFileLocation(self, lineEdit_file_location:QLineEdit, text:str=None, filter:str=None):
        text = text if text else "Выберите файл"
        filter = filter if filter else None
        file_location = QFileDialog.getOpenFileName(self, text, filter=filter)
        if file_location[0]:
            lineEdit_file_location.setText(file_location[0])
        pass
    def startWork(self):
        testing_classes = []
        for index in range(self.ui.listWidget_list_classes.count()):
            item = self.ui.listWidget_list_classes.item(index)
            widget = self.ui.listWidget_list_classes.itemWidget(item)
            if widget.checkbox.isChecked():
                testing_classes.append(widget.checkbox.text())
        self.hide()
        testerTrackerMain(
            netsDir=self.ui.lineEdit_to_networks_dir.text(),
            videosDir=self.ui.lineEdit_to_markup_dir.text(),
            resDir=self.ui.lineEdit_to_result_dir.text(),
            targetClasses=testing_classes,
            path2Epf=self.ui.lineEdit_path_to_epf_file.text(),
            useMot=self.ui.checkBox_use_MOT.isChecked(),
            motIouThr=float(self.ui.lineEdit_IOU_threshold.text()),
            framerate=int(self.ui.lineEdit_fps.text()),
            hideStillObjects=self.ui.checkBox_hide_stationary_objects.isChecked(),
            hideStillObjectsSensitivity=float(self.ui.lineEdit_sensitivity_detector_stationary_objects.text()),
            minDetectionTriggers=int(self.ui.lineEdit_minimum_number_of_triggers.text()),
            confThreshold=float(self.ui.lineEdit_confidence_threshold.text()),
            siameseFile=self.ui.lineEdit_path_to_siamese_neural_network.text(),
            onProgressCallback=self.onProgressWork.emit,
        )
        self.show()
        pass
    def loadState(self):
        path_to_settings = QFileDialog.getOpenFileName(self, 'Выберите файл настроек')
        if path_to_settings[0]:
            self.settings = QSettings(path_to_settings[0], QSettings.Format.IniFormat)

            self.ui.lineEdit_to_markup_dir.setText(self.settings.value(self.ui.lineEdit_to_markup_dir.objectName(), ""))
            self.ui.lineEdit_to_networks_dir.setText(self.settings.value(self.ui.lineEdit_to_networks_dir.objectName(), ""))
            self.ui.lineEdit_to_result_dir.setText(self.settings.value(self.ui.lineEdit_to_result_dir.objectName(), "/results"))
            self.ui.lineEdit_path_to_siamese_neural_network.setText(self.settings.value(self.ui.lineEdit_path_to_siamese_neural_network.objectName(), ""))
            self.ui.lineEdit_path_to_epf_file.setText(self.settings.value(self.ui.lineEdit_path_to_epf_file.objectName(), ""))
            self.ui.lineEdit_confidence_threshold.setText(self.settings.value(self.ui.lineEdit_confidence_threshold.objectName(), "0.3"))
            self.ui.lineEdit_minimum_number_of_triggers.setText(self.settings.value(self.ui.lineEdit_minimum_number_of_triggers.objectName(), "6"))
            self.ui.lineEdit_IOU_threshold.setText(self.settings.value(self.ui.lineEdit_IOU_threshold.objectName(), "0.3"))
            self.ui.lineEdit_sensitivity_detector_stationary_objects.setText(self.settings.value(self.ui.lineEdit_sensitivity_detector_stationary_objects.objectName(), "0.5"))
            self.ui.lineEdit_fps.setText(self.settings.value(self.ui.lineEdit_fps.objectName(), "13"))

            self.ui.checkBox_hide_stationary_objects.setChecked(bool(self.settings.value(self.ui.checkBox_hide_stationary_objects.objectName(), False)))
            self.ui.checkBox_use_MOT.setChecked(bool(self.settings.value(self.ui.checkBox_use_MOT.objectName(), False)))

            self.ui.listWidget_list_classes.clear()
            items = self.settings.value(self.ui.listWidget_list_classes.objectName(), {
                "Human":True
            })
            for class_name, check_state in items.items():
                self.addClass(lambda: class_name, check_state)
        pass
    def saveState(self):
        path_to_settings = QFileDialog.getSaveFileName(self, "Выберите путь\файл настроек")
        if path_to_settings[0]:
            self.settings = QSettings(path_to_settings[0], QSettings.Format.IniFormat)

            self.settings.setValue(self.ui.lineEdit_confidence_threshold.objectName(), self.ui.lineEdit_confidence_threshold.text())
            self.settings.setValue(self.ui.lineEdit_minimum_number_of_triggers.objectName(), self.ui.lineEdit_minimum_number_of_triggers.text())
            self.settings.setValue(self.ui.lineEdit_IOU_threshold.objectName(), self.ui.lineEdit_IOU_threshold.text())
            self.settings.setValue(self.ui.lineEdit_sensitivity_detector_stationary_objects.objectName(), self.ui.lineEdit_sensitivity_detector_stationary_objects.text())
            self.settings.setValue(self.ui.lineEdit_fps.objectName(), self.ui.lineEdit_fps.text())
            self.settings.setValue(self.ui.lineEdit_path_to_siamese_neural_network.objectName(), self.ui.lineEdit_path_to_siamese_neural_network.text())
            self.settings.setValue(self.ui.lineEdit_path_to_epf_file.objectName(), self.ui.lineEdit_path_to_epf_file.text())
            self.settings.setValue(self.ui.lineEdit_to_markup_dir.objectName(), self.ui.lineEdit_to_markup_dir.text())
            self.settings.setValue(self.ui.lineEdit_to_networks_dir.objectName(), self.ui.lineEdit_to_networks_dir.text())
            self.settings.setValue(self.ui.lineEdit_to_result_dir.objectName(), self.ui.lineEdit_to_result_dir.text())

            self.settings.setValue(self.ui.checkBox_hide_stationary_objects.objectName(), True if self.ui.checkBox_hide_stationary_objects.checkState() == Qt.CheckState.Checked else '')
            self.settings.setValue(self.ui.checkBox_use_MOT.objectName(), True if self.ui.checkBox_use_MOT.checkState() == Qt.CheckState.Checked else '')

            classes = {}
            for index in range(self.ui.listWidget_list_classes.count()):
                item = self.ui.listWidget_list_classes.item(index)
                widget:ListItemClass = self.ui.listWidget_list_classes.itemWidget(item)
                classes[widget.checkbox.text()] = widget.checkbox.isChecked()
            self.settings.setValue(self.ui.listWidget_list_classes.objectName(), classes)
        pass
    def addClass(self, class_name:Callable[[], str], check_state, isAddedFromLineEdit=False):
        if class_name():
            widget = ListItemClass(class_name(), check_state)
            list_item = QListWidgetItem()
            list_item.setFlags(list_item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
            list_item.setSizeHint(QSize(0, 40))
            self.ui.listWidget_list_classes.addItem(list_item)
            self.ui.listWidget_list_classes.setItemWidget(list_item, widget)
            widget.toolButton.clicked.connect(partial(self.removeClass, list_item))
            if isAddedFromLineEdit:
                self.ui.lineEdit_add_new_class.setText("")
        pass
    def removeClass(self, item):
        self.ui.listWidget_list_classes.takeItem(self.ui.listWidget_list_classes.row(item))
        pass
    pass

class ListItemClass(QWidget):
    def __init__(self, class_name, check_state):
        super().__init__()
        self.layout = QHBoxLayout(self)
        self.checkbox = QCheckBox(class_name)
        self.checkbox.setChecked(check_state)
        self.toolButton = QToolButton()
        self.toolButton.setText('-')
        self.spacer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.layout.addWidget(self.checkbox)
        self.layout.addItem(self.spacer)
        self.layout.addWidget(self.toolButton)
        pass
    pass

path = os.path.dirname(os.path.realpath(__file__))
if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon(os.path.join(path, 'icon.png')))
    window = MainWindow()
    window.setWindowTitle("GUI for tester tracker")
    window.show()
    app.exec()

