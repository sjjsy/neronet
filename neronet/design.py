# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'neronetgui.ui'
#
# Created: Fri Jan 29 13:48:10 2016
#      by: PyQt4 UI code generator 4.11.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(800, 600)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.submit_btn = QtGui.QPushButton(self.centralwidget)
        self.submit_btn.setGeometry(QtCore.QRect(20, 560, 281, 27))
        self.submit_btn.setObjectName(_fromUtf8("submit_btn"))
        self.line = QtGui.QFrame(self.centralwidget)
        self.line.setGeometry(QtCore.QRect(380, 30, 361, 16))
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.line_2 = QtGui.QFrame(self.centralwidget)
        self.line_2.setGeometry(QtCore.QRect(380, 190, 361, 20))
        self.line_2.setFrameShape(QtGui.QFrame.HLine)
        self.line_2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_2.setObjectName(_fromUtf8("line_2"))
        self.line_3 = QtGui.QFrame(self.centralwidget)
        self.line_3.setGeometry(QtCore.QRect(370, 40, 20, 161))
        self.line_3.setFrameShape(QtGui.QFrame.VLine)
        self.line_3.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_3.setObjectName(_fromUtf8("line_3"))
        self.line_4 = QtGui.QFrame(self.centralwidget)
        self.line_4.setGeometry(QtCore.QRect(730, 40, 20, 161))
        self.line_4.setFrameShape(QtGui.QFrame.VLine)
        self.line_4.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_4.setObjectName(_fromUtf8("line_4"))
        self.cluster_name_field = QtGui.QLineEdit(self.centralwidget)
        self.cluster_name_field.setGeometry(QtCore.QRect(620, 50, 113, 27))
        self.cluster_name_field.setObjectName(_fromUtf8("cluster_name_field"))
        self.cluster_address_field = QtGui.QLineEdit(self.centralwidget)
        self.cluster_address_field.setGeometry(QtCore.QRect(620, 80, 113, 27))
        self.cluster_address_field.setObjectName(_fromUtf8("cluster_address_field"))
        self.cluster_port_field = QtGui.QLineEdit(self.centralwidget)
        self.cluster_port_field.setGeometry(QtCore.QRect(620, 110, 113, 27))
        self.cluster_port_field.setObjectName(_fromUtf8("cluster_port_field"))
        self.cluster_add_btn = QtGui.QPushButton(self.centralwidget)
        self.cluster_add_btn.setGeometry(QtCore.QRect(620, 170, 111, 27))
        self.cluster_add_btn.setObjectName(_fromUtf8("cluster_add_btn"))
        self.exp_add_btn = QtGui.QPushButton(self.centralwidget)
        self.exp_add_btn.setGeometry(QtCore.QRect(390, 50, 111, 27))
        self.exp_add_btn.setObjectName(_fromUtf8("exp_add_btn"))
        self.cluster_type_combo = QtGui.QComboBox(self.centralwidget)
        self.cluster_type_combo.setGeometry(QtCore.QRect(620, 140, 111, 31))
        self.cluster_type_combo.setObjectName(_fromUtf8("cluster_type_combo"))
        self.cluster_type_combo.addItem(_fromUtf8(""))
        self.cluster_type_combo.addItem(_fromUtf8(""))
        self.clusters = QtGui.QListWidget(self.centralwidget)
        self.clusters.setGeometry(QtCore.QRect(220, 20, 151, 531))
        self.clusters.setObjectName(_fromUtf8("clusters"))
        self.label = QtGui.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(530, 50, 91, 21))
        self.label.setObjectName(_fromUtf8("label"))
        self.label_2 = QtGui.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(510, 80, 101, 21))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.label_3 = QtGui.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(530, 110, 81, 21))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.experiments = QtGui.QListWidget(self.centralwidget)
        self.experiments.setGeometry(QtCore.QRect(10, 20, 201, 531))
        self.experiments.setObjectName(_fromUtf8("experiments"))
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))
        self.submit_btn.setText(_translate("MainWindow", "Submit", None))
        self.cluster_port_field.setText(_translate("MainWindow", "22", None))
        self.cluster_add_btn.setText(_translate("MainWindow", "Add cluster", None))
        self.exp_add_btn.setText(_translate("MainWindow", "Add experiment", None))
        self.cluster_type_combo.setItemText(0, _translate("MainWindow", "unmanaged", None))
        self.cluster_type_combo.setItemText(1, _translate("MainWindow", "slurm", None))
        self.label.setText(_translate("MainWindow", "cluster name", None))
        self.label_2.setText(_translate("MainWindow", "cluster address", None))
        self.label_3.setText(_translate("MainWindow", "cluster port", None))

