# Form implementation generated from reading ui file 'MainWindow.ui'
#
# Created by: PyQt6 UI code generator 6.5.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1270, 889)
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_4 = QtWidgets.QLabel(parent=self.centralwidget)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout.addWidget(self.label_4)
        self.spinBox_ejectedObjects_in_row = QtWidgets.QSpinBox(parent=self.centralwidget)
        self.spinBox_ejectedObjects_in_row.setMinimum(1)
        self.spinBox_ejectedObjects_in_row.setMaximum(10)
        self.spinBox_ejectedObjects_in_row.setProperty("value", 4)
        self.spinBox_ejectedObjects_in_row.setObjectName("spinBox_ejectedObjects_in_row")
        self.horizontalLayout.addWidget(self.spinBox_ejectedObjects_in_row)
        self.label_3 = QtWidgets.QLabel(parent=self.centralwidget)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout.addWidget(self.label_3)
        self.lineEdit_work_dir = QtWidgets.QLineEdit(parent=self.centralwidget)
        self.lineEdit_work_dir.setDragEnabled(False)
        self.lineEdit_work_dir.setReadOnly(True)
        self.lineEdit_work_dir.setObjectName("lineEdit_work_dir")
        self.horizontalLayout.addWidget(self.lineEdit_work_dir)
        self.toolButton_select_work_dir = QtWidgets.QToolButton(parent=self.centralwidget)
        self.toolButton_select_work_dir.setObjectName("toolButton_select_work_dir")
        self.horizontalLayout.addWidget(self.toolButton_select_work_dir)
        self.pushButton_open_xgtf_files = QtWidgets.QPushButton(parent=self.centralwidget)
        self.pushButton_open_xgtf_files.setEnabled(False)
        self.pushButton_open_xgtf_files.setObjectName("pushButton_open_xgtf_files")
        self.horizontalLayout.addWidget(self.pushButton_open_xgtf_files)
        self.verticalLayout_5.addLayout(self.horizontalLayout)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.groupBox = QtWidgets.QGroupBox(parent=self.centralwidget)
        self.groupBox.setTitle("")
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label = QtWidgets.QLabel(parent=self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label.setObjectName("label")
        self.verticalLayout_2.addWidget(self.label)
        self.horizontalLayout_2.addWidget(self.groupBox)
        self.groupBox_2 = QtWidgets.QGroupBox(parent=self.centralwidget)
        self.groupBox_2.setTitle("")
        self.groupBox_2.setObjectName("groupBox_2")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.groupBox_2)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.label_2 = QtWidgets.QLabel(parent=self.groupBox_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.verticalLayout_3.addWidget(self.label_2)
        self.horizontalLayout_2.addWidget(self.groupBox_2)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.verticalLayout_5.addLayout(self.verticalLayout)
        self.pushButton_load_next_objects = QtWidgets.QPushButton(parent=self.centralwidget)
        self.pushButton_load_next_objects.setEnabled(False)
        self.pushButton_load_next_objects.setObjectName("pushButton_load_next_objects")
        self.verticalLayout_5.addWidget(self.pushButton_load_next_objects)
        self.pushButton_save_results = QtWidgets.QPushButton(parent=self.centralwidget)
        self.pushButton_save_results.setEnabled(False)
        self.pushButton_save_results.setObjectName("pushButton_save_results")
        self.verticalLayout_5.addWidget(self.pushButton_save_results)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(parent=MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1270, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label_4.setText(_translate("MainWindow", "Введите количество блоков в ряду"))
        self.label_3.setText(_translate("MainWindow", "Выберите рабочую папку:"))
        self.toolButton_select_work_dir.setText(_translate("MainWindow", "..."))
        self.pushButton_open_xgtf_files.setText(_translate("MainWindow", "Загрузить объекты"))
        self.label.setText(_translate("MainWindow", "Отсортированные объекты"))
        self.label_2.setText(_translate("MainWindow", "Неотсортированные объекты"))
        self.pushButton_load_next_objects.setText(_translate("MainWindow", "Загрузить следующие объекты"))
        self.pushButton_save_results.setText(_translate("MainWindow", "Сохранить результаты"))