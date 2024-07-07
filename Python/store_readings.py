##########################################################################
#
#  This script loads a list of all sensors from BC and stores their
#  constant data into a file for later usage.
#
#  Here are the columns that are stored with this query:
#  (https://api.purpleair.com/#api-sensors-get-sensor-data)
#
#   "last_seen"       - The UNIX time stamp of the last time the server 
#                       received data from the device.
#   "sensor_index"    - The sensor_id of the new member sensor. This must 
#                       be AS PRINTED on the sensor’s label.
#   "name"            - The name given to the sensor from the registration 
#                       form and used on the PA map.
#   "location_type"   - The location type.  Possible values are: 
#                       0 = Outside or 1 = Inside.
#   "latitude"        - Latitude coordinate of the sensor.
#   "longitude"       - Longitude coordinate of the sensor.
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
# SQL FUNCTiONS
#
##########################################################################
def checkTableExists(dbcon, tablename):
    dbcur = dbcon.cursor()
    dbcur.execute("""
        SELECT COUNT(*)
        FROM information_schema.tables
        WHERE table_name = '{0}'
        """.format(tablename.replace('\'', '\'\'')))
    if dbcur.fetchone()[0] == 1:
        dbcur.close()
        return True

    dbcur.close()
    return False

def createTable(dbcon, tablename, columns):
    sql = "CREATE TABLE " + tablename + " ("
    col_count = 0
    for col_name, col_type in columns:
        sql = sql + col_name + " " + col_type
        col_count = col_count + 1
        if (col_count < len(columns)):
            sql = sql + ", "
    sql = sql + ")"

    dbcur = dbcon.cursor()
    print("********************** Creating Table **********************")
    print(sql)
    dbcur.execute(sql)
    dbcur.close


##########################################################################
#
# Select the monitors that we will be updating with this run.
# 0 - Sunshine Coast
# 1 - Rest of BC
#
##########################################################################
region = 0
if (len(sys.argv) > 1) and (sys.argv[1] == '0'):
    print("******************** Sunshine Coast ********************")
    region = 0
elif (len(sys.argv) > 1) and (sys.argv[1] == '1'):
    print("******************** All of BC ********************")
    region = 1
else:
    print("******************** Unknown Region  ********************")
    sys.exit()

if (region == 0):
    nw_lat = 49.88034
    nw_lon = -124.65153
    se_lat = 49.34380
    se_lon = -123.43902
elif (region == 1):
    nw_lat = 60.00
    nw_lon = -139.06
    se_lat = 48.30
    se_lon = -114.03
else:
    sys.exit()

print('North West Latitude: ' + str(nw_lat))
print('North West Longitude: ' + str(nw_lon))
print('South East Latitude: ' + str(se_lat))
print('South East Longitude: ' + str(se_lon))


##########################################################################
#
# Get all the latest monitor data for all sensors in the BC region.
#
##########################################################################
PURPLE_AIR_SENSOR_API = 'https://api.purpleair.com/v1/sensors'
PURPLE_AIR_API_KEY = '5901141D-E28E-11EC-8561-42010A800005'
BC_NW_LATITUDE = nw_lat
BC_NW_LONGITUDE = nw_lon
BC_SE_LATITUDE = se_lat
BC_SE_LONGITUDE = se_lon
result = ''

# Sort method for the monitor list by id.
def sortParam(elem):
    return elem[0]

# List all the sensor fields that we want to retrieve from Purple Air.
Sensor_Fields = [
    "last_seen",      # The UNIX time stamp of the last time the server 
                      # received data from the device.
    "sensor_index",   # The sensor_id of the new member sensor. This must 
                      # be AS PRINTED on the sensor’s label.
    "name",           # The name given to the sensor from the registration 
                      # form and used on the PA map.
    "location_type",  # The location type.  Possible values are: 
                      # 0 = Outside or 1 = Inside.
    "humidity",       # Relative humidity inside of the sensor housing (%). 
                      # On average, this is 4% lower than ambient 
                      # conditions. Null if not equipped.
    "pm2.5",          # Average of channel A and B excluding downgraded 
                      # channels and using CF=1 variant for indoor, 
                      # ATM variant for outdoor devices
    "pm2.5_60minute",
    "pm2.5_24hour",
    "latitude",
    "longitude"
]

