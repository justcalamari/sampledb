#!/usr/bin/env python
import re
import os
import sys
import pandas as pd
from datetime import datetime

class DataPublisher(object):
    """
    Publish data to a database.
    """

    def __init__(self, collection):
        """
        Create a DataPublisher.
        """
        self.collection = collection
        
    @classmethod
    def parse_sheet(cls, sheet):
        """
        Converts each row in a sheet to a dictionary.
        Returns a list of the dictionaries.
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
                d[newkey] = row[1][oldkey]
            if 'date' not in d:
                d['date'] = datetime.now()
            samples.append(d)
    
        return samples
    
    
    @classmethod
    def parse_wb(cls, wb):
        """
        Converts each row in all sheets of a workbook to a dictionary.
        Returns a list of the dictionaries.
        """
        samples = []
    
        for sheet in wb.sheet_names:
            samples.extend(cls.parse_sheet(wb.parse(sheet)))
    
        return samples
    
    
    def publish(self, filename):
        """
        Publish a spreadsheet to the database.
        """
        wb = pd.ExcelFile(filename)
        for doc in self.parse_wb(wb):
            self.collection.save(doc)
