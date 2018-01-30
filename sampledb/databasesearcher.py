#!/usr/bin/env python
from datetime import datetime
from sampledb.searchresult import SearchResult


class DatabaseSearcher(object):
    """
    Seach a MongoDB database.
    """

    def __init__(self, collection):
        """Create a DatabaseSearcher.

        Parameters
        ----------
        collection : pymongo.collection.Collection
            The MongoDB collection to search.

        Returns
        -------
        DatabaseSearcher
            A DatabaseSearcher object that searches the input MongoDB collection.
        """
        self.collection = collection

    @classmethod
    def parse_date(cls, date):
        """Convert a string in 'YYYY-MM-DD' format to a datetime object.

        Parameters
        ----------
        date : str
            A date in 'YYYY-MM-DD' format.

        Returns
        -------
        datetime
            The input date as a datetime object.
        """
        date = date.split('-')
        date = [int(i) for i in date]
        return datetime(date[0], date[1], date[2])

    @classmethod
    def date_range(cls, startdate=None, enddate=None):
        """Return a MongoDB query for entries between two dates.

        Parameters
        ----------
        startdate : str, optional
            Search for entries on or after this date, given in 'YYYY-MM-DD' format. Default is None.
        enddate : str, optional
            Search for entries on or before this date, given in 'YYYY-MM-DD' format. Default is None.

        Returns
        -------
        dict
            A MongoDB style query for entries between the two given dates.
        """
        range_ = {}
        if startdate:
            start = cls.parse_date(startdate)
            range_['$gte'] = start
        if enddate:
            end = cls.parse_date(enddate)
            range_['$lte'] = end

        if range_:
            return {'date': range_}
        else:
            return {}

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
        query = kwargs
        if 'uid' in kwargs and isinstance(kwargs['uid'], list):
            query['uid'] = {'$in': kwargs['uid']}
        dr = self.date_range(query.pop('startdate', None),
                             query.pop('enddate', None))
        query.update(dr)
        return SearchResult(list(self.collection.find(query, {'_id': 0})))
