"""`main` is the top level module for your Flask application."""

# Mobile Byte Version 1
# 
# Copyright 1/2016 Jennifer Mankoff
#
# Licensed under GPL v3 (http://www.gnu.org/licenses/gpl.html)
#

# Imports
import os
import jinja2
import webapp2
import logging
import json
import urllib
import MySQLdb
import math
from flask import Flask, request, url_for

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

# Define your production Cloud SQL instance information.
_INSTANCE_NAME = 'byte3project:datapipe1'
_DB_NAME = 'asjkdbmobile'
_USER = 'root' 


# the table where activities are logged
_ACTIVITY = 'plugin_google_activity_recognition'
# the table where locations are logged
_LOCATIONS = 'locations'
# the distance that determins new locations
_EPSILON = 0.00001

if (os.getenv('SERVER_SOFTWARE') and
    os.getenv('SERVER_SOFTWARE').startswith('Google App Engine/')):
    logging.info("entering here...")
    _DB = MySQLdb.connect(unix_socket='/cloudsql/' + _INSTANCE_NAME, db=_DB_NAME, user=_USER, charset='utf8')
else:
    _DB = MySQLdb.connect(host='173.194.237.31',
                          port=3306,
                          db=_DB_NAME,
                          user=_USER,
                          charset='utf8')

    # Alternatively, connect to a Google Cloud SQL instance using:
    # _DB = MySQLdb.connect(host='ip-address-of-google-cloud-sql-instance', port=3306, user=_USER, charset='utf8')
# Import the Flask Framework
from flask import Flask, request
app = Flask(__name__)


initialize_db = 0




@app.route('/')
def index():
    template = JINJA_ENVIRONMENT.get_template('templates/index.html')
    cursor = _DB.cursor()
    cursor.execute('SHOW TABLES')
    
    if (os.getenv('SERVER_SOFTWARE') and
        os.getenv('SERVER_SOFTWARE').startswith('Google App Engine/')):
        db = MySQLdb.connect(unix_socket='/cloudsql/' + _INSTANCE_NAME,
                             db=_DB_NAME, user=_USER, charset='utf8')
        cursor = db.cursor()

        query = "SELECT FROM_UNIXTIME(timestamp/1000,'%m/%d/%Y  %h:%i') AS 'activity_time', activity_name FROM plugin_google_activity_recognition LIMIT 20".format()
        locactrows, locactcol_names = make_query(cursor, query)
        
        query = "SELECT DISTINCT FROM_UNIXTIME(timestamp/1000,'%Y-%m-%d %H:%i') AS Time_of_day, double_latitude AS Latitude, double_longitude AS Longitude, DAYNAME(FROM_UNIXTIME(timestamp/1000,'%Y-%m-%d %H:%i')) AS Day, DAYOFWEEK(FROM_UNIXTIME(timestamp/1000,'%Y-%m-%d %H:%i')) AS Day_INDEX, accuracy FROM locations LIMIT 20".format()
        timeloctrows, timeloct_names = make_query(cursor, query)
    else:
        queries = [{"query": 'Need to connect from Google Appspot', "results": []}]
        rows, col_names = "", ""
    return template.render(locactcol_names = locactcol_names, locactrows = locactrows, timeloctrows = timeloctrows, timeloct_names = timeloct_names)

    
@app.route('/about')
def about():
    template = JINJA_ENVIRONMENT.get_template('templates/about.html')
    image2 = url_for('static', filename='images/image2.png')
    image3 = url_for('static', filename='images/image3.png')
    image6 = url_for('static', filename='images/image6.png')
    image1 = url_for('static', filename='images/image1.png')
    return template.render(image2=image2, image3=image3, image6=image6, image1=image1)

@app.route('/quality')
def quality():
    template = JINJA_ENVIRONMENT.get_template('templates/quality.html')
    image5 = url_for('static', filename='images/image5.png')
    return template.render(image5=image5)

@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, Nothing at this URL.', 404

@app.errorhandler(500)
def application_error(e):
    """Return a custom 500 error."""
    return 'Sorry, unexpected error: {}'.format(e), 500

# Takes the database link and the query as input
def make_query(cursor, query):
    # this is for debugging -- comment it out for speed
    # once everything is working

    try:
        cursor.execute(query)
        
        data = cursor.fetchall()
        col_names = [i[0] for i in cursor.description]

        return (data, col_names) 
    
    except Exception:
        # if the query failed, log that fact
        logging.info("query making failed")
        logging.info(query)

        # finally, return an empty list of rows 
        return []