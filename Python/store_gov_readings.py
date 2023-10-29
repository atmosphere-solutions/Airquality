##########################################################################
#
# Python imports - Equivalent to includes in c.
#
##########################################################################
import sys
import io
import json
import requests
import csv
import mysql.connector
from datetime import datetime, timedelta, timezone

BC_GOVERNMENT_AQ_DATA = 'https://www.env.gov.bc.ca/epd/bcairquality/aqo/csv/Hourly_Raw_Air_Data/Air_Quality/PM25.csv'
BC_GOVERNMENT_HUMIDITY_DATA = 'https://www.env.gov.bc.ca/epd/bcairquality/aqo/csv/Hourly_Raw_Air_Data/Meteorological/HUMIDITY.csv'
BC_GOVERNMENT_VENTALATION_DATA = 'https://envistaweb.env.gov.bc.ca/aqo/files/venting_archive/2023/EC_BBS_230925_Mon_September_25_23.txt'

AQ_Data = []
Humidity_Data = []
Daily_AQ_Data = {}

# Get the current date to search the government CSV for the latest data.
current_time = ""
current_date = datetime.now().strftime("%Y-%m-%d")
current_datetime = datetime.now() 
one_day_datetime = datetime.now()

##########################################################################
# Build AQ data request and load data into an array.  
#  - Only load today's data!
##########################################################################
url = BC_GOVERNMENT_AQ_DATA
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
    text = response.text
    str_file = io.StringIO(text, newline='\n')
    reader = csv.reader(str_file, delimiter=',')

    # Process each row of the CSV file
    for row in reader:

        # Ignore Title Row
        if (row[0] != "DATE_PST"):

            #Load Current Values into the AQ_DATA array.
            if current_date in row[0]:
                if current_time == "":
                    AQ_Data.append(row)
                    current_time = row[0]
                    current_datetime = datetime.strptime(current_time, '%Y-%m-%d %H:%M')
                    one_day_datetime = current_datetime - timedelta(days=1) + timedelta(minutes=1)
                elif current_time == row[0]:
                    AQ_Data.append(row)

            #Load past 24 hours values into another array.
            row_datetime = datetime.strptime(row[0], '%Y-%m-%d %H:%M')
            if (row_datetime > one_day_datetime):
                monitor_id = row[7].strip()
                if monitor_id.isnumeric():
                    monitor_id = 'X' + monitor_id
                pm25_value = 0
                if (row[2] != ""):
                    pm25_value = float(row[2])
                if (monitor_id in Daily_AQ_Data):
                    Daily_AQ_Data[monitor_id][0] += 1
                    Daily_AQ_Data[monitor_id][1] += pm25_value
                    Daily_AQ_Data[monitor_id][2] = (Daily_AQ_Data[monitor_id][1] / float(Daily_AQ_Data[monitor_id][0]))
                else:
                    Daily_AQ_Data[monitor_id] = [1, pm25_value, pm25_value]

    str_file.close()

#for row in AQ_Data:
    #print(row)
#print(Daily_AQ_Data)
#for id in Daily_AQ_Data:
    #print(id)
    #print(Daily_AQ_Data[id])

##########################################################################
# Build humidity data request and load data into an array.  
#  - Only load today's data!
##########################################################################
url = BC_GOVERNMENT_HUMIDITY_DATA
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
    text = response.text
    str_file = io.StringIO(text, newline='\n')
    reader = csv.reader(str_file, delimiter=',')
    for row in reader:
        if current_date in row[0]:
            if current_time == "":
                Humidity_Data.append(row)
                current_time = row[0]
            elif current_time == row[0]:
                Humidity_Data.append(row)

        
    str_file.close()

#for row in Humidity_Data:
    #print(row)

##########################################################################
#
# Load the government data into a python data object.
#
##########################################################################

if len(AQ_Data) < 1:
    print('Retrieve Failed: No data in government data request')
    sys.exit()

humidity_dict = {}

# Load Humidity Data by monitor id into a dictionary.
for monitor in Humidity_Data:
    monitor_id = monitor[7].strip()
    if monitor_id.isnumeric():
        monitor_id = 'X' + monitor_id

    humidity = '50'
    if monitor[2] != '':
        humidity = monitor[2]

    humidity_dict[monitor_id] = humidity

#for monitor in humidity_dict:
    #print(monitor + ' ' + humidity_dict[monitor])


monitor_list = []
monitor_array = []

# Load airquality data into a python array in the same format as purple air data.
for monitor in AQ_Data:
    monitor_id = monitor[7].strip()
    if monitor_id.isnumeric():
        monitor_id = 'X' + monitor_id
    monitor_list.append(monitor_id)

    monitor_integer = int(monitor_id[1:])
    monitor_integer = 1000000000 + monitor_integer

    monitor_value = '0'
    if monitor[2] != '':
        monitor_value = monitor[2]

    humidity = '50'
    if monitor_id in humidity_dict:
        humidity = humidity_dict[monitor_id]

    daily_average = '0'
    if monitor_id in Daily_AQ_Data:
        daily_average = str(Daily_AQ_Data[monitor_id][2])


    try:
        monitor_datetime = datetime.strptime(monitor[0], '%Y-%m-%d %H:%M')
        #monitor_utc_datetime = monitor_datetime.replace(tzinfo=timezone.utc)
        #monitor_utc_timestamp = monitor_utc_datetime.timestamp()
        monitor_utc_timestamp = monitor_datetime.timestamp()
    except:
        print("Error 1")
        continue

    try:
        latitude = float(monitor[8])
    except ValueError:
        print("Error 2")
        continue

    try:
        longitude = float(monitor[9])
    except ValueError:
        print("Error 3")
        continue

    monitor_dict = {}
    monitor_dict['ID'] = monitor_integer
    monitor_dict["DateCreated"] = monitor_utc_timestamp
    monitor_dict["Lastseen"] = monitor_utc_timestamp
    monitor_dict['Name'] = monitor[1]
    monitor_dict['LocationType'] = 0
    monitor_dict["Lat"] = latitude
    monitor_dict["Lon"] = longitude
    monitor_dict["Humidity"] = humidity
    monitor_dict["PM2_5_Value"] = monitor_value
    monitor_dict["PM2_5_1_Hour"] = monitor_value
    monitor_dict["PM2_5_1_Day"] = daily_average

    monitor_array.append(monitor_dict)

    # For now only insert data for sunshine coast into tables.
    if (latitude < 49.34380) or (latitude > 49.88034):
        continue
    if (longitude > -123.43902) or (longitude < -124.65153):
        continue

    print(monitor_dict)



# Print out the monitor data.
#for monitor in monitor_array:
    #print(monitor)

#sys.exit()

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
    if (latitude < 49.34380) or (latitude > 49.88034):
        continue
    if (longitude > -123.43902) or (longitude < -124.65153):
        continue

    print(monitor)

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
