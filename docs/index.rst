.. sampledb documentation master file, created by
   sphinx-quickstart on Thu Nov  2 12:44:31 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to sampledb's documentation!
====================================

Installation
============

``conda install sampledb -c conda-forge``

Quickstart
==========

To start using sampledb with a remote server, create a configuration file 
in ~/.config/sampledb/config.yml. The config.yml should have the following
format:

.. code-block:: yaml
    
    hostname: <Remote server IP>
    db: sampleDB
    collection: samples
    key: <path/to/pem-key>
    user: <username on remote server>
    port: 8000

You can publish sample metadata to the database by typing
``publish_samples --config``,
and you can download sample metadata from the database to a spreadsheet by 
typing ``download_samples <spreadsheet_name.xlsx> --config``.
For more information on these commands, use ``publish_samples -h`` or 
``download_samples -h`` to display the help information.

.. toctree::
   :maxdepth: 4
   :caption: Contents:

   sampledb


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
