from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel
from PyQt5.QtWidgets import QMessageBox, QMainWindow
import os
from . import utils
from .importDialog import ImportDialog
from .catalogDialog import CatalogDialog
from datetime import datetime


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('src/mainView.ui', self)
        self.selectedDoc = ''
        self.mute = False
        self.openDB()
        self.updateListing()
        self.addBtn.clicked.connect(self.importAction)
        self.delBtn.clicked.connect(self.deleteAction)
        self.listing.selectionModel().selectionChanged.connect(
            lambda _, __: self.updatePreview())
        self.addBtn.dragEnterEvent = self.dragEnterFileEvent
        self.addBtn.dropEvent = self.dropFileEvent
        self.addBtn.setAcceptDrops(True)
        self.actionKatalog.triggered.connect(self.katalogAction)
        self.boxPreview.mouseDoubleClickEvent = lambda e: self.openDoc()
        self.boxOpen.clicked.connect(self.openDoc)
        self.boxFrame.resizeEvent = lambda e: self.resizeDock()
        self.searchBox.textChanged.connect(self.updateListing)
        self.boxTitle.textChanged.connect(lambda x: self.updateFromBox())
        self.boxIndex.textChanged.connect(lambda x: self.updateFromBox())
        self.boxDate.dateChanged.connect(lambda x: self.updateFromBox())
        self.boxCatalog.currentIndexChanged.connect(
            lambda x: self.updateFromBox())
        self.show()

    def openDoc(self):
        os.startfile(self.selectedDoc)

    def resizeDock(self):
        if hasattr(self, 'selectedThumb'):
            self.boxPreview.setPixmap(self.selectedThumb.scaledToWidth(
                self.boxPreview.width()))

    def openDB(self):
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName("mainDB.sqlite")
        self.db.open()

    def updateListing(self):
        if not hasattr(self, 'model'):
            self.model = QSqlTableModel(self)
            self.model.setTable('documents')
            self.listing.setModel(self.model)
            #QSqlTableModel.dataChanged
            self.model.dataChanged.connect(lambda x, y: self.updatePreview())
            self.listing.setItemDelegateForColumn(
                0, utils.NonEditableDelegate(self))
            self.listing.setItemDelegateForColumn(
                3, utils.DateEditDelegate(self))
            self.listing.setItemDelegateForColumn(
                5, utils.NonEditableDelegate(self))
            self.listing.setItemDelegateForColumn(
                4, utils.CatalogEditDelegate(self))
        if not hasattr(self, 'katalogmodel'):
            self.katalogmodel = QSqlTableModel(self)
            self.katalogmodel.setTable('catalogs')
            self.boxCatalog.setModel(self.katalogmodel)

        f = self.searchBox.text()
        self.model.setFilter(None if f == '' else f'`index` LIKE "%{f}%" '
                             f'OR `title` LIKE "%{f}%"')
        self.katalogmodel.select()
        self.model.select()

    def updatePreview(self):
        rows = self.listing.selectionModel().selectedRows()
        if (len(rows) == 1):
            datasheet = [self.model.data(self.model.index(
                rows[0].row(), x)) for x in range(6)]
            ID, Index, Title, Date, Catalog, File = datasheet
            self.mute = True
            self.selectedDoc = utils.getDocumentPath(ID, File)
            self.selectedThumb = QPixmap(
                utils.getThumbnailPath(ID, File))
            self.boxIndex.setText(Index)
            self.boxTitle.setText(Title)
            self.boxDate.setDate(datetime.strptime(Date, '%Y-%m-%d'))
            i = self.boxCatalog.findText(Catalog)
            if i >= 0:
                self.boxCatalog.setCurrentIndex(i)
            self.mute = False
            self.boxPreview.setPixmap(self.selectedThumb.scaled(
                self.boxPreview.width(), self.boxPreview.height(),
                Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def updateFromBox(self):
        if (self.mute): return
        rows = self.listing.selectionModel().selectedRows()
        if (len(rows) == 1):
            datasheet = [self.model.data(self.model.index(
                         rows[0].row(), x)) for x in range(6)]
            datasheet[1] = self.boxIndex.text()
            datasheet[2] = self.boxTitle.text()
            datasheet[3] = datetime.strftime(
                self.boxDate.date().toPyDate(), '%Y-%m-%d')
            datasheet[4] = self.boxCatalog.currentText()
            [self.model.setData(
                self.model.index(rows[0].row(), x),
                datasheet[x]) for x in range(6)]

    def deleteAction(self):
        rows = self.listing.selectionModel().selectedRows()
        if (len(rows) > 0):
            quit_msg = "Yakin membuang %s dokumen?" % len(rows)
            reply = QMessageBox.question(
                            self, 'Konfirmasi',
                            quit_msg, QMessageBox.Yes, QMessageBox.No)
            if reply == QMessageBox.Yes:
                for row in rows:
                    r = utils.deleteDocument(self.model.data(
                        self.model.index(row.row(), 0)))
                    while not r:
                        if QMessageBox.question(
                                self, 'Konfirmasi', "Penghapusan Gagal!"
                                "Pastikan semua file tertutup. Coba lagi?",
                                QMessageBox.Yes, QMessageBox.No
                                ) == QMessageBox.No:
                            break
                        r = utils.deleteDocument(self.model.data(
                            self.model.index(row.row(), 0)))
                self.updateListing()

    def importAction(self):
        ImportDialog(self).exec()
        self.updateListing()

    def katalogAction(self):
        CatalogDialog(self).exec()
        self.updateListing()

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
