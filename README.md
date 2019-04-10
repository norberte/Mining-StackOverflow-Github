## Mining-StackOverflow-Github
This project is part of my Master's thesis project on developer expertise learning by mining Stack Overflow (SOTorrent) and Github (GHTorrent) data.

Requirements:
Set up a MySQL database on a server, and create a database with the name of your choice.
When performing data gathering and database creation have at least 500 GB of disk space available on the server.

## Data gathering and database creation phase
To download, unzip, and import all data from GHTorrent follow the instructions on the README inside Mining-StackOverflow-Github/DB creation/Github db schema/ directory.

To download, unzip, and import all data from SOTorrent follow the instructions on the README inside Mining-StackOverflow-Github/DB creation/Stack Overflow db schema/ directory.

## Data linkage phase
Run the following SQL script on the already existing database: Mining-StackOverflow-Github/DB creation/SO-GH_linkage.sql

## Table stitching phase
Run the following SQL script on the already linked database: Mining-StackOverflow-Github/DB creation/SO-GH_table_stiching.sql

## Table reduction/filtering phase
Run the following SQL script on the already fully linked, and "stitched" database: Mining-StackOverflow-Github/DB creation/SO-GH_table_pruning.sql


Created by Norbert Eke, 2019
