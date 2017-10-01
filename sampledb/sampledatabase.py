#!/usr/bin/env python
from sampledb.databasesearcher import DatabaseSearcher
from sampledb.datapublisher import DataPublisher
from pymongo import MongoClient


class SampleDatabase(object):

    def __init__(self, hostname=None, db='sampleDB', collection='samples'):
        c = MongoClient(hostname)
        collection = c[db][collection]
        self.searcher = DatabaseSearcher(collection)
        self.publisher = DataPublisher(collection)

    def search(self, **kwargs):
        return self.searcher.search(**kwargs)

    def publish(self, filename):
        self.publisher.publish(filename)
