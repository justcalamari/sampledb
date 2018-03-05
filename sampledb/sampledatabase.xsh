#!/usr/bin/env python
import json
from sampledb.databasesearcher import DatabaseSearcher
from sampledb.datapublisher import DataPublisher
from pymongo import MongoClient


class SampleDatabase(object):

    def __init__(self, hostname=None, db='sampleDB', collection='samples', key, user, port):
        if key:
            self.server = user + '@' + hostname
            self.db = db
            self.collection = collection
            self.key = key
            self.port = port
        c = MongoClient(hostname)
        collection = c[db][collection]
        self.searcher = DatabaseSearcher(collection)
        self.publisher = DataPublisher(collection)

    def __enter__(self):
        if not self.key:
            return self
        tunnel = str(self.port) + ':localhost:27017'
        ssh -i @(self.key) -fNMS sock -L @(tunnel) @(self.server)
        c = MongoClient('localhost:' + str(self.port))
        collection = c[self.db][self.collection]
        self.searcher = DatabaseSearcher(collection)
        self.publisher = DataPublisher(collection)
        return self

    def __exit__(self, typ, value, traceback):
        if self.key:
            ssh -S sock -O exit @(self.server)

    def load_schema(self, schema_file):
        with open(schema_file) as sch:
            schema = json.load(sch)
        self.publisher.schema = schema 

    def get_schema(self):
        return self.publisher.get_schema()

    def search(self, **kwargs):
        return self.searcher.search(**kwargs)

    def publish(self, filename):
        self.publisher.publish(filename)
