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

    def Abort(self):
        transaction.abort()

    def Commit(self):
        transaction.commit()

    def StoreAssay(self, assayToStore):
        self.dbroot[assayToStore.name] = assayToStore
        self.dbroot[assayToStore.name].stored = True
        transaction.commit()

    def RemoveAssay(self, assayToRemove):
        del self.dbroot[assayToRemove]

    def FetchDB(self):
        return self.dbroot

    def SearchAssay(self, assayName):
        return False if not self.dbroot.get(assayName) else True

    def SearchSample(self, assayName, sampleName):
        assay = self.dbroot.get(assayName)
        sampleNames = [sample['Name'] for sample in assay.samples]
        return True if sampleName in sampleNames else False

    def FetchAssay(self, assayName):
        return self.dbroot.get(assayName)

