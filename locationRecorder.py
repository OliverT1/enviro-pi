# Written by Oliver Turnbull for EnviroPi project, part of the AstroPi competition

import sqlite3 as lite
import urllib.request
import json
import time

# Global variable to store the database
global db
# Time in hours to collect location, set to 10 days to ensure experiment is completely covered
timeHours = 240
# Time between data collection
sleepSecs = 1


# Creates SQLite DB, Creates images table and returns cursor
def getDatabase():
    global db
    db = None
    try:
        # Connects to DB, creates it if it doesn't exist
        db = lite.connect('enviroPiHome.db')
        cur = db.cursor()
        # Creates the table if it doesn't exist
        cur.execute('''CREATE TABLE IF NOT EXISTS
                        locations(id INTEGER PRIMARY KEY AUTOINCREMENT,
			lat REAL NOT NULL,
			long REAL NOT NULL,
			timeStamp DATETIME DEFAULT CURRENT_TIMESTAMP);''')
        db.commit()
    except Exception as e:
        # Roll back any changes if something goes wrong
        db.rollback()
        raise e
    # Returns cursor object to be used to later add entries
    return cur
# Retrieves GPS co-ords from ISS now API
def getCoords(cur):
    # Gets json data from ISS current location API and reads into obj
    req = urllib.request.Request("http://api.open-notify.org/iss-now.json")
    response = urllib.request.urlopen(req)
    
    # Decodes url into string data for json to read
    encoding = response.headers.get_content_charset('utf8')
    # Reads data into obj
    obj = json.loads(response.read().decode(encoding))

    # Inserts lat and long into SQLite table
    cur.execute('INSERT INTO locations(lat, long) values(?, ?);', (obj['iss_position']['latitude'], obj['iss_position']['longitude']))

# Opens database and gets reference to cursor
cursor = getDatabase()
x = 0
# Runs program for timeHours 
while x <= (timeHours * 60 * 60):
    getCoords(cursor)
    # Commits co-ords to database each time to prevent data loss
    db.commit()
    time.sleep(sleepSecs)
    x += sleepSecs

db.commit()
db.close()
