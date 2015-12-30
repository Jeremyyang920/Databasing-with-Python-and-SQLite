import urllib
import sqlite3
import json
import time
import ssl
import urllib.request

serviceurl = "http://maps.googleapis.com/maps/api/geocode/json?"

# Deal with SSL certificate anomalies Python > 2.7
# scontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
scontext = None

conn = sqlite3.connect('geodata.sqlite')
cur = conn.cursor()

cur.executescript('''
DROP TABLE IF EXISTS Locations;

CREATE TABLE Locations (
    address TEXT,
    geodata TEXT
);
''')

fh = open("where.data")
count = 0
for line in fh:
    if count > 200 : break
    address = line.strip()
    print(address)
    print ('')
    cur.execute("SELECT geodata FROM Locations WHERE address= ?", (address, ))

    try:
        data = cur.fetchone()[0]
        print ("Found in database ",address)
        continue
    except:
        pass

    print ('Resolving', address)
    url = serviceurl + urllib.parse.urlencode({"sensor":"false", "address": address})
   
    print ('Retrieving', url)
    uh = urllib.request.urlopen(url)
    data = uh.read().decode(encoding='utf-8')
##    data=data[:20].replace('\n',' ')
    print ('Retrieved',len(data),'characters')
    count = count + 1
    try: 
        js = json.loads(data)
        # print js  # We print in case unicode causes an error
    except: 
        continue

    if 'status' not in js or (js['status'] != 'OK' and js['status'] != 'ZERO_RESULTS') : 
        print ('==== Failure To Retrieve ====')
        print (data)
        break

    cur.execute('''INSERT INTO Locations (address, geodata) 
            VALUES ( ?, ? )''', ( address,data  ))
    conn.commit() 

print ("Run geodump.py to read the data from the database so you can visualize it on a map.")
