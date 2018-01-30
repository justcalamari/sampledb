#!/usr/bin/env python
import json
from sampledb.databasesearcher import DatabaseSearcher
from sampledb.datapublisher import DataPublisher
from pymongo import MongoClient


class SampleDatabase(object):
    """
    """

    def __init__(self, hostname=None, db='sampleDB', collection='samples'):
        """
        Parameters
        ----------

        Returns
        -------
        """
        c = MongoClient(hostname)
        collection = c[db][collection]
        self.searcher = DatabaseSearcher(collection)
        self.publisher = DataPublisher(collection)

    def load_schema(self, schema_file):
        """
        Parameters
        ----------

        Returns
        -------
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
