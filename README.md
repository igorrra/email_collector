API for email upload, read, update and delete.

How to use:

1. Create and activate virtual environment:

$ virtualenv venv

$ source venv/bin/activate

2. Install requirements:

$ pip install -r requirements.txt

3. Make app.py file executable:

$ chmod a+x app.py

4. Create 'email_collector' database structure:

$ cd db
mysql> source CREATE_DB.sql

5.Run the API:

$ ./run.py