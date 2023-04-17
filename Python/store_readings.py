##########################################################################
#
#  The script takes in a db table name as a command line parameter.
#  It validates that the name is one of two tables:
#    - monitor_data - Data that is retrieved every 5 minutes
#    - nightly_monitor_data - Data that is retrieved once a day
#  The script then creates the database table if it doesn't already
#  exists.  This table uses the purple air json file tags as
#  it column names.  
#  The script then populate the database table with data retrieved for a list of
#  stations hard-coded into this script.
#
#  Here are the new purple air API column names:
#  (https://api.purpleair.com/#api-sensors-get-sensor-data)
#
#  ## Station information and status fields ##
#  name - String - The name given to the sensor from the registration form and used on the PA map.
#  icon - Integer - A flag reserved for future use to reference an icon for the sensor.
#  model - 
#  hardware - String - The sensors and other hardware that was detected by the firmware.
#  location_type - Integer - The location type.  Possible values are: 0 = Outside or 1 = Inside.
#  private - Integer - A flag indicating the private status of the sensor. Possible values are: 0 = public or 1 = private
#  latitude - Number - The latitude position value for the sensor.
#  longitude - Number - The longitude position value for the sensor.
#  altitude - Number - The altitude for the sensor's location in feet.
#  position_rating - Integer - 0 is nowhere near the claimed, 5 is close to the map location
#  led_brightness -
#  firmware_version - String - The last known firmware version on the device.
#  firmware_upgrade - 
#  rssia - Integer - The WiFi signal strength.
#  uptime - Integer - The time in minutes since the firmware started as last reported by the sensor.
#  pa_latency - Integer - The time taken to send data to the PurpleAir servers in milliseconds.
#  memory - Integer - Free HEAP memory in Kb.
#  last_seen - Long - The UNIX time stamp of the last time the server received data from the device.
#  last_modified - Long - The UNIX time stamp from the last time the device was modified by the registration form.
#  date_created - Long - The UNIX time stamp from when the device was created.
#  channel_state - String[] - ["No PM", "PM-A", "PM-B", "PM-A+PM-B"] Possible values are:
#                             - No PM = No PM sensors were detected.
#                             - PM-A = PM sensor on channel A only.
#                             - PM-B = PM sensor on channel B only.
#                             - PM-A+PM-B = PM sensor on both channel A and B.
#  channel_flags - String[] - ["Normal", "A-Downgraded", "B-Downgraded", "A+B-Downgraded"] Possible values are:
#                             - Normal = No PM sensors are marked as downgraded.
#                             - A-Downgraded = PM sensor on channel A is marked as downgraded.
#                             - B-Downgraded = PM sensor on channel B is marked as downgraded.
#                             - A+B-Downgraded = PM sensors on both channels A and B are marked as downgraded.
#  channel_flags_manual -
#  channel_flags_auto -
#  confidence -
#  confidence_manual -
#  confidence_auto -
#
#  ## Environmental fields ##
#  humidity - Integer - Relative humidity inside of the sensor housing (%). On average, this is 4% lower than 
#                       ambient conditions. Null if not equipped. (Average of a and b sensors)
#  humidity_a - Integer - As above for sensor a.
#  humidity_b - Integer - As above for sensor b.
#  temperature - Integer - Temperature inside of the sensor housing (F). On average, this is 8F higher than 
#                        - ambient conditions. Null if not equipped. (Average of a and b sensors)
#  temperature_a - Integer - As above for sensor a.
#  temperature_b - Integer - As above for sensor b.
#  pressure - Number - Current pressure in Millibars. (Average of a and b sensors)
#  pressure_a - Number - As above for sensor a.
#  pressure_b - Number - As above for sensor b.
#
#  ## Miscellaneous fields ##
#  voc - Number - VOC concentration (IAQ) in Bosch static iaq units as per BME680 spec sheet, EXPERIMENTAL. 
#                 Null if not equipped. (Average of a and b sensors)
#  voc_a - Number - As above for sensor a.
#  voc_b - Number - As above for sensor b.
#  ozone1 - Number - Ozone concentration (PPB) Null if not equipped.
#  analog_input - Number - If anything is connected to it, the analog voltage on ADC input of the PurpleAir sensor control board.
#
#  ## PM2.5 fields ##
#  pm2.5_alt - Number - The ALT Variant estimated mass concentration PM2.5 (ug/m3) is derived from the particle counts. 
#                       PM2.5 are fine particulates with a diameter of fewer than 2.5 microns.  pm2.5_alt returns average 
#                       ALT variant for channel A and B but excluding downgraded channels. (Average of a and b sensors)
#  pm2.5_alt_a - Number - As above for sensor a.
#  pm2.5_alt_b - Number - As above for sensor b.
#  pm2.5 - Number - Estimated mass concentration PM2.5 (ug/m3). PM2.5 are fine particulates with a diameter of fewer
#                   than 2.5 microns.  (Average of a and b sensors)
#  pm2.5_a - Number - As above for sensor a.
#  pm2.5_b - Number - As above for sensor b. 
#  pm2.5_atm - Number - Returns ATM variant average for channel A and B but excluding downgraded channels. 
#  pm2.5_atm_a - Number - As above for sensor a.
#  pm2.5_atm_b - Number - As above for sensor b.
#  pm2.5_cf_1 - Number - Returns CF=1 variant average for channel A and B but excluding downgraded channels. 
#  pm2.5_cf_1_a - Number - As above for sensor a.
#  pm2.5_cf_1_b - Number - As above for sensor b.
#
#  ## PM2.5 pseudo (simple running) average fields ##
#  pm2.5_10minute - Number - 10 minute pseudo (estimated) average for PM2.5 (Average of a and b sensors)
#  pm2.5_10minute_a - Number - As above for sensor a.
#  pm2.5_10minute_b - Number - As above for sensor b.
#  pm2.5_30minute - Number - 30 minute pseudo (estimated) average for PM2.5 (Average of a and b sensors)
#  pm2.5_30minute_a - Number - As above for sensor a.
#  pm2.5_30minute_b - Number - As above for sensor b.
#  pm2.5_60minute - Number - 60 minute pseudo (estimated) average for PM2.5 (Average of a and b sensors)
#  pm2.5_60minute_a - Number - As above for sensor a.
#  pm2.5_60minute_b - Number - As above for sensor b.
#  pm2.5_6hour - Number - 6 hour pseudo (estimated) average for PM2.5 (Average of a and b sensors)
#  pm2.5_6hour_a - Number - As above for sensor a.
#  pm2.5_6hour_b - Number - As above for sensor b.
#  pm2.5_24hour - Number - 24 hour pseudo (estimated) average for PM2.5 (Average of a and b sensors)
#  pm2.5_24hour_a - Number - As above for sensor a.
#  pm2.5_24hour_b - Number - As above for sensor b.
#  pm2.5_1week - Number - 7 day pseudo (estimated) average for PM2.5 (Average of a and b sensors)
#  pm2.5_1week_a - Number - As above for sensor a.
#  pm2.5_1week_b - Number - As above for sensor b.
#
#  ## ThingSpeak fields, used to retrieve data from api.thingspeak.com ##
#  primary_id_a - Number - ThingSpeak channel ID for storing sensor values
#  primary_key_a - String - ThingSpeak read key used for accessing data for the channel
#  secondary_id_a - Number - ThingSpeak channel ID for storing sensor values
#  secondary_key_a - String - ThingSpeak read key used for accessing data for the channel
#  primary_id_b - Number - ThingSpeak channel ID for storing sensor values
#  primary_key_b - String - ThingSpeak read key used for accessing data for the channel
#  secondary_id_b - Number - ThingSpeak channel ID for storing sensor values
#  secondary_key_b - String - ThingSpeak read key used for accessing data for the channel
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
# Get all the latest monitor data for all sensors in the BC region.
#
##########################################################################
PURPLE_AIR_SENSOR_API = 'https://api.purpleair.com/v1/sensors'
PURPLE_AIR_API_KEY = '5901141D-E28E-11EC-8561-42010A800005'
BC_NW_LATITUDE = 60.00
BC_NW_LONGITUDE = -139.06
BC_SE_LATITUDE = 48.30
BC_SE_LONGITUDE = -114.03
result = ''

# Sort method for the monitor list by id.
def sortParam(elem):
    return elem[0]

# List all the sensor fields that we want to retrieve from Purple Air.
Sensor_Fields = [
    "last_seen",      # The UNIX time stamp of the last time the server received data from the device.
    "sensor_index",   # The sensor_id of the new member sensor. This must be AS PRINTED on the sensor’s label.
    "name",           # The name given to the sensor from the registration form and used on the PA map.
    "location_type",  # The location type.  Possible values are: 0 = Outside or 1 = Inside.
    "humidity",       # Relative humidity inside of the sensor housing (%). On average, this is 4% lower than ambient conditions. Null if not equipped.
    "pm2.5",          # Average of channel A and B excluding downgraded channels and using CF=1 variant for indoor, ATM variant for outdoor devices
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
    # Get the timestamp from the monitor data and convert to SQL date format.
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

    # For now only insert data for sunshine coast into tables.
    #if (latitude < 49.34380) or (latitude > 49.88034):
    #    continue
    #if (longitude > -123.43902) or (longitude < -124.65153):
    #    continue

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
    if (lastseen_dt.minute < 5):
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

    if ((lastseen_dt.minute < 5) and (lastseen_dt.hour == 8)):
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
