# @todo: replace prints with logging

from ZODB import FileStorage, DB
from zc.zlibstorage import ZlibStorage
from persistent.mapping import PersistentMapping

from utils.global_utils import DATABASE_FILE
import transaction, sys


class LogDB:
    def __init__(self, file=DATABASE_FILE):
        self.fp= file
        (self.db, self.root) = self.load(self.fp) # type: (DB, PersistentMapping)

        self.set_defaults()

    @classmethod
    def load(cls, file) -> (DB, PersistentMapping):
        # load from file
        storage= ZlibStorage(FileStorage.FileStorage(file))
        db= DB(storage)
        connection= db.open()
        root= connection.root()
        return (db,root)

    def set_defaults(self, force=False):
        from classes.database import DEFAULT_EXTRACTORS

        # clear
        if force:
            self.root['extractors'] = {}

        # set defaults
        dct= self.root.setdefault('extractors',{})
        for x,y in DEFAULT_EXTRACTORS.items():
            if x not in dct or force:
                print('adding extractor:', x,y)
                dct[x]= y

        transaction.commit()

    def clear(self, logs=False, caches=False, to_defaults=False):
        from classes.database import Extractor

        if logs:
            keys= list(self.root.get('logs', {}).keys())
            print(f'clearing {len(keys)} logs...', file=sys.stderr)
            for x in keys:
                del self.root['logs'][x]
            transaction.commit()

        if caches:
            print(f'clearing cache for {len(self.root["extractors"])} extractors...', file=sys.stderr)
            Extractor.clear_all_caches(self.root['extractors'])
            transaction.commit()

        if to_defaults:
           self.set_defaults(force=True)

    def pack(self):
        self.db.pack()