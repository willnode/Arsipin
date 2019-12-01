from PyQt5 import QtWidgets, uic, QtGui, QtSql, QtCore
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel
from PyQt5.QtWidgets import QMessageBox, QItemDelegate
import sys, utils, os
from importDialog import ImportDialog
from datetime import datetime

class NonEditableDelegate(QItemDelegate):
    def editorEvent(self, event, item, option, model): return False
    def createEditor(self, parent, option, index): return None

class DateEditDelegate(QItemDelegate):
    def createEditor(self, parent, option, index): return QtWidgets.QDateEdit(parent=parent)
    def updateEditorGeometry(self, editor, option, index): editor.setGeometry(option.rect)

class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        self.openDB()

        #QItemDelegate.cre
        super(Ui, self).__init__()
        uic.loadUi('mainView.ui', self)
        self.updateListing()
        self.addBtn.clicked.connect(self.importAction)
        self.delBtn.clicked.connect(self.deleteAction)
        self.listing.selectionModel().selectionChanged.connect(lambda _,__: self.updatePreview())
        self.addBtn.dragEnterEvent = self.dragEnterFileEvent
        self.addBtn.dropEvent = self.dropFileEvent
        self.addBtn.setAcceptDrops(True)
        self.boxPreview.mouseDoubleClickEvent = self.openDoc
        self.boxFrame.resizeEvent = self.resizeDock
        self.searchBox.textChanged.connect(self.updateListing)
        self.show()


    def dragEnterFileEvent(self, e):
        # if e.mimeData().hasUrls():
            e.setDropAction(QtCore.Qt.CopyAction)
            e.accept()
        # else:
        #     e.ignore()

    def dropFileEvent(self, e):
        files = [u.toLocalFile() for u in e.mimeData().urls()]
        for f in files:
            print(f)

    def openDoc(self, event):
        os.startfile(self.selectedDoc)

    def resizeDock(self, event):
        if hasattr(self, 'selectedThumb'):
            self.boxPreview.setPixmap(self.selectedThumb.scaledToWidth(self.boxPreview.width()))

    def openDB(self):
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName("mainDB.sqlite")
        self.db.open()

    def updateListing(self):
        if not hasattr(self, 'model'):
            self.model = QSqlTableModel(self)
            self.model.setTable('documents')
            self.listing.setModel(self.model)
            self.listing.setItemDelegateForColumn(0, NonEditableDelegate(self))
            self.listing.setItemDelegateForColumn(3, DateEditDelegate(self))
            self.listing.setItemDelegateForColumn(4, NonEditableDelegate(self))

        filt = self.searchBox.text()
        self.model.setFilter(None if filt == '' else '`index` LIKE "%%%s%%" OR `title` LIKE "%%%s%%"' % (filt, filt))
        self.model.select()

    def updatePreview(self):
        rows = self.listing.selectionModel().selectedRows()
        if (len(rows) == 1):
            selectedID = self.model.data(self.model.index(rows[0].row(), 0))
            selectedIndex = self.model.data(self.model.index(rows[0].row(), 1))
            selectedTitle = self.model.data(self.model.index(rows[0].row(), 2))
            selectedDate = self.model.data(self.model.index(rows[0].row(), 3))
            selectedFile = self.model.data(self.model.index(rows[0].row(), 4))
            self.selectedDoc = utils.getDocumentPath(selectedID, selectedFile)
            self.selectedThumb = QtGui.QPixmap(utils.getThumbnailPath(selectedID, selectedFile))
            self.boxTitle.setText(selectedTitle)
            self.boxIndex.setText(selectedIndex)
            self.boxDate.setDate(datetime.strptime(selectedDate, '%Y-%m-%d'))
            self.boxPreview.setPixmap(self.selectedThumb.scaledToWidth(self.boxPreview.width()))


    def deleteAction(self):
        rows = self.listing.selectionModel().selectedRows()
        if (len(rows) > 0):
            quit_msg = "Yakin membuang %s dokumen?" % len(rows)
            reply = QMessageBox.question(self, 'Konfirmasi',
                            quit_msg, QMessageBox.Yes, QMessageBox.No)

            if reply == QMessageBox.Yes:
                for row in rows:
                    r = utils.deleteDocument(self.model.data(self.model.index(row.row(), 0)))
                    while not r:
                        if QMessageBox.question(self, 'Konfirmasi',
                            "Penghapusan Gagal! Pastikan semua file tertutup. Coba lagi?", QMessageBox.Yes, QMessageBox.No) == QMessageBox.No:
                            break
                        r = utils.deleteDocument(self.model.data(self.model.index(row.row(), 0)))
                self.updateListing()


    def importAction(self):
        ImportDialog(self).exec()
        self.updateListing()


app = QtWidgets.QApplication(sys.argv)
window = Ui()
app.exec_()