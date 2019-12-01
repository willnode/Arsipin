from PyQt5 import QtWidgets, QtGui, uic
from PyQt5.QtWidgets import QFileDialog
import utils, os

class ImportDialog(QtWidgets.QDialog):
    def __init__(self, parent):
        super(ImportDialog, self).__init__(parent)
        uic.loadUi('importView.ui', self)
        self.openBtn.clicked.connect(self.openAction)
        self.buttonBox.accepted.connect(self.importAction)

    def openAction(self):
        filePath = QFileDialog.getOpenFileName(self, 'OpenFile')[0]
        self.addPath(filePath)

    def addPath(self, filePath):
        fileImage = utils.retrieveTempThumb(filePath, "import")
        fileDate = utils.getModifiedDate(filePath)
        self.filePath = filePath
        self.fileLabel.setPixmap(QtGui.QPixmap(fileImage))
        self.boxTitle.setText(utils.getFileNameNoExt(filePath))
        self.boxIndex.setText("")
        self.boxDate.setDate(fileDate)


    def importAction(self):
        path = self.filePath
        title = self.boxTitle.text()
        index = self.boxIndex.text()
        date = self.boxDate.date().toPyDate()
        utils.importDocument(path, title, index, date)
