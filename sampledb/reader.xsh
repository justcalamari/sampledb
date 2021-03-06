import json
import os
import argparse
import yaml
import pandas as pd
from pkg_resources import resource_string, resource_filename
from time import time
from sampledb.sampledatabase import SampleDatabase
from collections import OrderedDict


def sanitize_df(name):
    return name.replace('_', ' ').title()

def get_uid_from_qr():
    a = $(zbarcam)
    b = a.split()
    c = [z.strip('QR-Code:') for z in b]
    d = OrderedDict({})
    for z in c:
        d.update({z: None})
    return d

def write_sample_spreadsheet(uids, sdb):
    if len(uids) == 0:
        return

    sdb.load_schema(resource_filename('sampledb', 'data/sample_schema.json'))
    schema = sdb.get_schema()

    fields = []
    for name in schema['properties']:
        f = name.replace('_', ' ').title()
        fields.append(f)
    fields = {f: schema['properties'][k].get('default') for k, f
              in zip(schema['properties'], fields)}
    fields = {k: [v]*len(uids) for k, v in fields.items()}
    fields['Uid'] = list(uids)
    df = pd.DataFrame.from_records(fields)
    # Move uid to first column
    cols = [sanitize_df(n) for n in schema['order']]
    df = df[cols]

    df = df.rename(index=str,
            columns={sanitize_df(n): sanitize_df(n) + '\n(' + 
                schema['properties'][n]['description'] + ')'
                for n in schema['order'] 
                if schema['properties'][n].get('description')})

    required = schema.get('required', [])
    required = [sanitize_df(n) for n in required]
    df = df.rename(index=str,
            columns={n: n + '\n[Required]' for n in required})

    filename = str(int(time())) + '.xlsx'
    writer = pd.ExcelWriter(filename, engine='xlsxwriter')
    df.to_excel(writer, index=False)
    workbook = writer.book
    sheet = writer.sheets['Sheet1']

    req_form = workbook.add_format({
        'bold': True,
        'text_wrap': True,
        'align': 'center',
        'valign': 'vcenter',
        'border': 1,
        'bg_color': 'red'})
    nonreq_form = workbook.add_format({
        'bold': True,
        'text_wrap': True,
        'align': 'center',
        'valign': 'vcenter',
        'border': 1,
        'bg_color': 'green'})

    sheet.set_row(0, 13*max(len(name.split('\n')) for name in df))
    for i, name in enumerate(df):
        if '[Required]' in name:
            sheet.write(0, i, name, req_form)
        else:
            sheet.write(0, i, name, nonreq_form)
        n = name.split('\n')[0].replace(' ', '_').lower()
        if schema['properties'][n].get('enum'):
            sheet.data_validation(1, i, len(uids), i,
                    {'validate': 'list',
                     'source': schema['properties'][n]['enum']})
        width = max(len(str(val)) for val in df[name])
        width = max(width, max(len(n) for n in name.split('\n'))) + 1
        sheet.set_column(i, i, width)
    writer.save()

    soffice @(filename)
    sdb.publish(filename)
    rm @(filename)

def find_uids(uids, sdb):
    known = []
    unknown = []
    for uid in uids:
        if sdb.search(uid=uid).count():
            known.append(uid)
        else:
            unknown.append(uid)
    return known, unknown

def upload(sdb):
    uids = get_uid_from_qr()
    known, unknown = find_uids(uids, sdb)
    if len(known):
        print('The following sample uids were found in the database:')
    for uid in known:
        print(uid)
    write_sample_spreadsheet(unknown, sdb)

def download(filename, sdb):
    uids = get_uid_from_qr()
    _, unknown = find_uids(uids, sdb)
    if len(unknown):
        print('The following sample uids are not in the database:')
        for uid in unknown:
            print(uid)
    schema = resource_string('sampledb', 'data/sample_schema.json')
    schema = json.loads(schema)
    sdb.search(uid=list(uids)).download(filename, schema)

def upload_samples(host=None, db='sampleDB', collection='samples', key=None,
                   user=None, port=8000, config=None):
    if not config:
        with SampleDatabase(host, db, collection, key, user, port) as sdb:
            upload(sdb)
        return
    with open(config, 'r') as f:
        conf = yaml.load(f)
    with SampleDatabase.load_config(conf) as sdb:
        upload(sdb)

def download_sample_spreadsheet(filename, host=None, db='sampleDB',
                                collection='samples', key=None, user=None,
                                port=8000, config=None):
    if not config:
        with SampleDatabase(host, db, collection, key, user, port) as sdb:
            download(filename, sdb)
        return
    with open(config, 'r') as f:
        conf = yaml.load(f)
    with SampleDatabase.load_config(conf) as sdb:
        download(filename, sdb)

def add_args(parser):
    parser.add_argument('-n', '--host', default=None, 
            help='hostname or IP of the server on which the database lives.')
    parser.add_argument('-d' ,'--db', default='sampleDB',
            help='the name of the MongoDB database to publish to.')
    parser.add_argument('-c', '--collection', default='samples',
            help='the name of the MongoDB collection to publish to.')
    parser.add_argument('-k', '--key', default=None,
            help='path to the key file for authentication into the server.')
    parser.add_argument('-u', '--user', default=None,
            help='username on the server.')
    parser.add_argument('-p', '--port', default=8000,
            help='port on localhost to use as a tunnel to port 27017 on the remote server.')
    parser.add_argument('--config', nargs='?',
            const=os.path.join(os.path.expanduser('~'), '.config', 'sampledb', 'config.yml'),
            help='path to config.yml file. Defaults to ~/.config/sampledb/config.yml.')

def publish_samples():
    parser = argparse.ArgumentParser(description='Publish sample metadata \
            to a database.')
    add_args(parser)
    args = parser.parse_args()

    if args.config:
        upload_samples(args.host, args.db, args.collection, args.key,
                args.user, args.port, args.config)
    else:
        upload_samples(args.host, args.db, args.collection, args.key,
                args.user, args.port, args.config)

def download_samples():
    parser = argparse.ArgumentParser(description='Download sample metadata \
            from a database to a spreadsheet.')
    parser.add_argument('filename',
            help='the name of the spreadsheet where the sample data is to be saved.')
    add_args(parser)
    args = parser.parse_args()

    if args.config:
        download_sample_spreadsheet(args.filename, args.host, args.db,
                args.collection, args.key, args.user, args.port, args.config)
    else:
        download_sample_spreadsheet(args.filename, args.host, args.db,
                args.collection, args.key, args.user, args.port)
