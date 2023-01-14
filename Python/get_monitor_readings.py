##########################################################################
#
#  The script takes in a db table name as a command line parameter.
#  It validates that the name is one of two tables:
#    - monitor_data - Data that is retrieved every 5 minutes
#    - nightly_monitor_data - Data that is retrieved once a day
#  The script then creates the database table if it doesn't already
#  exists.  This table uses the purple air json file tags as
#  it column names.  Here is the definition of the column names
#  with unused columns noted:
#    - ID - PurpleAir Sensor ID
#    - ParentID - The PurpleAir Sensor Id of the "parent" entr for the B Channel
#    - Label - The "name" that appears on the map for this sensor
#    - DEVICE_LOCATIONTYPE - <NOT USED>
#    - THINGSPEAK_PRIMARY_ID - Thingspeak Channel ID for Primary Data
#    - THINGSPEAK_PRIMARY_ID_READ_KEY - Thingspeak Read Key for Primary Data
#    - THINGSPEAK_SECONDARY_ID - Thingspeak Channel ID for Secondary Data
#    - THINGSPEAK_SECONDARY_ID_READ_KEY - Thingspeak Read Key for Secondary Data
#    - Lat - Latitude Position Info
#    - Lon - Longitude Position Info
#    - PM2_5Value - Current PM2.5 Value
#    - LastSeen - <NOT USED>
#    - State - <NOT USED>
#    - Type - Sensor Type (PMS5003, PMS1003, BME280, etc.)
#    - Hidden - Hide from public view on map: true/false
#    - Flag - Data flagged for unusally high readings
#    - DEVICE_BRIGHTNESS - <NOT USED>
#    - DEVICE_HARDWAREDISCOVERED - <NOT USED>
#    - DEVICE_FIRMWAREVERSION - <NOT USED>
#    - Version - <NOT USED>
#    - LastUpdateCheck - <NOT USED>
#    - Uptime - <NOT USED>
#    - RSSI - <NOT USED>
#    - isOwner - Currently logged in user is the sensor owner
#    - A_H - True if sensor output is downgraded or marked for hardware issues
#    - temp_f - Current temperature in F
#    - humidity - Current humidity in %
#    - pressure - Current pressure in Millibars
#    - AGE - Sensor data age (when data was last received) in minutes
#    - Stats - Secondary json blob containing the following data:
#      - v - Real time or current PM2.5 value
#      - v1 - Short term (10 minute average)
#      - v2 - 30 minute average
#      - v3 - 1 hour average
#      - v4 - 6 hour average
#      - v5 - 24 hour average
#      - v6 - One week average
#      - pm - Real time or current PM2.5 Value
#      - lastModified - Last modified time stamp for averages
#      - timeSinceModified - Time between last two readings in milliseconds
# The script then populate the database table with data retrieved for a list of
# stations hard-coded into this script.
#
##########################################################################

##########################################################################
#
# Python imports - Equivalent to includes in c.
#
##########################################################################
import sys
import json
import requests
import mysql.connector
from datetime import datetime

##########################################################################
#
# Read the command line argument and ensure it is valid.
#  - As a reminder from the description above, this selects which
#    database to store the current purple air data to.
#
##########################################################################
TABLE_NAME = ""

if len(sys.argv) != 2:
    print("Invalid number of arguments!")
    print("  USAGE: script.py table_name")
    exit()
else:
    TABLE_NAME = sys.argv[1]


##########################################################################
#
# For Each Monitor ID, Get data the latest data from purpleair.com
#
##########################################################################
PURPLE_AIR_WEBSITE = 'https://www.purpleair.com/json'



import requests

import json

 

# Sort method for the monitor list by id.

def sortParam(elem):

    return elem[0]

 

# List all the sensor fields that we want to retrieve from Purple Air.

Sensor_Fields = [
    "last_seen",        # The UNIX time stamp of the last time the server received data from the device.

    "sensor_index",        # The sensor_id of the new member sensor. This must be AS PRINTED on the sensor’s label.

    "name",             #  The name given to the sensor from the registration form and used on the PA map.

    "pm2.5",             #  returns average for channel A and B but excluding downgraded channels and using CF=1 variant for indoor, ATM variant for outdoor devices

    "latitude",

    "longitude"

]

 

