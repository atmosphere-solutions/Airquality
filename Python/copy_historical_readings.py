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
from datetime import datetime, timedelta


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

def dropTable(dbcon, tablename):
    sql = "DROP TABLE IF EXISTS " + tablename

    dbcur = dbcon.cursor()
    print("********************** Drop Table **********************")
    print(sql)
    dbcur.execute(sql)
    dbcur.close

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
# Get all the monitor data we currently have stored in our database.
#
##########################################################################
MAP_TABLE_NAME = "Current_Readings_For_Map"
HOURLY_TABLE_PREFIX = "Hourly_Readings_"
DAILY_TABLE_PREFIX = "Daily_Readings_"

# Create SQL string to select the row from the database table.
sql = "SELECT * FROM " + MAP_TABLE_NAME
mycursor.execute(sql)
myresult = mycursor.fetchall()

# Print each row of the table out.
for row in myresult:
    sensor_index, name, location_type, humidity, pm2_5, last_seen, last_modified, latitude, longitude = row
    current_time = datetime.now()

    if (sensor_index != 1086):
        continue

    print(str(sensor_index) + " " + name + " " + str(last_seen) + " " + str(humidity) + " " + str(pm2_5))
    print(str(latitude) + "," + str(longitude))

    ##########################################################################
    #
    # Calculate the start time to retrieve historical data.
    # Hourly:
    # - Sunshine Coast - 2 Years (10219 days)
    # - Rest of BC and Alberta - 125 Days
    # - United States - 27 Days
    #
    # Daily:
    # - Sunshine Coast - Since Monitor was Initialized
    # - Rest of BC and Alberta - 15 months
    # - United States - 3 months
    #
    ##########################################################################
    hourly_start_time = last_modified
    daily_start_time = last_modified
    if (latitude > 49.331) and (latitude < 50.363) and (longitude > -124.889) and (longitude < -122.734):
        hourly_start_time = current_time - timedelta(days=125)
        #hourly_start_time = current_time - timedelta(days=10219)
        daily_start_time = last_modified
        print('Sunshine Coast and Sea to Sky')
    elif (latitude < 49.0) and (longitude > -123.204):
        hourly_start_time = current_time - timedelta(days=27)
        daily_start_time = current_time - timedelta(days=3 * 30)
        print('US')
    else:
        hourly_start_time = current_time - timedelta(days=125)
        daily_start_time = current_time - timedelta(days=15 * 30)
        print('Alberta and BC')
    if (last_modified > hourly_start_time):
        hourly_start_time = last_modified
    if (last_modified > daily_start_time):
        daily_start_time = last_modified

    print(hourly_start_time)
    print(daily_start_time)

    ##########################################################################
    #
    # Select the correct fields to query based on this being and indoor or
    # outdoor sensor.
    # - location_type = 0 (outdoor) uses ATM readings
    # - location_type = 1 (indoor) uses CF_1 readings
    #
    ##########################################################################
    pm_field = 'pm2.5_cf_1'
    if (location_type == 0):
        pm_field = 'pm2.5_atm'

    ##########################################################################
    #
    #  Purple Air Constants
    #
    ##########################################################################
    PURPLE_AIR_SENSOR_API = 'https://api.purpleair.com/v1/sensors/'
    PURPLE_AIR_API_KEY = '5901141D-E28E-11EC-8561-42010A800005'

    ##########################################################################
    #
    # Common Functions
    #
    ##########################################################################
    # Sort method for the monitor list by date.
    def sortParam(elem):
        return elem[0]

    ##########################################################################
    #
    #  Create the query to retrieve hourly average data.
    #  - average field must equal 60
    #
    ##########################################################################
    url = PURPLE_AIR_SENSOR_API + str(sensor_index) + '/history?average=60&fields=humidity%2C' + pm_field
    headers = {'content-type': 'application/json', 'X-API-Key': '5901141D-E28E-11EC-8561-42010A800005'}
    
    ##########################################################################
    #
    # Retrieve hourly data from PurpleAir
    #
    ##########################################################################
    data_count = 0
    hourly_monitor_data = []
    status_code = 200

    while hourly_start_time<current_time:
        new_url = url +'&start_timestamp=' + str(hourly_start_time.timestamp())
        req = requests.Request('Get',new_url,headers=headers,data='')
        prepared = req.prepare()
        s = requests.Session()
        response = s.send(prepared)
        status_code = response.status_code

        if status_code != 200:
            print(f'Request Failed: {response.status_code} for {sensor_index}')
            print(response.reason)
            print(response)
            break
        else:
            result = response.text

            # Verify if the data returned is valid.
            if len(result) < 1:
                print('Retrieve Failed: No data in purple air request')
                continue

            # Load purple air data into json object and sort it.
            json_data = json.loads(response.text)
            hourly_monitor_data = hourly_monitor_data + json_data['data']
            data_count = len(json_data['data'])
            hourly_start_time = datetime.fromtimestamp(json_data['end_timestamp'])

    # If our query failed go to the next sensor.
    if status_code != 200:
        continue

    # Sort the first chunk of data
    hourly_monitor_data.sort(key=sortParam)

    ##########################################################################
    #
    #  Create the query to retrieve daily average data.
    #  - average field must equal 1440
    #
    ##########################################################################
    url = PURPLE_AIR_SENSOR_API + str(sensor_index) + '/history?average=1440&fields=humidity%2C' + pm_field
    headers = {'content-type': 'application/json', 'X-API-Key': '5901141D-E28E-11EC-8561-42010A800005'}
    
    ##########################################################################
    #
    # Retrieve daily data from PurpleAir
    #
    ##########################################################################
    data_count = 0
    daily_monitor_data = []
    status_code = 200

    while daily_start_time<current_time:
        new_url = url +'&start_timestamp=' + str(daily_start_time.timestamp())
        req = requests.Request('Get',new_url,headers=headers,data='')
        prepared = req.prepare()
        s = requests.Session()
        response = s.send(prepared)
        status_code = response.status_code

        if status_code != 200:
            print(f'Request Failed: {response.status_code} for {sensor_index}')
            print(response.reason)
            print(response)
            break
        else:
            result = response.text

            # Verify if the data returned is valid.
            if len(result) < 1:
                print('Retrieve Failed: No data in purple air request')
                continue

            # Load purple air data into json object and sort it.
            json_data = json.loads(response.text)
            daily_monitor_data = daily_monitor_data + json_data['data']
            data_count = len(json_data['data'])
            daily_start_time = datetime.fromtimestamp(json_data['end_timestamp'])

    # If our query failed go to the next sensor.
    if status_code != 200:
        continue

    # Sort the first chunk of data
    daily_monitor_data.sort(key=sortParam)

    ######################################################################
    #
    # Clear out existing tables.
    #
    ######################################################################
    daily_table = DAILY_TABLE_PREFIX + str(sensor_index)
    hourly_table = HOURLY_TABLE_PREFIX + str(sensor_index)

    result = checkTableExists(mydb, daily_table)
    if (result == True):
        dropTable(mydb, daily_table)

    result = checkTableExists(mydb, hourly_table)
    if (result == True):
        dropTable(mydb, hourly_table)

    column_names = [ ('Humidity', 'DOUBLE'),
                     ('PM2_5Value', 'DOUBLE'),
                     ('Lastseen', 'DATETIME PRIMARY KEY') ]
    createTable(mydb, daily_table, column_names)

    column_names = [ ('Humidity', 'DOUBLE'),
                     ('PM2_5Value', 'DOUBLE'),
                     ('Lastseen', 'DATETIME PRIMARY KEY') ]
    createTable(mydb, hourly_table, column_names)

    ######################################################################
    #
    # Insert hourly data into sensor specific table.
    #
    ######################################################################
    for reading in hourly_monitor_data:
        epoch_time, humidity, hourly_pmvalue = reading

        if epoch_time is None:
             epoch_time = 0
        if humidity is None:
             humidity = 50
        if hourly_pmvalue is None:
             hourly_pmvalue = 0

        lastseen_dt = datetime.fromtimestamp(epoch_time)

        print(str(lastseen_dt) + ' ' + str(humidity) + ' ' + str(hourly_pmvalue))

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
    #
    # Insert daily data into sensor specific table.
    #
    ######################################################################
    for reading in daily_monitor_data:
        epoch_time, humidity, daily_pmvalue = reading

        if epoch_time is None:
             epoch_time = 0
        if humidity is None:
             humidity = 50
        if daily_pmvalue is None:
             daily_pmvalue = 0

        lastseen_dt = datetime.fromtimestamp(epoch_time)

        print(str(lastseen_dt) + ' ' + str(humidity) + ' ' + str(daily_pmvalue))

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
# Close all open connections and exit program.
#
##########################################################################
print("End it!")
mycursor.close()
mydb.close()
sys.exit()
print("You are still alive!")
