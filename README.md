A Terminal-Based Message Board Program that allows users to interact with a postgres database.

### Installation
Requires Python and Postgresql

1. Clone repo
2. Install requirements.txt
3. Create a database in Postgresql and run the set_up.sql file
3. Create a .env file with variables DATABASE, DATABASE_USERNAME, PASSWORD, and HOST. They should contain the database name, username for Postgresql, password for Postgres, and 'localhost', respectively.
3. run python threads.py

### This project not being updated
Originally, this project was meant to include networking capabilites, but it will not be implemented because the code is not modular(due to it not being an object-oriented implementation) and does not use a framework.
