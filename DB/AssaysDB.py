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

        self.dbroot[assayToStore.name] = assayToStore
        self.dbroot[assayToStore.name].stored = True
        transaction.commit()

    def FetchAssays(self):
        return self.dbroot

