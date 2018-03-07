import json
from sampledb.databasesearcher import DatabaseSearcher
from sampledb.datapublisher import DataPublisher
from pymongo import MongoClient


class SampleDatabase(object):

    def __init__(self, hostname=None, db='sampleDB', collection='samples',
                 key=None, user=None, port=8000):
        if key:
            self.server = user + '@' + hostname
            self.db = db
            self.collection = collection
            self.key = key
            self.port = port
        self.key = key
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

    @classmethod
    def load_config(cls, config):
        host = config.get('hostname', None)
        db = config.get('db', 'sampleDB')
        coll = config.get('collection', 'samples')
        key = config.get('key', None)
        user = config.get('user', None)
        port = config.get('port', 8000)
        return cls(host, db, coll, key, user, port)

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
