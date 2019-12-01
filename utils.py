from PyQt5.QtSql import QSqlQuery
from PyQt5.QtWidgets import QDateEdit, QItemDelegate
from pathlib import Path
import subprocess, os
from datetime import datetime
from shutil import copyfile

def retrieveTempThumb(path, key):
	dest = os.getcwd() + "\\temp\\thumb-%s.jpg" % key
	subprocess.run(["magick", path + "[0]", "-resize", "200x280", dest])
	return dest

def getFileNameNoExt(path):
	return Path(path).stem

def getFileName(path):
	return Path(path).name

def getModifiedDate(path):
	return datetime.fromtimestamp(os.path.getmtime(path))

def getDocumentPath(id, name): return "%s\\indexed\\documents\\%d-%s" % (os.getcwd(), id, name)
def getThumbnailPath(id, name): return "%s\\indexed\\thumbs\\%d-%s.jpg" % (os.getcwd(), id, name)

def importDocument(path, title, index, date, category):
	name = getFileName(path)
	# add to SQL
	q = QSqlQuery()
	q.prepare("INSERT INTO documents VALUES (NULL, :index, :title, :date, :file, :category)")
	q.bindValue(":index", str(index))
	q.bindValue(":title", str(title))
	q.bindValue(":date", str(date))
	q.bindValue(":category", str(category))
	q.bindValue(":file", str(name))
	if not q.exec():
		print("FAIL", q.executedQuery(), index, title, date, name)
		return
	# Save the file
	identity = q.lastInsertId()
	dest = getDocumentPath(identity, name)
	copyfile(path, dest)
	thumb = getThumbnailPath(identity, name)
	subprocess.run(["magick", path + "[0]", "-resize", "595x842", thumb])
	return identity

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
    def createEditor(self, parent, option, index): return QDateEdit(parent=parent)
    def updateEditorGeometry(self, editor, option, index): editor.setGeometry(option.rect)
