#!/usr/bin/env python
import re
import pandas as pd
from datetime import datetime
from jsonschema import validate, ValidationError


class DataPublisher(object):
    """
    Publish data from a spreadsheet to a MongoDB database.
    """

    def __init__(self, collection, schema={}):
        """Create a DataPublisher.

        Parameters
        ----------
        collection : pymongo.collection.Collection
            The MongoDB collection to which data is published.
        schema : dict, optional
            A json schema against which data is validated. Defaults to an empty dict, which accepts all data.

        Returns
        -------
        DataPublisher
            A DataPublisher object that publishes to the input MongoDB collection.
        """
        self.collection = collection
        self.schema = schema

    @classmethod
    def get_SAF(cls, filename):
        """Get the SAF number of the samples in the spreadsheet if it is in the filename.

        Parameters
        ----------
        filename : str
            The name of the spreadsheet containing the data to be published.

        Returns
        -------
        str
            The SAF number of the data in the spreadsheet, or None if it cannot be found.
        """

        splt = filename.split('_')
        if len(splt) != 2:
            return None
        if splt[1] != 'sample.xlsx':
            return None
        return splt[0]

    @classmethod
    def parse_sheet(cls, sheet):
        """Converts each row in a single sheet of a workbook to a dictionary.

        Parameters
        ----------
        sheet : pandas.core.frame.DataFrame

        Returns
        -------
        list of dict
            A list of dictionaries of data for each sample in the sheet.
        """
        keys = {}
        for key in sheet.columns:
            keys[key] = re.sub('[,\s]+', '_',
                               re.split('[\(\[]', key)[0].strip()).lower()

        samples = []
        for row in sheet.iterrows():
            d = {}
            if re.match('[^\w\d]', row[1][0]):
                continue
            for oldkey, newkey in keys.items():
                if row[1][oldkey] == row[1][oldkey]:
                    d[newkey] = row[1][oldkey]
            if 'date' not in d:
                d['date'] = datetime.now()
            samples.append(d)

        return samples

    @classmethod
    def parse_wb(cls, wb):
        """Converts each row in all sheets of a workbook to a dictionary.
        Returns a list of the dictionaries.

        Parameters
        ----------
        wb : pandas.io.excel.ExcelFile

        Returns
        -------
        list of dict
            A list of dictionaries of data for each sample in a workbook.
        """
        samples = []

        for sheet in wb.sheet_names:
            samples.extend(cls.parse_sheet(wb.parse(sheet)))

        return samples

    def get_schema(self):
        """Return the schema against which this DataPublisher validates.

        Returns
        -------
        dict
            The json schema against which this DataPublisher validates.
        """
        return self.schema

    def publish(self, filename):
        """Publish a spreadsheet to the database.

        Parameters
        ----------
        filename : str
            The name of the spreadsheet containing the data to be published.
        """
        saf = self.get_SAF(filename)
        wb = pd.ExcelFile(filename)
        for doc in self.parse_wb(wb):
            if saf:
                doc['saf'] = saf
            try:
                validate(doc, self.schema)
                self.collection.save(doc)
            except ValidationError as e:
                print('Failed validating uid={}'.format(doc.get('uid')))
                raise e
