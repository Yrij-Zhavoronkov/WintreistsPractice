import sys
import os
from functools import partial
import subprocess as sub
from PyQt6 import uic, QtGui, QtCore
from PyQt6.QtWidgets import QMainWindow, QApplication, QPushButton, QLineEdit, QFileDialog, QMessageBox, QProgressBar


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('untitled.ui', self)


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
        pass

    def clear_all_inputs(self):
        for input in self.findChildren(QLineEdit):
            input.setText('')
        self.set_default_value()
        pass

    def start_program(self):
        if self.input_work_dir.text() == '':
            QMessageBox.critical(self, "Ошибка запуска", "Вы не ввели рабочую директорию!")
            return False
        if self.input_file_name.text() == '':
            QMessageBox.critical(self, "Ошибка запуска", "Вы не ввели название файла с результатом!")
            return False
        work_dir = os.path.join(self.input_work_dir.text())
        result_dir = os.path.join(self.input_result_dir.text(), self.input_file_name.text()+".xlsx")
        sub.run(['../venv/Scripts/python.exe', 'xgtf_to_excel.py', '--work-dir', work_dir, '--result-dir', result_dir])
        self.button_open_result_file.setVisible(True)
        self.button_open_result_file.clicked.connect(partial(self.open_result_file, result_dir))
        pass

    def open_result_file(self, file_path:str):
        os.system("start " + file_path)
        pass

if __name__ == '__main__':
    file_path = os.path.realpath(__file__[:__file__.rfind("\\")])
    os.chdir(file_path)
    app = QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon('icon.png'))
    main_window = MainWindow()
    app.exec()