# List all the fields in url format in a single string.

field_list_string = "last_modified"

for field in Sensor_Fields:

    field_list_string += "%2C" + field

 

url = 'https://api.purpleair.com/v1/sensors' + '?fields=' + field_list_string + '&nwlng=-139.06&nwlat=60&selng=-114.03&selat=48.3'

headers = {'content-type': 'application/json', 'X-API-Key': '5901141D-E28E-11EC-8561-42010A800005'}

 

req = requests.Request('Get',url,headers=headers,data='')

prepared = req.prepare()

 

s = requests.Session()

response = s.send(prepared)

 

monitor_list = []

monitor_array = []

 

if response.status_code != 200:

    print(f'Request Failed: {response.status_code}')

    print(response.reason)

else:

    json_data = json.loads(response.text)

    raw_monitor_data = json_data['data']

    raw_monitor_data.sort(key=sortParam)

    for monitor in raw_monitor_data:
        i = 0

        print("*******************************\n")

        for x in monitor :
            print(f"Item: #{i}, Value: {x} \n")
            i += 1
        
        print("*******************************\n")
        print(monitor)


    for monitor in raw_monitor_data:

        monitor_list.append(monitor[0])

        monitor_dict = {}

        monitor_dict['ID'] = monitor[0]
        monitor_dict["Lastmodified"] = monitor[1]
        monitor_dict["Lastseen"] = monitor[2]
        monitor_dict['Name'] = monitor[3]
        monitor_dict["Lat"] = monitor[4]
        monitor_dict["Lon"] = monitor[5]
        monitor_dict["PM2_5Value"] = monitor[6]

        monitor_array.append(monitor_dict)

##########################################################################
#
# Connect to the MYSQL database on this machine, check to see if the selected
# table exists.  If it does not exist, create it.
#
##########################################################################
# Connect to the mysql database.
mydb = mysql.connector.connect(
    host="localhost",
    user="airdata",
    passwd="AESl0uis!",
    database="airdata"
)
mycursor = mydb.cursor()

##########################################################################
#
# Insert data from each monitor into the SQL database.
#
##########################################################################

for monitor in monitor_array:
    # Get the timestamp from the monitor data and convert to SQL date format.
    lastmodified = monitor["Lastmodified"]
    lastseen = monitor["Lastseen"]

    if lastmodified is not None:
        lastmodified_dt = datetime.utcfromtimestamp(lastmodified)
    else:
        lastmodified_dt = datetime.utcfromtimestamp(0)
    if lastseen is not None:
        lastseen_dt = datetime.utcfromtimestamp(lastseen)
    else:
        lastseen_dt = datetime.utcfromtimestamp(0)

    latitude = monitor.get("Lat", 0)
    longitude = monitor.get("Lon", 0)

    if latitude is None or (latitude > 90 or latitude < -90):
        latitude = 0
    if longitude is None or (longitude > 180 or longitude < -180):
        longitude = 0

    pmvalue = monitor.get("PM2_5Value", -1)

    if pmvalue is None:
        pmvalue = -1

    name = monitor.get("Name", "null")

    index = monitor.get("ID", 0)

    if index is None:
        index = 0

    if name is None:
        name = "null"

    # Create SQL string to insert a row into the database table.
    sql = "INSERT INTO monitor_data (ID, Name, PM2_5Value, Lastseen, Lastmodified, Lat, Lon) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    sql2 = "REPLACE INTO current_data (ID, Name, PM2_5Value, Lastseen, Lastmodified, Lat, Lon) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    
    # Create a list of the data we are going to insert into the table.
    val = (
            str(index), 
            str(name),
            str(pmvalue),
            lastseen_dt, 
            lastmodified_dt,
            str(latitude),
            str(longitude)
            )

    # Insert the data into the table.
    print("**********************INSERTING DATA**********************\n", sql, val)
    mycursor.execute(sql, val)
    mydb.commit()

    # Insert the data into the table.
    print("**********************INSERTING DATA**********************\n", sql2, val)
    mycursor.execute(sql2, val)
    mydb.commit()

