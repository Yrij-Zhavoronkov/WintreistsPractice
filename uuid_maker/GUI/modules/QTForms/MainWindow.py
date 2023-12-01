# Form implementation generated from reading ui file 'C:\Users\smeta\source\repos\WintreistsPractice\uuid_maker\GUI\modules\QTForms\MainWindow.ui'
#
# Created by: PyQt6 UI code generator 6.6.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(938, 542)
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.label_6 = QtWidgets.QLabel(parent=self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_6.sizePolicy().hasHeightForWidth())
        self.label_6.setSizePolicy(sizePolicy)
        self.label_6.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_6.setObjectName("label_6")
        self.verticalLayout_4.addWidget(self.label_6)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.pushButton_open_xgtf_files_and_load = QtWidgets.QPushButton(parent=self.centralwidget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.pushButton_open_xgtf_files_and_load.setFont(font)
        self.pushButton_open_xgtf_files_and_load.setLayoutDirection(QtCore.Qt.LayoutDirection.LeftToRight)
        self.pushButton_open_xgtf_files_and_load.setAutoFillBackground(False)
        self.pushButton_open_xgtf_files_and_load.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/Images/open_files.svg"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.pushButton_open_xgtf_files_and_load.setIcon(icon)
        self.pushButton_open_xgtf_files_and_load.setIconSize(QtCore.QSize(32, 32))
        self.pushButton_open_xgtf_files_and_load.setObjectName("pushButton_open_xgtf_files_and_load")
        self.horizontalLayout_4.addWidget(self.pushButton_open_xgtf_files_and_load)
        self.pushButton_save_results = QtWidgets.QPushButton(parent=self.centralwidget)
        self.pushButton_save_results.setEnabled(True)
        self.pushButton_save_results.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/Images/save_files.svg"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.pushButton_save_results.setIcon(icon1)
        self.pushButton_save_results.setIconSize(QtCore.QSize(32, 32))
        self.pushButton_save_results.setObjectName("pushButton_save_results")
        self.horizontalLayout_4.addWidget(self.pushButton_save_results)
        self.verticalLayout_4.addLayout(self.horizontalLayout_4)
        self.horizontalLayout.addLayout(self.verticalLayout_4)
        self.frame = QtWidgets.QFrame(parent=self.centralwidget)
        self.frame.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.frame.setObjectName("frame")
        self.horizontalLayout.addWidget(self.frame)
        self.line = QtWidgets.QFrame(parent=self.centralwidget)
        self.line.setFrameShape(QtWidgets.QFrame.Shape.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.line.setObjectName("line")
        self.horizontalLayout.addWidget(self.line)
        self.verticalLayout_6 = QtWidgets.QVBoxLayout()
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.label_4 = QtWidgets.QLabel(parent=self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy)
        self.label_4.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_4.setObjectName("label_4")
        self.verticalLayout_6.addWidget(self.label_4)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetMaximumSize)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.pushButton_set_1 = QtWidgets.QPushButton(parent=self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Maximum, QtWidgets.QSizePolicy.Policy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_set_1.sizePolicy().hasHeightForWidth())
        self.pushButton_set_1.setSizePolicy(sizePolicy)
        self.pushButton_set_1.setText("")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/Images/1x1.bmp"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.pushButton_set_1.setIcon(icon2)
        self.pushButton_set_1.setIconSize(QtCore.QSize(32, 32))
        self.pushButton_set_1.setCheckable(True)
        self.pushButton_set_1.setObjectName("pushButton_set_1")
        self.horizontalLayout_3.addWidget(self.pushButton_set_1)
        self.pushButton_set_2 = QtWidgets.QPushButton(parent=self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Maximum, QtWidgets.QSizePolicy.Policy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_set_2.sizePolicy().hasHeightForWidth())
        self.pushButton_set_2.setSizePolicy(sizePolicy)
        self.pushButton_set_2.setText("")
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/Images/2x2.bmp"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.pushButton_set_2.setIcon(icon3)
        self.pushButton_set_2.setIconSize(QtCore.QSize(32, 32))
        self.pushButton_set_2.setCheckable(True)
        self.pushButton_set_2.setObjectName("pushButton_set_2")
        self.horizontalLayout_3.addWidget(self.pushButton_set_2)
        self.pushButton_set_3 = QtWidgets.QPushButton(parent=self.centralwidget)
        self.pushButton_set_3.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Maximum, QtWidgets.QSizePolicy.Policy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_set_3.sizePolicy().hasHeightForWidth())
        self.pushButton_set_3.setSizePolicy(sizePolicy)
        self.pushButton_set_3.setText("")
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(":/Images/3x3.bmp"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.pushButton_set_3.setIcon(icon4)
        self.pushButton_set_3.setIconSize(QtCore.QSize(32, 32))
        self.pushButton_set_3.setCheckable(True)
        self.pushButton_set_3.setChecked(True)
        self.pushButton_set_3.setObjectName("pushButton_set_3")
        self.horizontalLayout_3.addWidget(self.pushButton_set_3)
        self.pushButton_set_4 = QtWidgets.QPushButton(parent=self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Maximum, QtWidgets.QSizePolicy.Policy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_set_4.sizePolicy().hasHeightForWidth())
        self.pushButton_set_4.setSizePolicy(sizePolicy)
        self.pushButton_set_4.setText("")
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(":/Images/4x4.bmp"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.pushButton_set_4.setIcon(icon5)
        self.pushButton_set_4.setIconSize(QtCore.QSize(32, 32))
        self.pushButton_set_4.setCheckable(True)
        self.pushButton_set_4.setObjectName("pushButton_set_4")
        self.horizontalLayout_3.addWidget(self.pushButton_set_4)
        self.verticalLayout_6.addLayout(self.horizontalLayout_3)
        self.horizontalLayout.addLayout(self.verticalLayout_6)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout_5.addLayout(self.horizontalLayout)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.groupBox = QtWidgets.QGroupBox(parent=self.centralwidget)
        self.groupBox.setTitle("")
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetMaximumSize)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 1)
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
        self.verticalLayout_3.setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetMaximumSize)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 1)
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
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(parent=MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 938, 21))
        self.menubar.setObjectName("menubar")
        self.menu = QtWidgets.QMenu(parent=self.menubar)
        self.menu.setObjectName("menu")
        self.menu_styles = QtWidgets.QMenu(parent=self.menu)
        self.menu_styles.setObjectName("menu_styles")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.action_2 = QtGui.QAction(parent=MainWindow)
        self.action_2.setObjectName("action_2")
        self.menu.addAction(self.menu_styles.menuAction())
        self.menubar.addAction(self.menu.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "XGTFUuidCombiner"))
        self.label_6.setText(_translate("MainWindow", "Файлы xgtf"))
        self.pushButton_open_xgtf_files_and_load.setToolTip(_translate("MainWindow", "Открыть папку с файлами xgtf"))
        self.pushButton_save_results.setToolTip(_translate("MainWindow", "Сохранить результаты"))
        self.label_4.setText(_translate("MainWindow", "Вид интерфейса"))
        self.pushButton_set_1.setToolTip(_translate("MainWindow", "Устанавливает один столбец объектов"))
        self.pushButton_set_2.setToolTip(_translate("MainWindow", "Устанавливает два столбеца объектов"))
        self.pushButton_set_3.setToolTip(_translate("MainWindow", "Устанавливает три столбеца объектов"))
        self.pushButton_set_4.setToolTip(_translate("MainWindow", "Устанавливает четыре столбца объектов"))
        self.label.setText(_translate("MainWindow", "Отсортированные объекты"))
        self.label_2.setText(_translate("MainWindow", "Неотсортированные объекты"))
        self.menu.setTitle(_translate("MainWindow", "Меню"))
        self.menu_styles.setTitle(_translate("MainWindow", "Стили"))
        self.action_2.setText(_translate("MainWindow", "Основная тема"))