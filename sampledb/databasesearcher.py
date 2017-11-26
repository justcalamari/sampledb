#!/usr/bin/env python
from datetime import datetime
from sampledb.searchresult import SearchResult


class DatabaseSearcher(object):
    """
    Seach a database.
    """

    def __init__(self, collection):
        """
        Create a DatabaseSearcher.
        """
        self.collection = collection

    @classmethod
    def parse_date(cls, date):
        """
        Convert a string in 'YYYY-MM-DD' format to a datetime object.
        """
        date = date.split('-')
        date = [int(i) for i in date]
        return datetime(date[0], date[1], date[2])

    @classmethod
    def date_range(cls, startdate=None, enddate=None):
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
        """
        Search the database for entries with the specified key, value pairs.
        Returns a cursor with the results.
        """
        query = kwargs
        if 'uid' in kwargs and type(kwargs['uid']) == type([]):
            query['uid'] = {'$in': kwargs['uid']}
        dr = self.date_range(query.pop('startdate', None),
                             query.pop('enddate', None))
        query.update(dr)
        return SearchResult(list(self.collection.find(query, {'_id': 0})))
