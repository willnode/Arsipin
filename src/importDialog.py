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
        self.mute = 0
        self.listing.setColumnHidden(5, True)
        self.listing.setColumnHidden(6, True)
        self.listing.selectionModel().selectionChanged.connect(
            lambda _, __: self.updatePreview())
        self.listing.setItemDelegateForColumn(
            2, utils.DateEditDelegate(self))
        self.listing.setItemDelegateForColumn(
            3, utils.CatalogEditDelegate(self))
        self.listing.setItemDelegateForColumn(
            4, utils.NonEditableDelegate(self))
        self.listing.cellChanged.connect(lambda x, y: self.updatePreview())
        self.openBtn.clicked.connect(self.openAction)
        self.openBtn.dragEnterEvent = self.dragEnterFileEvent
        self.openBtn.dropEvent = self.dropFileEvent
        self.delBtn.clicked.connect(self.deleteAction)
        self.buttonBox.accepted.connect(self.importAction)
        self.katalogmodel = QSqlTableModel(self)
        self.katalogmodel.setTable('catalogs')
        self.katalogmodel.select()
        self.boxCatalog.setModel(self.katalogmodel)
        self.boxTitle.textChanged.connect(lambda x: self.updateFromBox())
        self.boxIndex.textChanged.connect(lambda x: self.updateFromBox())
        self.boxDate.dateChanged.connect(lambda x: self.updateFromBox())
        self.boxCatalog.currentIndexChanged.connect(
            lambda x: self.updateFromBox())

    def openAction(self):
        filePath = QFileDialog.getOpenFileNames(self, 'OpenFile')[0]
        [self.addPath(path) for path in filePath]

    def addPath(self, filePath):
        self.thumbTicket += 1
        fileThumb = utils.retrieveTempThumb(
            filePath, "import_%d" % self.thumbTicket)
        date = datetime.strftime(utils.getModifiedDate(filePath), '%Y-%m-%d')
        title = utils.getFileNameNoExt(filePath)
        index = ""
        category = ""
        items = [index, title, str(date), category,
                 filePath, fileThumb]
        row = self.listing.rowCount()
        self.listing.insertRow(row)
        for i, item in enumerate(items):
            self.listing.setItem(row, i, QTableWidgetItem(item))

    def updatePreview(self):
        rows = self.listing.selectedItems()
        if (len(rows) > 0):
            datasheet = [self.listing.item(rows[0].row(), x)
                         .text() for x in range(6)]
            index, title, date, catalog, path, thumb = datasheet
            date = datetime.strptime(date, '%Y-%m-%d')
            self.mute += 1
            self.fileLabel.setPixmap(QtGui.QPixmap(thumb))
            if not self.boxTitle.hasFocus():
                self.boxTitle.setText(title)
            if not self.boxIndex.hasFocus():
                self.boxIndex.setText(index)
            if not self.boxDate.hasFocus():
                self.boxDate.setDate(date)
            i = self.boxCatalog.findText(catalog)
            if i >= 0:
                self.boxCatalog.setCurrentIndex(i)
            self.mute -= 1

    def importAction(self):
        for row in range(self.listing.rowCount()):
            datasheet = [self.listing.item(row, x)
                         .text() for x in range(6)]
            index, title, date, catalog, path, thumb = datasheet
            utils.importDocument(path, title, index, date, catalog)

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

    def updateFromBox(self):
        rows = self.listing.selectedItems()
        if (len(rows) > 0 and self.mute == 0):
            datasheet = [self.listing.item(rows[0].row(), x)
                         .text() for x in range(6)]
            datasheet[0] = self.boxIndex.text()
            datasheet[1] = self.boxTitle.text()
            datasheet[2] = datetime.strftime(
                self.boxDate.date().toPyDate(), '%Y-%m-%d')
            datasheet[3] = self.boxCatalog.currentText()
            [self.listing.item(rows[0].row(), x)
                         .setText(datasheet[x]) for x in range(6)]

    def deleteAction(self):
        rows = [x.row() for x in self.listing.selectedItems()]
        rows = reversed(list(set(rows)))
        for r in rows:
            self.listing.removeRow(r)
