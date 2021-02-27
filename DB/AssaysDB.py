#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ZODB import FileStorage, DB
import transaction


class MyZODB(object):

    def __init__(self):

        self.storage = FileStorage.FileStorage('DB/assaysDB.fs')
        self.db = DB(self.storage)
        self.connection = self.db.open()
        self.dbroot = self.connection.root()

    def Close(self):

        self.connection.close()
        self.db.close()
        self.storage.close()

    def StoreAssay(self, assayToStore):

        if self.dbroot.get(assayToStore.name) is None:
            self.dbroot[assayToStore.name] = assayToStore
            self.dbroot[assayToStore.name].stored = True
            transaction.commit()
            return True
        else:
            return False

    def FetchDB(self):
        return self.dbroot

    def SearchAssay(self, assayName):
        if not self.dbroot.get(assayName):
            return False
        else:
            return True

    def FetchAssay(self, assayName):
        return self.dbroot.get(assayName)

