import pytest
import os
from datetime import datetime
from sampledb.sampledatabase import SampleDatabase


@pytest.fixture(scope='function')
def pdb():
    db = SampleDatabase(hostname=os.environ.get('Host'),
                        db='test', collection='publishtests')
    yield db
    db.publisher.collection.remove()


@pytest.fixture(scope='function')
def sdb(entries):
    db = SampleDatabase(hostname=os.environ.get('Host'),
                        db='test', collection='searchtests')
    db.searcher.collection.insert(entries)
    entries = [d.pop('_id', None) for d in entries]
    yield db
    db.searcher.collection.remove()


@pytest.fixture(scope='function')
def entries():
    return [{'date': datetime(2017, 1, 1), 'sample_name': 'Ni'},
            {'date': datetime(2017, 1, 1), 'sample_name': None},
            {'date': datetime(2017, 2, 27), 'sample_name': 'Ni'},
            {'date': datetime(2017, 2, 27), 'sample_name': None}]

@pytest.fixture(scope='function')
def config():
    return {'hostname': '0.0.0.0',
            'db': 'test_db',
            'collection': 'test_coll'}
