from PyQt5 import QtWidgets, QtGui, uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFileDialog, QTableWidgetItem
from PyQt5.QtSql import QSqlTableModel
from datetime import datetime
from . import utils


class ImportDialog(QtWidgets.QDialog):
    def __init__(self, parent):
        super(ImportDialog, self).__init__(parent)
        uic.loadUi('src/importView.ui', self)
        self.thumbTicket = 0
        self.listing.setColumnHidden(5, True)
        self.listing.setColumnHidden(6, True)
        self.listing.selectionModel().selectionChanged.connect(
            lambda _, __: self.updatePreview())
        self.listing.setItemDelegateForColumn(
            4, utils.NonEditableDelegate(self))
        self.listing.setItemDelegateForColumn(
            2, utils.DateEditDelegate(self))
        self.openBtn.clicked.connect(self.openAction)
        self.openBtn.dragEnterEvent = self.dragEnterFileEvent
        self.openBtn.dropEvent = self.dropFileEvent
        self.buttonBox.accepted.connect(self.importAction)
        self.katalogmodel = QSqlTableModel(self)
        self.katalogmodel.setTable('catalogs')
        self.katalogmodel.select()
        self.boxCatalog.setModel(self.katalogmodel)

    def openAction(self):
        filePath = QFileDialog.getOpenFileNames(self, 'OpenFile')[0]
        [self.addPath(path) for path in filePath]

    def addPath(self, filePath):
        self.thumbTicket += 1
        fileName = utils.getFileName(filePath)
        fileThumb = utils.retrieveTempThumb(
            filePath, "import_%d" % self.thumbTicket)
        date = datetime.strftime(utils.getModifiedDate(filePath), '%Y-%m-%d')
        title = utils.getFileNameNoExt(filePath)
        index = ""
        category = ""
        items = [index, title, str(date), category,
                 fileName, filePath, fileThumb]
        row = self.listing.rowCount()
        self.listing.insertRow(row)
        for i, item in enumerate(items):
            self.listing.setItem(row, i, QTableWidgetItem(item))

    def updatePreview(self):
        rows = self.listing.selectedItems()
        if (len(rows) > 0):
            selectedIndex = self.listing.item(rows[0].row(), 0).text()
            selectedTitle = self.listing.item(rows[0].row(), 1).text()
            selectedDate = datetime.strptime(self.listing.item(
                rows[0].row(), 2).text(), '%Y-%m-%d')
            selectedThumb = self.listing.item(rows[0].row(), 6).text()

            self.fileLabel.setPixmap(QtGui.QPixmap(selectedThumb))
            self.boxTitle.setText(selectedTitle)
            self.boxIndex.setText(selectedIndex)
            self.boxDate.setDate(selectedDate)

    def importAction(self):
        for row in range(self.listing.rowCount()):
            path = self.listing.item(row, 5).text()
            title = self.listing.item(row, 1).text()
            index = self.listing.item(row, 0).text()
            date = self.listing.item(row, 2).text()
            category = self.listing.item(row, 3).text()
            utils.importDocument(path, title, index, date, category)

    def dragEnterFileEvent(self, e):
        if e.mimeData().hasUrls():
            e.setDropAction(Qt.CopyAction)
            e.accept()
        else:
            e.ignore()

    def dropFileEvent(self, e):
        files = [u.toLocalFile() for u in e.mimeData().urls()]
        im = ImportDialog(self)
        for f in files:
            im.addPath(f)
        im.exec()
        self.updateListing()
