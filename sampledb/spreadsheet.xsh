import json
import pandas as pd

schema = json.load(open('sample_schema.json'))

#df = DataFrame(schema)
#df.to_excel('test.xlsx')

fields = []
for name in schema:
    f = name.replace('_', ' ').title()
    fields.append(f)
df = pd.DataFrame(dict.fromkeys(fields), index=[0])

writer = pd.ExcelWriter('test.xlsx', engine='xlsxwriter')
df.to_excel(writer, index=False)
sheet = writer.sheets['Sheet1']
for i, name in enumerate(df):
    width = len(name) + 1
    sheet.set_column(i, i, width)
writer.save()

soffice 'test.xlsx'
rm 'test.xlsx'
