#!/usr/bin/env python
from sampledb.searchresult import SearchResult


def test_publish(pdb):
    pdb.publish('300000_sample.xlsx')
    assert pdb.publisher.collection.count() == 23


def test_search(sdb, entries):
    result = sdb.search(sample_name='Ni')
    assert result == SearchResult([entries[i] for i in [0, 2]])

    result = sdb.search(startdate='2017-01-01', enddate='2017-02-01')
    assert result == SearchResult([entries[i] for i in [0, 1]])

    result = sdb.search(enddate='2016-12-31')
    assert result == SearchResult([])

    result = sdb.search(startdate='2017-01-01', enddate='2017-03-01')
    assert result == SearchResult(entries)
