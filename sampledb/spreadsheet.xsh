import json
import pandas as pd

schema = json.load(open('sample_schema.json'))

fields = []
for name in schema:
    f = name.replace('_', ' ').title()
    fields.append(f)
df = pd.DataFrame(dict.fromkeys(fields), index=[0])
# Move uid to first column
cols = df.columns.tolist()
cols.insert(0, cols.pop(cols.index('Uid')))
df = df[cols]

writer = pd.ExcelWriter('test.xlsx', engine='xlsxwriter')
df.to_excel(writer, index=False)
sheet = writer.sheets['Sheet1']
for i, name in enumerate(df):
    width = len(name) + 1
    sheet.set_column(i, i, width)
writer.save()

soffice 'test.xlsx'
rm 'test.xlsx'
