import sys
import os
from functools import partial
import subprocess as sub
from PyQt6 import uic, QtGui
from PyQt6.QtWidgets import QMainWindow, QApplication, QPushButton, QLineEdit, QFileDialog, QMessageBox, QProgressBar
from PyQt6.QtCore import pyqtSignal
from threading import Thread
from xgtf_to_excel import xgtf_to_excel_work


class MainWindow(QMainWindow):
    
    updateProgressBarSignal = pyqtSignal(int)
    endBackgroundProcess = pyqtSignal()

    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('xgtf_to_excel_dir/untitled.ui', self)

        
        # Определение виджетов
        self.input_work_dir = self.findChild(QLineEdit, "input_work_dir")
        self.input_result_dir = self.findChild(QLineEdit, "input_result_dir")
        self.input_file_name = self.findChild(QLineEdit, "input_file_name")

        self.button_select_work_dir = self.findChild(QPushButton, "button_select_work_dir")
        self.button_select_result_dir = self.findChild(QPushButton, "button_select_result_dir")
        self.button_exit = self.findChild(QPushButton, "button_exit")
        self.button_clear_input = self.findChild(QPushButton, "button_clear_input")
        self.button_start = self.findChild(QPushButton, "button_start")
        self.button_open_result_file = self.findChild(QPushButton, "button_open_result_file")

        self.progressBar = self.findChild(QProgressBar, "progressBar")
        # ~~~~~~~~
        # Значения по умолчанию
        self.set_default_value()
        # ~~~~~~~~
        # Свойства
        self.input_work_dir.setReadOnly(True)
        self.input_result_dir.setReadOnly(True)
        self.button_open_result_file.setVisible(False)
        # ~~~~~~~~
        # Сигналы

        self.button_select_work_dir.clicked.connect(partial(self.openFileExplorer, self.input_work_dir))
        self.button_select_result_dir.clicked.connect(partial(self.openFileExplorer, self.input_result_dir))
        self.button_exit.clicked.connect(self.close)
        self.button_clear_input.clicked.connect(self.clear_all_inputs)
        self.button_start.clicked.connect(self.start_program)
        # ~~~~~~~~

        self.show()
        pass

    def openFileExplorer(self, input_directory:QLineEdit):
        directory = QFileDialog.getExistingDirectory(self, "Выберите директорию")
        if directory != '':
            input_directory.setText(directory)
        pass

    def set_default_value(self):
        self.input_file_name.setText("result")
        self.input_result_dir.setText(os.getcwd())
        self.progressBar.setValue(0)
        self.button_open_result_file.setVisible(False)
        pass

    def clear_all_inputs(self):
        for input in self.findChildren(QLineEdit):
            input.setText('')
        self.set_default_value()
        pass

    def start_program(self):
        if not self.input_work_dir.text():
            QMessageBox.critical(self, "Ошибка запуска", "Вы не ввели рабочую директорию!")
            return False

        if not self.input_file_name.text():
            QMessageBox.critical(self, "Ошибка запуска", "Вы не ввели название файла с результатом!")
            return False

        self.button_start.setEnabled(False)
        work_dir = os.path.join(self.input_work_dir.text())
        result_dir = os.path.join(self.input_result_dir.text(), self.input_file_name.text() + ".xlsx")

        self.updateProgressBarSignal.connect(self.progressBar.setValue)
        self.endBackgroundProcess.connect(partial(self.endBackgroundProcessFunction, result_dir))
        self.backgroundThread = Thread(target=self.threadFunctionForBackgroundProcess, args=(work_dir, result_dir, self.updateProgressBarSignal, self.endBackgroundProcess))
        self.backgroundThread.start()

    def endBackgroundProcessFunction(self, result_dir:str):
        self.button_start.setEnabled(True)
        self.button_open_result_file.setVisible(True)
        self.button_open_result_file.clicked.connect(partial(self.open_result_file, result_dir))


    def threadFunctionForBackgroundProcess(self, work_dir:str, result_dir:str, updateSignal:pyqtSignal, endSignal:pyqtSignal):
        callback = updateSignal.emit
        xgtf_to_excel_work(work_dir, result_dir, callback)
        endSignal.emit()



    def open_result_file(self, file_path:str):
        sub.run(["start", file_path], shell=True)
        pass

if __name__ == '__main__':
    # os.chdir(os.path.realpath(__file__[:__file__.rfind("\\")]))
    app = QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon('xgtf_to_excel_dir/icon.png'))
    main_window = MainWindow()
    app.exec()