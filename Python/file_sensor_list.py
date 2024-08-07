##########################################################################
#
#  This script loads a list of all sensors from BC and stores their
#  constant data into a file for later usage.
#
#  Here are the columns that are stored with this query:
#  (https://api.purpleair.com/#api-sensors-get-sensor-data)
#
#   "last_seen"       - The UNIX time stamp of the last time the server received data from the device.
#   "sensor_index"    - The sensor_id of the new member sensor. This must be AS PRINTED on the sensor’s label.
#   "name"            - The name given to the sensor from the registration form and used on the PA map.
#   "location_type"   - The location type.  Possible values are: 0 = Outside or 1 = Inside.
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
from datetime import datetime


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
storage_array = []

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

    monitor_array.append(monitor_dict)


##########################################################################
#
#  Store a copy of the data for each sensor into a file.  This file will
#  later be used to populate of SQL databases.   The goal of this is
#  to reduce the amount of data retrieved from purple air.  We will
#  run this once per day, which will mean new sensors will not show up
#  until the next day.
#
##########################################################################


##########################################################################
#
# For each unique sensor on the sunshine coast and for each outdoor
# sensor in the rest of the region, add to the sensor info file.
#
##########################################################################
SENSOR_INFO_FILE_NAME = "sensor_info.json"

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

    if location_type is None:
        location_type = -1

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

    # Create a dictionary for storing parsed data.
    storage_dict = {}
    storage_dict['ID'] = index
    storage_dict["DateCreated"] = datecreated_dt
    storage_dict["Lastseen"] = lastseen_dt
    storage_dict['Name'] = name
    storage_dict['LocationType'] = location_type
    storage_dict["Lat"] = latitude
    storage_dict["Lon"] = longitude

    # Only include inside sensors on sunshine coast.  Also
    # add a flag indicating that the sensor is on the coast
    # and add a flag saying its a purple air sensor.
    if (latitude > 49.34380) and (latitude < 49.88034) and (longitude < -123.43902) and (longitude > -124.65153):
        monitor["sunshine"] = 1
        monitor["purple"] = 1
        storage_array.append(monitor)
    else if (
    	
    

    
