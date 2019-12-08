from PyQt5 import uic
from PyQt5.QtWidgets import QDialog
import shlex
from .worker import SearchWorker
from . import utils
from datetime import datetime


class SearchDialog(QDialog):
    def __init__(self, parent, searchWorker):
        super(SearchDialog, self).__init__(parent)
        self.searchWorker = searchWorker
        uic.loadUi('src/searchView.ui', self)
        utils.populateCatalog(self.catalogEdit)
        self.read(searchWorker)

    def read(self, searchWorker: SearchWorker):
        if len(searchWorker.commons) > 0:
            self.commonEdit.setText(" ".join(
                shlex.quote(s) for s in searchWorker.commons
                ).replace("'", '"'))
        self.indexEdit.setText(searchWorker.index)
        self.titleEdit.setText(searchWorker.title)
        i = self.catalogEdit.findText(searchWorker.catalog)
        if i >= 0:
            self.catalogEdit.setCurrentIndex(i)
        if searchWorker.range is not None:
            self.dateEdit_use.setChecked(True)
            start, end = searchWorker.range
            self.dateEdit_start.setDate(datetime.strptime(start, '%Y-%m-%d'))
            self.dateEdit_end.setDate(datetime.strptime(end, '%Y-%m-%d'))
