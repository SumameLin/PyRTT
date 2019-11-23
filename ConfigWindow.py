# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ConfigWindow.ui'
#
# Created by: PyQt5 UI code generator 5.13.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(402, 168)
        self.groupBox = QtWidgets.QGroupBox(Dialog)
        self.groupBox.setGeometry(QtCore.QRect(50, 10, 311, 81))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.groupBox.setFont(font)
        self.groupBox.setObjectName("groupBox")
        self.cmbTarget = QtWidgets.QComboBox(self.groupBox)
        self.cmbTarget.setGeometry(QtCore.QRect(10, 30, 141, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.cmbTarget.setFont(font)
        self.cmbTarget.setEditable(True)
        self.cmbTarget.setObjectName("cmbTarget")
        self.cmbTarget.addItem("")
        self.cmbTarget.addItem("")
        self.cmbSpeed = QtWidgets.QComboBox(self.groupBox)
        self.cmbSpeed.setGeometry(QtCore.QRect(180, 30, 111, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.cmbSpeed.setFont(font)
        self.cmbSpeed.setObjectName("cmbSpeed")
        self.cmbSpeed.addItem("")
        self.cmbSpeed.addItem("")
        self.cmbSpeed.addItem("")
        self.cmbSpeed.addItem("")
        self.cmbSpeed.addItem("")
        self.cmbSpeed.addItem("")
        self.cmbSpeed.addItem("")
        self.cmbSpeed.addItem("")
        self.btnOK = QtWidgets.QPushButton(Dialog)
        self.btnOK.setGeometry(QtCore.QRect(70, 110, 91, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.btnOK.setFont(font)
        self.btnOK.setFlat(False)
        self.btnOK.setObjectName("btnOK")
        self.btnCancel = QtWidgets.QPushButton(Dialog)
        self.btnCancel.setGeometry(QtCore.QRect(260, 110, 91, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.btnCancel.setFont(font)
        self.btnCancel.setFlat(False)
        self.btnCancel.setObjectName("btnCancel")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.groupBox.setTitle(_translate("Dialog", "目标芯片 & 速度"))
        self.cmbTarget.setItemText(0, _translate("Dialog", "STM32F103CB"))
        self.cmbTarget.setItemText(1, _translate("Dialog", "STM32F407VE"))
        self.cmbSpeed.setItemText(0, _translate("Dialog", "9600KHz"))
        self.cmbSpeed.setItemText(1, _translate("Dialog", "12000KHz"))
        self.cmbSpeed.setItemText(2, _translate("Dialog", "15000KHz"))
        self.cmbSpeed.setItemText(3, _translate("Dialog", "20000KHz"))
        self.cmbSpeed.setItemText(4, _translate("Dialog", "25000KHZ"))
        self.cmbSpeed.setItemText(5, _translate("Dialog", "30000KHz"))
        self.cmbSpeed.setItemText(6, _translate("Dialog", "40000KHz"))
        self.cmbSpeed.setItemText(7, _translate("Dialog", "50000KHz"))
        self.btnOK.setText(_translate("Dialog", "确认"))
        self.btnCancel.setText(_translate("Dialog", "取消"))
