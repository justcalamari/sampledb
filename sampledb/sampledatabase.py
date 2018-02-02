#!/usr/bin/env python
import json
from sampledb.databasesearcher import DatabaseSearcher
from sampledb.datapublisher import DataPublisher
from pymongo import MongoClient


class SampleDatabase(object):
    """
    Search and publish data to a MongoDB database.
    """

    def __init__(self, hostname=None, db='sampleDB', collection='samples'):
        """Create a SampleDatabase.

        Parameters
        ----------
        hostname : str, optional
            The hostname of IP address of the server hosting the database. Defaults to None, which is equivalent to localhost.
        db : str, optional
            The name of the MongoDB database. Defaults to 'sampleDB'.
        collection : str, optional
            The name of the MongoDB collection. Defaults to 'samples'.

        Returns
        -------
        SampleDatabase
            A SampleDatabase object for the specified MongoDB collection.
        """
        c = MongoClient(hostname)
        collection = c[db][collection]
        self.searcher = DatabaseSearcher(collection)
        self.publisher = DataPublisher(collection)

    def load_schema(self, schema_file):
        """Loads a json schema from a specified file as a dict.

        Parameters
        ----------
        schema_file : str
            The name of the json schema file.

        Returns
        -------
        dict
            The json schema as a dict.
        """
        with open(schema_file) as sch:
            schema = json.load(sch)
        self.publisher.schema = schema

    def get_schema(self):
        """Return the schema against which this DataPublisher validates.

        Returns
        -------
        dict
            The json schema against which this DataPublisher validates.
        """
        return self.publisher.get_schema()

    def search(self, **kwargs):
        """Search the database for entries with the specified key, value pairs. Returns a cursor with the results.
        
        Parameters
        ----------
        startdate : str
            A date in 'YYYY-MM-DD' format. Search for entries on or after this date.
        enddate : str
            A date in 'YYYY-MM-DD' format. Search for entries on or before this date.

        Returns
        -------
        SearchResult
            The entries matching the input query.
        """
        return self.searcher.search(**kwargs)

    def publish(self, filename):
        """Publish a spreadsheet to the database.

        Parameters
        ----------
        filename : str
            The name of the spreadsheet containing the data to be published.
        """
        self.publisher.publish(filename)
