#!/usr/bin/env python
from sampledb.searchresult import SearchResult
from sampledb.sampledatabase import SampleDatabase


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


def test_load_config(config):
    sdb = SampleDatabase.load_config(config)
    coll = sdb.publisher.collection
    db = coll.database
    addr = db.client.address
    assert coll.name == config.get('collection', 'samples')
    assert db.name == config.get('db', 'sampleDB')
    assert addr == (config.get('hostname', 'localhost'), 27017)
