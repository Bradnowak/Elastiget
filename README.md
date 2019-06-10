# Elastiget

Python wrapper for getting data out of a remote Elastic instance and storing it locally.  Ability to pull down documents by field name search, by label, or all documents.  Enumerates all indexes and displays them as a list to choose from.  Pick a single instance, or use \"\*\" to pull down all files  Uses Elastic's scrolling API to pull more than the default 10,000 documents.  Store returned documents as a single JSON file or multiple individual JSON files.     
