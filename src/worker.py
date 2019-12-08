import threading
import subprocess
import shlex
from . import utils
from PyQt5.QtSql import QSqlQuery
from shutil import copyfile


class DocumentImporter(threading.Thread):
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


class SearchWorker():
    def __init__(self):
        self.commons = []
        self.index = None
        self.title = None
        self.catalog = None
        self.range = None

    def escapeLike(self, word=""):
        return (word.replace("%", "%%").replace('\\', '\\\\')
                    .replace('"', '\\"'))

    def allocateWord(self, word=''):
        if ":" in word:
            key, value = word.split(':', 2)
            if key == 'index':
                self.index = value
            elif key == 'title':
                self.title = value
            elif key == 'catalog':
                self.catalog = value
            elif key == 'range':
                start, end = value.split(':', 2)
                self.range = (start, end)
        else:
            self.commons.append(word)

    def buildQuery(self):
        result = []
        if len(self.commons) > 0:
            for word in self.commons:
                e = self.escapeLike(word)
                result.append(f'(`index` LIKE "%{e}%" OR `title` '
                              f'LIKE "%{e}%" OR `catalog` LIKE "%{e}%")')
        if self.index:
            result.append(f'`index` LIKE "%{self.escapeLike(self.index)}%"')
        if self.title:
            result.append(f'`title` LIKE "%{self.escapeLike(self.title)}%"')
        if self.catalog is not None:
            result.append(f'`catalog` = "{self.escapeLike(self.catalog)}"')
        if self.range is not None:
            start, end = self.range
            result.append(f'`date` BETWEEN "{self.escapeLike(start)}"'
                          f' AND "{self.escapeLike(end)}"')
        return None if len(result) == 0 else ' AND '.join(result)

    def parse(self, query=''):
        SearchWorker.__init__(self)
        if query == '':
            return
        try:
            [self.allocateWord(word) for word in shlex.split(query)]
        except Exception:
            return
