from PyQt5 import uic
from PyQt5.QtSql import QSqlTableModel, QSqlQuery
from PyQt5.QtWidgets import QDialog, QInputDialog


class CatalogDialog(QDialog):
    def __init__(self, parent):
        super(CatalogDialog, self).__init__(parent)
        uic.loadUi('src/catalogView.ui', self)
        self.addBtn.clicked.connect(self.addAction)
        self.updateListing()

    def updateListing(self):
        if not hasattr(self, 'model'):
            self.model = QSqlTableModel(self)
            self.model.setTable('catalogs')
            self.model.setFilter('name != ""')
            self.listView.setModel(self.model)
        self.model.select()

    def addAction(self):
        content, ok = QInputDialog.getText(self, 'Input Dialog', 'Enter text:')
        if ok and content != '':
            q = QSqlQuery()
            q.prepare('REPLACE INTO catalogs VALUES (:name)')
            q.bindValue(':name', content)
            q.exec()
            self.updateListing()
