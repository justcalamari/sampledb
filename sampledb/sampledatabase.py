#!/usr/bin/env python
import json
from sampledb.databasesearcher import DatabaseSearcher
from sampledb.datapublisher import DataPublisher
from pymongo import MongoClient


class SampleDatabase(object):

    def __init__(self, hostname=None, db='sampleDB', collection='samples'):
        c = MongoClient(hostname)
        collection = c[db][collection]
        self.searcher = DatabaseSearcher(collection)
        self.publisher = DataPublisher(collection)

    def load_schema(self, schema_file):
        schema = json.load(open(schema_file))
        self.publisher.schema = schema

    def get_schema(self):
        return self.publisher.get_schema()

    def search(self, **kwargs):
        return self.searcher.search(**kwargs)

    def publish(self, filename):
        self.publisher.publish(filename)
