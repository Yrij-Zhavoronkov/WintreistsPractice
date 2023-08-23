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
# from gui import Ui_MainWindow


class MainWindow(QMainWindow):

    # Сигналы
    onProgressWork = pyqtSignal(int, int, str, str)
    endWork = pyqtSignal()

    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('gui-for-tester-tracker/gui.ui', self)

        # self.ui = Ui_MainWindow()
        # self.ui.setupUi(self)

        self.settings = QSettings('gui_for_tester_tracker', QSettings.Format.IniFormat)

        # Определение виджетов
        self.pushButton_start_work = self.findChild(QPushButton, 'pushButton_start_work')

        # Tab Widget
        # Параметры тестера
        self.lineEdit_to_networks_dir = self.findChild(QLineEdit, 'lineEdit_to_networks_dir')
        self.lineEdit_to_markup_dir = self.findChild(QLineEdit, 'lineEdit_to_markup_dir')
        self.lineEdit_to_result_dir = self.findChild(QLineEdit, 'lineEdit_to_result_dir')
        self.lineEdit_path_to_epf_file = self.findChild(QLineEdit, 'lineEdit_path_to_epf_file')
        self.lineEdit_add_new_class = self.findChild(QLineEdit, 'lineEdit_add_new_class')

        self.toolButton_select_networks_dir = self.findChild(QToolButton, 'toolButton_select_networks_dir')
        self.toolButton_select_markup_dir = self.findChild(QToolButton, 'toolButton_select_markup_dir')
        self.toolButton_select_result_dir = self.findChild(QToolButton, 'toolButton_select_result_dir')
        self.toolButton_select_path_to_epf_file = self.findChild(QToolButton, 'toolButton_select_path_to_epf_file')
        self.toolButton_add_class = self.findChild(QToolButton, 'toolButton_add_class')
        
        self.listWidget_list_classes = self.findChild(QListWidget, 'listWidget_list_classes')
        
        
        # Параметры трекера
        self.checkBox_hide_stationary_objects = self.findChild(QCheckBox, 'checkBox_hide_stationary_objects')

        self.lineEdit_path_to_siamese_neural_network = self.findChild(QLineEdit, 'lineEdit_path_to_siamese_neural_network')
        self.lineEdit_fps = self.findChild(QLineEdit, 'lineEdit_fps')
        self.lineEdit_sensitivity_detector_stationary_objects = self.findChild(QLineEdit, 'lineEdit_sensitivity_detector_stationary_objects')
        self.lineEdit_minimum_number_of_triggers = self.findChild(QLineEdit, 'lineEdit_minimum_number_of_triggers')
        self.lineEdit_confidence_threshold = self.findChild(QLineEdit, 'lineEdit_confidence_threshold')

        self.toolButton_select_path_to_siamese_neural_network = self.findChild(QToolButton, 'toolButton_select_path_to_siamese_neural_network')

        # Использование MOT
        self.checkBox_use_MOT = self.findChild(QCheckBox, 'checkBox_use_MOT')

        self.lineEdit_IOU_threshold = self.findChild(QLineEdit, 'lineEdit_IOU_threshold')
        # ~~~~~
        # Загрузка состояния виджетов
        self.loadState()
        # ~~~~~
        # Свойства виджетов
        # ~~~~~~~~
        # Сигналы
        self.toolButton_select_markup_dir.clicked.connect(partial(self.openFileExplorer, self.lineEdit_to_markup_dir, "Выберите путь к папке с разметкой"))
        self.toolButton_select_networks_dir.clicked.connect(partial(self.openFileExplorer, self.lineEdit_to_networks_dir, "Выберите путь к папке с сетями"))
        self.toolButton_select_result_dir.clicked.connect(partial(self.openFileExplorer, self.lineEdit_to_result_dir, "Выберите путь к папке для сохранения результатов"))
        self.toolButton_select_path_to_siamese_neural_network.clicked.connect(partial(self.openFileLocation, self.lineEdit_path_to_siamese_neural_network, "Выберите путь к сиамской нейронной сети"))
        self.toolButton_select_path_to_epf_file.clicked.connect(partial(self.openFileLocation, self.lineEdit_path_to_epf_file, "Выберите путь к .epf файлу", "*.epf"))
        self.toolButton_add_class.clicked.connect(partial(self.addClass, self.lineEdit_add_new_class.text, False, True))

        self.lineEdit_add_new_class.returnPressed.connect(partial(self.addClass, self.lineEdit_add_new_class.text, False, True))

        self.pushButton_start_work.clicked.connect(self.startWork)

        
        # ~~~~~~~~



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
        for index in range(self.listWidget_list_classes.count()):
            item = self.listWidget_list_classes.item(index)
            widget = self.listWidget_list_classes.itemWidget(item)
            if widget.checkbox.isChecked():
                testing_classes.append(widget.checkbox.text())
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
            hideStillObjectsSensitivity=float(self.lineEdit_sensitivity_detector_stationary_objects.text()),
            minDetectionTriggers=int(self.lineEdit_minimum_number_of_triggers.text()),
            confThreshold=float(self.lineEdit_confidence_threshold.text()),
            siameseFile=self.lineEdit_path_to_siamese_neural_network.text(),
            onProgressCallback=self.onProgressWork.emit,
        )
        self.show()
        pass
    
    def loadState(self):
        self.lineEdit_to_markup_dir.setText(self.settings.value(self.lineEdit_to_markup_dir.objectName(), ""))
        self.lineEdit_to_networks_dir.setText(self.settings.value(self.lineEdit_to_networks_dir.objectName(), ""))
        self.lineEdit_to_result_dir.setText(self.settings.value(self.lineEdit_to_result_dir.objectName(), "/results"))
        self.lineEdit_path_to_siamese_neural_network.setText(self.settings.value(self.lineEdit_path_to_siamese_neural_network.objectName(), ""))
        self.lineEdit_path_to_epf_file.setText(self.settings.value(self.lineEdit_path_to_epf_file.objectName(), ""))
        self.lineEdit_confidence_threshold.setText(self.settings.value(self.lineEdit_confidence_threshold.objectName(), "0.3"))
        self.lineEdit_minimum_number_of_triggers.setText(self.settings.value(self.lineEdit_minimum_number_of_triggers.objectName(), "6"))
        self.lineEdit_IOU_threshold.setText(self.settings.value(self.lineEdit_IOU_threshold.objectName(), "0.3"))
        self.lineEdit_sensitivity_detector_stationary_objects.setText(self.settings.value(self.lineEdit_sensitivity_detector_stationary_objects.objectName(), "0.5"))
        self.lineEdit_fps.setText(self.settings.value(self.lineEdit_fps.objectName(), "13"))

        self.checkBox_hide_stationary_objects.setChecked(bool(self.settings.value(self.checkBox_hide_stationary_objects.objectName(), False)))
        self.checkBox_use_MOT.setChecked(bool(self.settings.value(self.checkBox_use_MOT.objectName(), False)))

        items = self.settings.value(self.listWidget_list_classes.objectName(), {
            "Human":True
        })
        for class_name, check_state in items.items():
            self.addClass(lambda: class_name, check_state)




    def saveState(self):
        self.settings.setValue(self.lineEdit_confidence_threshold.objectName(), self.lineEdit_confidence_threshold.text())
        self.settings.setValue(self.lineEdit_minimum_number_of_triggers.objectName(), self.lineEdit_minimum_number_of_triggers.text())
        self.settings.setValue(self.lineEdit_IOU_threshold.objectName(), self.lineEdit_IOU_threshold.text())
        self.settings.setValue(self.lineEdit_sensitivity_detector_stationary_objects.objectName(), self.lineEdit_sensitivity_detector_stationary_objects.text())
        self.settings.setValue(self.lineEdit_fps.objectName(), self.lineEdit_fps.text())
        self.settings.setValue(self.lineEdit_path_to_siamese_neural_network.objectName(), self.lineEdit_path_to_siamese_neural_network.text())
        self.settings.setValue(self.lineEdit_path_to_epf_file.objectName(), self.lineEdit_path_to_epf_file.text())
        self.settings.setValue(self.lineEdit_to_markup_dir.objectName(), self.lineEdit_to_markup_dir.text())
        self.settings.setValue(self.lineEdit_to_networks_dir.objectName(), self.lineEdit_to_networks_dir.text())
        self.settings.setValue(self.lineEdit_to_result_dir.objectName(), self.lineEdit_to_result_dir.text())

        self.settings.setValue(self.checkBox_hide_stationary_objects.objectName(), True if self.checkBox_hide_stationary_objects.checkState() == Qt.CheckState.Checked else '')
        self.settings.setValue(self.checkBox_use_MOT.objectName(), True if self.checkBox_use_MOT.checkState() == Qt.CheckState.Checked else '')

        classes = {}
        for index in range(self.listWidget_list_classes.count()):
            item = self.listWidget_list_classes.item(index)
            widget:ListItemClass = self.listWidget_list_classes.itemWidget(item)
            classes[widget.checkbox.text()] = widget.checkbox.isChecked()
        self.settings.setValue(self.listWidget_list_classes.objectName(), classes)


    def addClass(self, class_name:Callable[[None], str], check_state, isAddedFromLineEdit=False):
        widget = ListItemClass(class_name(), check_state)
        list_item = QListWidgetItem()
        list_item.setFlags(list_item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
        list_item.setSizeHint(QSize(0, 40))
        self.listWidget_list_classes.addItem(list_item)
        self.listWidget_list_classes.setItemWidget(list_item, widget)
        widget.toolButton.clicked.connect(partial(self.removeClass, list_item))
        if isAddedFromLineEdit:
            self.lineEdit_add_new_class.setText("")
        pass
    def removeClass(self, item):
        self.listWidget_list_classes.takeItem(self.listWidget_list_classes.row(item))
        pass

    def closeEvent(self, event):
        self.saveState()
        

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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon('gui-for-tester-tracker/app_icon.png'))
    window = MainWindow()
    window.show()
    app.exec()

