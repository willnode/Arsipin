import threading
import subprocess
from . import utils
from PyQt5.QtSql import QSqlQuery
from shutil import copyfile


class documentImporter(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        # Save the file
        identity, name, path = self.state
        dest = utils.getDocumentPath(identity, name)
        copyfile(path, dest)
        thumb = utils.getThumbnailPath(identity, name)
        subprocess.run(["magick", path + "[0]", "-resize", "595x842", thumb])

    def execute(self, path, title, index, date, category):
        name = utils.getFileName(path)
        q = QSqlQuery()
        q.prepare("INSERT INTO documents VALUES (NULL, :index, "
                  ":title, :date, :category, :file)")
        q.bindValue(":index", str(index))
        q.bindValue(":title", str(title))
        q.bindValue(":date", str(date))
        q.bindValue(":category", str(category))
        q.bindValue(":file", str(name))
        if not q.exec():
            print("FAIL", q.executedQuery(), index, title, date, name)
            return
        self.state = (q.lastInsertId(), name, path)
        self.start()


def escapeLike(word=""):
    return word.replace("%", "%%").replace('\\', '\\\\').replace('"', '\\"')


def translateKeyword(word=''):
    if ":" in word:
        key, value = word.split(':', 2)
        if key == 'index':
            return f'`index` LIKE "%{escapeLike(value)}%"'
        elif key == 'title':
            return f'`title` LIKE "%{escapeLike(value)}%"'
        elif key == 'catalog':
            return f'`catalog` = "{escapeLike(value)}"'
        elif key == 'range':
            start, end = value.split(':', 2)
            return (f'`date` BETWEEN "{escapeLike(start)}"'
                    f' AND "{escapeLike(end)}"')
    e = escapeLike(word)
    return (f'(`index` LIKE "%{e}%" OR `title` '
            f'LIKE "%{e}%" OR `catalog` LIKE "%{e}%")')


def searchWorker(query=''):
    if query == '':
        return None
    outs = [translateKeyword(word) for word in query.split()]
    return " AND ".join(outs)
