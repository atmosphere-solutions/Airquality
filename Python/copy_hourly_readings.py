##########################################################################
#
#  Get monitor IDs from current_data table.
#  For each ID, get hourly data from the monitor_data table and insert into the hourly data table.
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
# Get a list of Monitor IDs from the current_data table.
#
##########################################################################
mycursor.execute("SELECT ID FROM current_data")
myresult = mycursor.fetchall()
monitor_ids = []
for x in myresult:
    monitor_ids.append(int(x[0]))
monitor_ids.sort()


##########################################################################
#
# For each ID, get hourly data from monitor_data table, then insert
# that data into each individual hourly table.
#
##########################################################################
HOURLY_TABLE_PREFIX = "Hourly_Readings_"

for monitor in monitor_ids:
    if (monitor == 1086):
        # Select all the hourly data for a single monitor from the monitor_data table..
        sql = "select DISTINCT(Lastseen), PM2_5Value from (select *, rank() over (partition by"
        sql = sql + " date_format(Lastseen, '%Y%m%d%H') order by Lastseen) rnk from monitor_data where ID="
        sql = sql + str(monitor) + ") t where t.rnk = 1;"
        mycursor.execute(sql)
        hourly_data = mycursor.fetchall()

        # Check if the hourly readings table exists and create it if it doesn't.
        hourly_table = HOURLY_TABLE_PREFIX + str(monitor)
        result = checkTableExists(mydb, hourly_table)
        if (result == False):
            column_names = [ ('PM2_5Value', 'DOUBLE'),
                             ('Lastseen', 'DATETIME PRIMARY KEY') ]
            createTable(mydb, hourly_table, column_names)

        # Insert historical data into hour table.
        for lastseen_dt, hourly_pmvalue in hourly_data:
            # Create SQL string to insert a row into the database table.
            sql = "REPLACE INTO " + hourly_table + " (Lastseen, PM2_5Value) VALUES (%s, %s)"

            # Create a list of the data we are going to insert into the table.
            val = (
                    lastseen_dt,
                    str(hourly_pmvalue)
                  )

            # Insert the data into the table.
            print("**********************INSERTING DATA**********************\n", sql, val)
            mycursor.execute(sql, val)
            mydb.commit()

