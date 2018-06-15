-=============================================================================-

             Email Collector Application Programming Interface

-=============================================================================-

This application was designed to parse uploaded emails and store such information
as Sender, Recipients, Subject, Body, HTML, Timestamp, Attachments (name, size,
content type, MD5, path to saved file on the server) on the server.
User is able to upload emails through this API, read, update and delete them.
Also, downloading back saved attachments supported.
Basic HTTP Authorization supported and mandatory for all available application
endpoints

-=============================================================================-

How to install and run the application:

-=============================================================================-

1. Create and activate virtual environment:

$ virtualenv venv

$ source venv/bin/activate

2. Install requirements:

$ pip install -r requirements.txt

3. Make run.py file executable:

$ chmod a+x run.py

4. Create 'email_collector' database structure:

$ cd db

mysql> source CREATE_DB.sql

5.Run the API:

./run.py -h
usage: run.py [-h] [-H HOST] [-P PORT]

optional arguments:
  -h, --help            show this help message and exit
  -H HOST, --host HOST  Hostname for the Flask application
  -P PORT, --port PORT  Port for the Flask application


Also, a hidden argument can be used:

--debug

$ ./run.py --host=127.0.0.1 --port=5000 --debug


-=============================================================================-

How to use the application. Supported features.

-=============================================================================-

* Upload emails.

GET/POST /api/v1/email - Upload email files:

curl -i -u login:pass -X POST http://127.0.0.1:5000/api/v1/email -F file=@filename


* Retrieve uploaded emails.

/api/v1/email/all - method GET:

curl -i -u login:pass -X GET http://127.0.0.1:5000/api/v1/email/all


* Retrieve uploaded email by id:

/api/v1/email/id - method GET.

curl -i -u login:pass -X GET http://127.0.0.1:5000/api/v1/email/id


* Update uploaded email.

/api/v1/email/id - method PUT:

curl -i -u login:pass -H 'Content-Type: application/json' -X PUT -d '{"timestamp": "1", "body": "text", "subject": "text"}' http://127.0.0.1:5000/api/v1/email/id


* Delete uploaded email.

/api/v1/email/id - method DELETE:

curl -i -u login:pass -X DELETE http://127.0.0.1:5000/api/v1/email/id


* Download attachment from server.

/api/v1/email/attachments/directory/filename - method GET:

('directory' and 'filename' attributes stored in the database and can be found while retrieving an email by id under the 'path' value)

curl -i -u login:pass GET http://127.0.0.1:5000/api/v1/email/attachments/directory/filename