# List all the fields in url format in a single string.
field_list_string = "date_created"
for field in Sensor_Fields:
    field_list_string += "%2C" + field

# Build http request and send.
location_box_params = '&nwlng=' + str(BC_NW_LONGITUDE) + '&nwlat=' + str(BC_NW_LATITUDE)
location_box_params = location_box_params + '&selng=' + str(BC_SE_LONGITUDE) + '&selat=' + str(BC_SE_LATITUDE)
url = 'https://api.purpleair.com/v1/sensors' + '?fields=' + field_list_string + location_box_params
headers = {'content-type': 'application/json', 'X-API-Key': '5901141D-E28E-11EC-8561-42010A800005'}
req = requests.Request('Get',url,headers=headers,data='')
prepared = req.prepare()
s = requests.Session()
response = s.send(prepared)

if response.status_code != 200:
    print(f'Request Failed: {response.status_code}')
    print(response.reason)
    print(response)
    sys.exit()
else:
    result = response.text

 
##########################################################################
#
# Load the data from the purple air website into a python data object.
#
##########################################################################

if len(result) < 1:
    print('Retrieve Failed: No data in purple air request')
    sys.exit()


monitor_list = []
monitor_array = []

# Load purple air data into json object and sort it.
json_data = json.loads(response.text)
raw_monitor_data = json_data['data']
raw_monitor_data.sort(key=sortParam)

# Load json data into a python array of monitor dictionaries.
for monitor in raw_monitor_data:
    monitor_list.append(monitor[0])
        
    monitor_dict = {}
    monitor_dict['ID'] = monitor[0]
    monitor_dict["DateCreated"] = monitor[1]
    monitor_dict["Lastseen"] = monitor[2]
    monitor_dict['Name'] = monitor[3]
    monitor_dict['LocationType'] = monitor[4]
    monitor_dict["Lat"] = monitor[5]
    monitor_dict["Lon"] = monitor[6]
    monitor_dict["Humidity"] = monitor[7]
    monitor_dict["PM2_5_Value"] = monitor[8]
    monitor_dict["PM2_5_1_Hour"] = monitor[9]
    monitor_dict["PM2_5_1_Day"] = monitor[10]

    monitor_array.append(monitor_dict)


##########################################################################
#
#  Store current data and hourly/daily data per sensor.
#
##########################################################################


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
MAP_TABLE_NAME = "Current_Readings_For_Map"
HOURLY_TABLE_PREFIX = "Hourly_Readings_"
DAILY_TABLE_PREFIX = "Daily_Readings_"

