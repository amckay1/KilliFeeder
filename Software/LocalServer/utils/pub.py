#!/usr/bin/python
import datetime
import sqlite3
import time
import paho.mqtt.publish as publish
import os

sqlite_file = '/home/pi/.KilliFeeder/data/db.sqlite'

table_name = 'clients'   # name of the table to be created
id_column = 'client_id' # name of the PRIMARY KEY column
order_column = 'orders'  # name of the new column
senspt_column = 'senspt'
cal_column = 'calibrated'  # name of the new column


################################################################################
# Connecting and creating the database file #
################################################################################
if (not os.path.isfile(sqlite_file)):
    default_val_ord = ",".join(map(str,[434*60, 614*60, 734*60, 1094*60])) # a default value for the new column rows
    default_val_cal = 'no' # a default value for the new column rows
    default_val_spt = '88'
    column_type = 'TEXT' # E.g., INTEGER, TEXT, NULL, REAL, BLOB
    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()
    # Creating a second table with 1 column and set it as PRIMARY KEY
    # note that PRIMARY KEY column must consist of unique values!
    c.execute('CREATE TABLE {tn} ({nf} {ft} PRIMARY KEY)'\
            .format(tn=table_name, nf=id_column, ft=column_type))

    c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct} DEFAULT '{df}'"\
            .format(tn=table_name, cn=order_column, ct=column_type, df=default_val_ord))

    c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct} DEFAULT '{df}'"\
            .format(tn=table_name, cn=cal_column, ct=column_type, df=default_val_cal))

    c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct} DEFAULT '{df}'"\
            .format(tn=table_name, cn=senspt_column, ct=column_type, df=default_val_spt))
    # Committing changes and closing the connection to the database file
    conn.commit()
    conn.close()
################################################################################

### need to also publish "orders" for all client ids, reference csv,
### setup new topic if new client with defaults and calibrated flag = "no"

###  initialize counter and client_list
i = 0
def getclients_orders():
    ordersdict = {}
    caldict = {}
    sensptdict = {}
    client_list = []
    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()
    c.execute('SELECT {coi},{coi2},{coi3},{coi4} FROM {tn}'.\
            format(coi=id_column, coi2=order_column, coi3=cal_column, coi4=senspt_column,tn=table_name))
    all_rows = c.fetchall()
    conn.commit()
    conn.close()
    for i in all_rows:
        client_list.append(str(i[0]))
        ordersdict[str(i[0])] = str(i[1])
        caldict[str(i[0])] = str(i[2])
        sensptdict[str(i[0])] = str(i[3])

    return client_list,ordersdict,caldict,sensptdict

### initialize client_list
client_list,ordersdict,caldict,sensptdict = getclients_orders()
print(sensptdict)
print(client_list)
### publish time and orders
i = 0
while True:
    now = datetime.datetime.now()
    secondtime = (now.second)+(now.minute*60)+(now.hour*60*60)
    publish.single("time", payload=secondtime, qos=0, retain=True) # was False
    print(secondtime)
    print(i)
    ### every 1000 iterations, check the csv file and look for new client_ids to publish to:
    client_list,ordersdict,caldict,sensptdict = getclients_orders()
    ### loop through and publish orders for all clients
    if i > 5:
        i = 0
        print(client_list)
        for client_id in client_list:
            print(client_id)
            topic = str("orders/"+client_id)
            specificorders =  ",".join(map(str,[ordersdict[client_id],caldict[client_id],sensptdict[client_id]]))
            print(specificorders)
            publish.single(topic, payload=specificorders, qos=0, retain=True) # was False

    print("repeat")
    i= i+1
    time.sleep(1)

