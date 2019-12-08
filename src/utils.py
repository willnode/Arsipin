from PyQt5.QtSql import QSqlQuery, QSqlTableModel
from PyQt5.QtWidgets import QDateEdit, QItemDelegate, QComboBox
from pathlib import Path
import os
from . import worker
from datetime import datetime
from subprocess import Popen


def retrieveTempThumb(path, key):
    dest = os.getcwd() + "\\temp\\thumb-%s.jpg" % key
    Popen(["magick", path + "[0]", "-resize", "200x280", dest])
    return dest


def getFileNameNoExt(path):
    return Path(path).stem


def getFileName(path):
    return Path(path).name


def getModifiedDate(path):
    return datetime.fromtimestamp(os.path.getmtime(path))


def getDocumentPath(id, name):
    return "%s\\indexed\\documents\\%d-%s" % (os.getcwd(), id, name)


def getThumbnailPath(id, name):
    return "%s\\indexed\\thumbs\\%d-%s.jpg" % (os.getcwd(), id, name)


def importDocument(path, title, index, date, category):
    worker.documentImporter().execute(path, title, index, date, category)


def deleteDocument(identity):
    try:
        # Delete File
        q = QSqlQuery()
        q.prepare("SELECT file FROM documents WHERE id=:id")
        q.bindValue(":id", identity)
        q.exec()
        if q.next():
            os.remove(getDocumentPath(identity, q.value(0)))
            os.remove(getThumbnailPath(identity, q.value(0)))
    except Exception:
        return False
    else:
        # Delete Record
        q = QSqlQuery()
        q.prepare("DELETE FROM documents WHERE id=:id")
        q.bindValue(":id", identity)
        return q.exec()


class NonEditableDelegate(QItemDelegate):
    def editorEvent(self, event, item, option, model): return False
    def createEditor(self, parent, option, index): return None


class DateEditDelegate(QItemDelegate):
    def createEditor(self, parent, option, index):
        return QDateEdit(parent=parent)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)


class CatalogEditDelegate(QItemDelegate):
    def createEditor(self, parent, option, index):
        combo = QComboBox(parent=parent)
        model = QSqlTableModel(parent)
        model.setTable('catalogs')
        model.select()
        combo.setModel(model)
        return combo

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)


def populateCatalog(comboBox):
    model = QSqlTableModel(comboBox.parent())
    model.setTable('catalogs')
    model.select()
    comboBox.setModel(model)
