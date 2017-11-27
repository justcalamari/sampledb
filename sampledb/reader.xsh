import pandas as pd
from time import time
from sampledb.sampledatabase import SampleDatabase
from collections import OrderedDict


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

    sdb.load_schema('sample_schema.json')
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
    cols = df.columns.tolist()
    cols.insert(0, cols.pop(cols.index('Uid')))
    df = df[cols]

    filename = str(int(time())) + '.xlsx'
    writer = pd.ExcelWriter(filename, engine='xlsxwriter')
    df.to_excel(writer, index=False)
    sheet = writer.sheets['Sheet1']
    for i, name in enumerate(df):
        width = max(len(str(val)) for val in df[name])
        width = max(width, len(name)) + 1
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

def upload_samples(host=None, db='sampleDB', collection='samples', key=None, user=None, port=8000):
    if key:
        server = user + '@' + host
        tunnel = str(port) + ':localhost:27017'
        ssh -i @(key) -fNMS sock -L @(tunnel) @(server)
        sdb = SampleDatabase('localhost:' + str(port), db, collection)
    else:
        sdb = SampleDatabase(host, db, collection)
    uids = get_uid_from_qr()
    known, unknown = find_uids(uids, sdb)
    if len(known):
        print('The following sample uids were found in the database:')
    for uid in known:
        print(uid)
    write_sample_spreadsheet(unknown, sdb)
    if key:
        ssh -S sock -O exit @(server)

def download_sample_spreadsheet(filename, host=None, db='sampleDB', collection='samples', key=None, user=None, port=8000):
    if key:
        server = user + '@' + host
        tunnel = str(port) + ':localhost:27017'
        ssh -i @(key) -fNMS sock -L @(tunnel) @(server)
        sdb = SampleDatabase('localhost:' + str(port), db, collection)
    else:
        sdb = SampleDatabase(host, db, collection)
    uids = get_uid_from_qr()
    _, unknown = find_uids(uids, sdb)
    if len(unknown):
        print('The following sample uids are not in the database:')
        for uid in unknown:
            print(uid)
    sdb.search(uid=list(uids)).download(filename)
    if key:
        ssh -S sock -O exit @(server)
