# Instructions for using the Sample Database
- Log on to EC2 instance and type the following into the terminal:

    ```bash
    $ source activate sdb
    $ python
    >>> from sampledb.sampledatabase import SampleDatabase
    >>> sdb = SampleDatabase()
    ```
    
- Now you can search and publish to the database using `sdb.search()` and `sdb.publish()`
- Use `sdb.publish()` as follows:
    - `sdb.publish('<SAF_number>_sample.xlsx')`, for example, `sdb.publish('300874_sample.xlsx')`
    - This saves the samples in the spreadsheet to the database.
- Use `sdb.search()` as follows:
    - `sdb.search(key1='val1', key2='val2', key3='val3', ...)`
    - e.g.
        - `sdb.search(sample_name='Ni')`
        - `sdb.search(startdate='2017-03-24', enddate='2017-09-19')`
    - `startdate` and `enddate` are special keywords for searching by date. This finds all samples with a date on or after `startdate` 
       and on or before `enddate`. Dates must be in 'YYYY-MM-DD' format.
    - The keys your search on must match the keys used in the database. To see what keys the database is using, run `sdb.search()`, which
      returns all samples.
- You can also download searches to new spreadsheets:

    ```python
    >>> samples = sdb.search(sample_name='Ni')
    >>> samples.download('new_spreadsheet.xlsx')
    ```
    
- Before downloading data, you can filter your data further. Each sample in your search has an associated index. You can view all the samples in your
  search by printing the object. This will show you the contents of the samples and their associated indices.
    
    ```python
    >>> samples = sdb.search()
    >>> print(samples)
    >>> samples = samples.filter([1, 3, 5])
    >>> samples.download('filtered_spreadsheet.xlsx')
    ```