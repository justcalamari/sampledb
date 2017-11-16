import json
import pandas as pd

def write_sample_spreadsheet(uids):
    schema = json.load(open('sample_schema.json'))

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
    
    writer = pd.ExcelWriter('test.xlsx', engine='xlsxwriter')
    df.to_excel(writer, index=False)
    sheet = writer.sheets['Sheet1']
    for i, name in enumerate(df):
        width = max(len(str(val)) for val in df[name])
        width = max(width, len(name)) + 1
        sheet.set_column(i, i, width)
    writer.save()
    
    soffice 'test.xlsx'
    rm 'test.xlsx'
