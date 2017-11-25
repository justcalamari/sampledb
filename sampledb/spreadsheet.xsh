import pandas as pd
from time import time
from sampledb.sampledatabase import SampleDatabase

def write_sample_spreadsheet(uids):
    sdb = SampleDatabase(collection='test')
    sdb.load_schema('sample_schema.json')
    schema = sdb.get_schema()

    fields = []
    for name in schema['properties']:
        f = name.replace('_', ' ').title()
        fields.append(f)
    fields = {k:[None]*len(uids) for k in fields}
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
