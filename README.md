# LFCS-History
Code for the tech side of the LFCS history project.

The repo is divided in two parts, the scraping part and the webapp.
The scraping part was used to collect various pieces of information, 
and is included in case there is a need to update the information.

##Details of the webapp:
* **run.py** is the file for starting the server
* **full.py** is the code used to take information from scraped json files, and the online 
[spreadsheet](https://docs.google.com/spreadsheets/d/1bszochg8ZHpsf2phzVIw_xhKkDlNebpowGay6TVadsE/edit?usp=sharing)
and add them to the psql database. It does not have any direct relation to the webapp, 
but uses some elements of it, which is why it is placed here.
* all the flask configuration is done within **__init__.py**, for modyfing any of those settings check in there.
* **views.py** contains all the views for the frontend.
* **database.py** contains all the [SQl-Alchemy](http://www.sqlalchemy.org/) models for the database.
* **func.py** contains all the functions for interaction between the views and the database.

##Instructions to add all data from the spreadshee to the database:
1. Download the 
[spreadsheet](https://docs.google.com/spreadsheets/d/1bszochg8ZHpsf2phzVIw_xhKkDlNebpowGay6TVadsE/edit?usp=sharing)
as a tab-separated file (.tsv)
2. Create the psql database
3. Initialise the models and search using the following commands from **__init__.py**
    1. make_searchable
    2. db.configure_mappers()
    3. db.create_all()
4. Add all the people with *add_all()* from **full.py**
5. Write all the names to a file called **names.txt**, and place that in the **scraping** folder
6. Run all the scrapers with "scrapy crawl *scrapername* -o *filename*" and write their output to their respective file (see table below)
7. Move the json files to root folder, then run *build_db()* from **full.py**

| Scraper        | File         |
| -------------  |-------------  |
| grant          | grants.json   |
| grant_secondary| grant2.json   |
| exploregrant   | exploregrant.json |
| exploregrant2  | exploregrant2.json |
| research       | explorer.json |
