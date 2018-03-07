====================
Sampledb Change Log
====================

.. current developments

v0.1.5
====================

**Added:**

* Load remote server login information from a configuration files.
* Note the required fields in the spreadsheet used for uploading.

* Dropdown lists in spreadsheet for fields that can only take specific values.
* Quickstart info.
* Allow users to update data by uploading a spreadsheet.


**Changed:**

* Raise exception if port for ssh tunnel is already in use.

* Suppress channel 3 open failed message if mongo is not running on remote.
* Print message when attempting to download an empty spreadsheet instead of raising an error.

* Downloaded spreadsheets have columns in the correct order.


**Fixed:**

* Fixed the regex pattern for bumping the version in setup.py


**Security:**

* Use try/except/finally to make sure ssh tunnels are closed if there is an exception.




v0.1.4
====================

**Changed:**

* No changes, just testing conda-forge auto-ticker.




v0.1.3
====================

**Added:**

* License
* Requirements folder to track requirements


**Changed:**

* Sphinx theme to RTD
* QR codes are smaller now (small enough to fit on the top of a vial)




v0.1.2
====================

**Added:**

* Read QRs into a spreadsheet which is uploaded to DB
* Read QRs to query DB
* Write QRs for UIDs on stickers
* Added rever and news



