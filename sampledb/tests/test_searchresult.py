#!/usr/bin/env python
from sampledb.searchresult import SearchResult
from pandas import read_excel, notnull
from pandas import DataFrame as df
from pytest import fail


def test_filter(entries):
    sr = SearchResult(entries)
    assert sr.filter([0, 3]).results.equals(df([entries[i]
                                            for i in [0, 3]]))
    assert sr.filter([1, 4]).results.equals(df([entries[1]]))


def test_download(entries):
    sr = SearchResult(entries)
    sr.download('test.xlsx')
    wb = read_excel('test.xlsx')
    wb = wb.where(notnull(wb), None)
    wb.rename(columns={c: c.replace(' ', '_').lower() for c in wb.columns},
              inplace=True)
    assert wb.equals(df(entries))

    sr = SearchResult([])
    try:
        sr.download('test.xlsx')
    except Exception:
        fail('Trying to download an empty spreadsheet should not raise '
             'an exception.')


def test_eq(entries):
    sr = SearchResult(entries)
    assert sr == sr
    assert sr == SearchResult(entries)
    assert sr == SearchResult(entries[::-1])
    assert sr != SearchResult([])
    assert sr != SearchResult(entries[1:])
    assert sr != df(entries)
