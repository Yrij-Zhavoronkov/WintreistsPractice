import typing
from PyQt6.QtWidgets import QPushButton, QLineEdit, QToolButton, QListWidget, QCheckBox, QApplication, QMainWindow, QListWidgetItem
from PyQt6 import uic, QtGui
from PyQt6.QtCore import QSettings, Qt

import sys
import os
from operator import methodcaller


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('gui.ui', self)

        # Определение виджетов
        self.lineEdit_to_networks_dir = self.findChild(QLineEdit, 'lineEdit_to_networks_dir')
        self.lineEdit_to_markup_dir = self.findChild(QLineEdit, 'lineEdit_to_markup_dir')
        self.lineEdit_to_result_dir = self.findChild(QLineEdit, 'lineEdit_to_result_dir')
        self.lineEdit_path_to_epf_file = self.findChild(QLineEdit, 'lineEdit_path_to_epf_file')
        self.lineEdit_path_to_siamese_neural_network = self.findChild(QLineEdit, 'lineEdit_path_to_siamese_neural_network')
        self.lineEdit_fps = self.findChild(QLineEdit, 'lineEdit_fps')
        self.lineEdit_sensitivity_detector_stationary_objects = self.findChild(QLineEdit, 'lineEdit_sensitivity_detector_stationary_objects')
        self.lineEdit_minimum_number_of_earnings = self.findChild(QLineEdit, 'lineEdit_minimum_number_of_earnings')
        self.lineEdit_confidence_threshold = self.findChild(QLineEdit, 'lineEdit_confidence_threshold')

        self.toolButton_select_path_to_siamese_neural_network = self.findChild(QToolButton, 'toolButton_select_path_to_siamese_neural_network')
        self.toolButton_select_path_to_epf_file = self.findChild(QToolButton, 'toolButton_select_path_to_epf_file')
        self.toolButton_select_result_dir = self.findChild(QToolButton, 'toolButton_select_result_dir')
        self.toolButton_select_markup_dir = self.findChild(QToolButton, 'toolButton_select_markup_dir')
        self.toolButton_select_networks_dir = self.findChild(QToolButton, 'toolButton_select_networks_dir')

        self.pushButton_start_work = self.findChild(QPushButton, 'pushButton_start_work')

        self.checkBox_hide_stationary_objects = self.findChild(QCheckBox, 'checkBox_hide_stationary_objects')

        self.listWidget_testing_classes = self.findChild(QListWidget, 'listWidget_testing_classes')
        self.checkBox_hide_stationary_objects.isChecked
        # ~~~~~
        # Загрузка состояния виджетов
        # self.loadState()
        # ~~~~~
        self.test_save()


    def _get_saving_types(self) -> list:
        return [
            (QLineEdit, ["setText", "text"]),
            (QCheckBox, ["setChecked", "isChecked"]),
            (QListWidget, ["addItems"]),
        ]
    
    def test_save(self):
        import pickle as pk
        with open('test.pkl', 'wb') as f:
            items = []
            for index in range(self.listWidget_testing_classes.count()):
                items.append(self.listWidget_testing_classes.item(index))
            pk.dump(items, f)

    
    def loadState(self):
        settings = QSettings('gui_for_tester_tracker.ini', QSettings.Format.IniFormat)
        print(settings.fileName())
        for type, method in self._get_saving_types():
            for widget in self.findChildren(type):
                if settings.value(widget.objectName()) is not None:
                    methodcaller(method[0], settings.value(widget.objectName()))(widget)
        pass
    
    def saveState(self):
        settings = QSettings('gui_for_tester_tracker.ini', QSettings.Format.IniFormat)
        for type, method in self._get_saving_types():
            for widget in self.findChildren(type):
                if isinstance(widget, QListWidget):
                    items = []
                    for index in range(widget.count()):
                        items.append(widget.item(index))
                    settings.setValue(widget.objectName(), items)
                    pass
                else:
                    settings.setValue(widget.objectName(), methodcaller(method[1])(widget))
        settings.sync()

    def closeEvent(self, event):
        self.saveState()
        

if __name__ == '__main__':
    os.chdir(os.path.realpath(__file__[:__file__.rfind("\\")]))
    app = QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon('icon.png'))
    window = MainWindow()
    window.show()
    app.exec()