for monitor in monitor_array:
    # Get the timestamp from monitor data and convert to SQL date format.
    datecreated = monitor["DateCreated"]
    lastseen = monitor["Lastseen"]

    if datecreated is not None:
        datecreated_dt = datetime.utcfromtimestamp(datecreated)
    else:
        datecreated_dt = datetime.utcfromtimestamp(0)
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

    location_type = monitor.get("LocationType", 0)

    humidity = monitor.get("Humidity", -1)
    pmvalue = monitor.get("PM2_5_Value", -1)
    hourly_pmvalue = monitor.get("PM2_5_1_Hour", -1)
    daily_pmvalue = monitor.get("PM2_5_1_Day", -1)

    if location_type is None:
        location_type = -1

    if humidity is None:
        humidity = -1

    if pmvalue is None:
        pmvalue = -1

    if hourly_pmvalue is None:
        hourly_pmvalue = -1

    if daily_pmvalue is None:
        daily_pmvalue = -1

    name = monitor.get("Name", "null")

    index = monitor.get("ID", 0)

    if index is None:
        index = 0

    if name is None:
        name = "null"

    # If we have bad data, then don't add it to the table.
    if (latitude == 0) or (longitude == 0) or (index == 0):
        print("Bad Data:")
        print(monitor)
        continue

    ######################################################################
    # Ensure tables exist for current monitor.
    ######################################################################
    current_data_table = MAP_TABLE_NAME
    daily_table = DAILY_TABLE_PREFIX + str(index)
    hourly_table = HOURLY_TABLE_PREFIX + str(index)

    result = checkTableExists(mydb, current_data_table)
    if (result == False):
        print("Create Table")
        column_names = [ ('ID', 'INT PRIMARY KEY'),
                         ('Name', 'VARCHAR(128)'),
                         ('Location', 'INTEGER'),
                         ('Humidity', 'DOUBLE'),
                         ('PM2_5Value', 'DOUBLE'),
                         ('Lastseen', 'DATETIME'),
                         ('DateCreated', 'DATETIME'),
                         ('Lat', 'DECIMAL(11,8)'),
                         ('Lon', 'DECIMAL(11,8)') ]
        createTable(mydb, current_data_table, column_names)

    result = checkTableExists(mydb, daily_table)
    if (result == False):
        column_names = [ ('Humidity', 'DOUBLE'),
                         ('PM2_5Value', 'DOUBLE'),
                         ('Lastseen', 'DATETIME PRIMARY KEY') ]
        createTable(mydb, daily_table, column_names)

    result = checkTableExists(mydb, hourly_table)
    if (result == False):
        column_names = [ ('Humidity', 'DOUBLE'),
                         ('PM2_5Value', 'DOUBLE'),
                         ('Lastseen', 'DATETIME PRIMARY KEY') ]
        createTable(mydb, hourly_table, column_names)


    ######################################################################
    # Replace Current Map values into Map Table
    ######################################################################
    # Create SQL string to insert a row into the database table.
    sql = "REPLACE INTO " + current_data_table + " (ID, Name, Location, Humidity, PM2_5Value, Lastseen, DateCreated, Lat, Lon) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    
    # Create a list of the data we are going to insert into the table.
    val = (
            str(index), 
            str(name),
            str(location_type),
            str(humidity),
            str(hourly_pmvalue),
            lastseen_dt, 
            datecreated_dt,
            str(latitude),
            str(longitude)
            )


    # Insert the data into the table.
    print("**********************INSERTING DATA**********************\n", sql, val)
    mycursor.execute(sql, val)
    mydb.commit()


    ######################################################################
    # Insert hourly data into sensor specific tables.
    # - Only insert at the top of the hour.
    ######################################################################
    if (lastseen_dt.minute < 9):
        # Create SQL string to insert a row into the database table.
        sql = "REPLACE INTO " + hourly_table + " (Lastseen, Humidity, PM2_5Value) VALUES (%s, %s, %s)"
    
        # Create a list of the data we are going to insert into the table.
        val = (
                lastseen_dt, 
                str(humidity),
                str(hourly_pmvalue)
              )

        # Insert the data into the table.
        print("**********************INSERTING DATA**********************\n", sql, val)
        mycursor.execute(sql, val)
        mydb.commit()

    ######################################################################
    # Insert daily data into sensor specific tables.
    # - Only insert at the top of the hour at midnight pacific time.
    ######################################################################

    if ((lastseen_dt.minute < 9) and (lastseen_dt.hour == 8)):
        # Create SQL string to insert a row into the database table.
        sql = "REPLACE INTO " + daily_table + " (Lastseen, Humidity, PM2_5Value) VALUES (%s, %s, %s)"
    
        # Create a list of the data we are going to insert into the table.
        val = (
                lastseen_dt, 
                str(humidity),
                str(daily_pmvalue)
              )

        # Insert the data into the table.
        print("**********************INSERTING DATA**********************\n", sql, val)
        mycursor.execute(sql, val)
        mydb.commit()


##########################################################################
#
# Close all open connections.
#
##########################################################################
mycursor.close()
mydb.close()
