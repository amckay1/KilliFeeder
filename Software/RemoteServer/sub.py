#!/usr/bin/python
import datetime
import sqlite3
import time
import os
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import paho.mqtt.subscribe as subscribe
import struct
import csv

sqlite_file = '/home/ubuntu/.KilliFeeder/data/db.sqlite'

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


################################################################################
### Define functions
################################################################################
def checkclient(cid):
    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()
    c.execute("SELECT * FROM {tn} WHERE {idf}='{my_id}'"\
            .format(tn=table_name, cn=cal_column, my_id=cid, idf=id_column))

    id_exists = c.fetchone()
    conn.commit()
    conn.close()
    if id_exists:
        return True
    else:
        return False

def makeclient(cid):
    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()
    #### This worked for inserting new client_id in
    c.execute("INSERT OR IGNORE INTO {tn} ({idf}) VALUES ('{my_id}')"\
        .format(tn=table_name, idf=id_column, my_id=cid))

    conn.commit()
    conn.close()

def change_cal(cid,calmsg,senspt):
    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()
    ### use this to change orders/calibrated.  Updates the newly inserted or pre-existing entry
    c.execute("UPDATE {tn} SET {cn}=('{calm}') WHERE {idf}=('{my_id}')"\
            .format(tn=table_name, cn=cal_column, calm=calmsg, idf=id_column, my_id=cid))

    c.execute("UPDATE {tn} SET {cn}=('{calm}') WHERE {idf}=('{my_id}')"\
            .format(tn=table_name, cn=senspt_column, calm=senspt, idf=id_column, my_id=cid))

    conn.commit()
    conn.close()
    print("updated "+str(cid)+" "+str(calmsg)+" "+str(senspt))

def deltaorders(cid,neworders):
    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()
    ### use this to change orders/calibrated.  Updates the newly inserted or pre-existing entry
    c.execute("UPDATE {tn} SET {cn}=('{calm}') WHERE {idf}=('{my_id}')"\
            .format(tn=table_name, cn=order_column, calm=neworders, idf=id_column, my_id=cid))

    conn.commit()
    conn.close()
    print("Updated orders for: "+str(cid)+" to "+str(neworders))

def on_message(client, userdata, msg):
    if msg.topic == "ctime":
        print("ctime subject")
        messagecontent = msg.payload
        receivedmsg= messagecontent.decode('utf-8')
        print("msgcontent is")
        print(receivedmsg)
        ### check if client exists already
        client_id = receivedmsg.split(",")[0]
        print(client_id)
        if (not checkclient(client_id)):
            makeclient(client_id)

        actualvoltage = receivedmsg.split(",")[1]
        ttime = receivedmsg.split(",")[2]
        date = datetime.date.today()-datetime.timedelta(hours=8) # this is currently on UTC because on AWS, so now corrected
        date = date.isoformat()
        entryline = ",".join(map(str,[client_id, actualvoltage, ttime, date, "\n"]))
        print(entryline)
        f = open('/home/ubuntu/.KilliFeeder/data/ctimelog.csv', 'a+')
        f.write(entryline)
        f.close()
    elif msg.topic == "calibrate":  ### here need to change calibration status
        messagecontent = msg.payload
        print(messagecontent)
        receivedmsg= messagecontent.decode('utf-8').split(",")
        client_id = receivedmsg[0]
        calmsg = receivedmsg[1]
        senspt = receivedmsg[2]
        change_cal(client_id,calmsg,senspt)
    elif msg.topic == "cfeed":
        messagecontent = msg.payload
        receivedmsg= messagecontent.decode('utf-8').split(",")
        client_id = receivedmsg[0]
        ttime = receivedmsg[1]
        foodout = receivedmsg[2]
        foodin = receivedmsg[3]
        calibrated = receivedmsg[4]
        date = datetime.date.today()-datetime.timedelta(hours=8) # this is currently on UTC because on AWS, so now corrected
        date = date.isoformat()
        entryline = ",".join(map(str,[client_id, ttime, foodout, foodin, calibrated, date, "\n"]))
        f = open('/home/ubuntu/.KilliFeeder/data/cfeedlog.csv', 'a+')
        f.write(entryline)
        f.close()
    elif msg.topic == "deltaorder":  ### here need to change calibration status
        messagecontent = msg.payload
        print(messagecontent)
        receivedmsg= messagecontent.decode('utf-8').split(":")
        client_id = receivedmsg[0]
        neworders = receivedmsg[1]
        deltaorders(client_id,neworders)
    elif msg.topic == "deltacal":
        messagecontent = msg.payload
        print(messagecontent)
        receivedmsg= messagecontent.decode('utf-8').split(",")
        client_id = receivedmsg[0]
        newcal = receivedmsg[1]
        senspt = receivedmsg[2]
        change_cal(client_id,newcal,senspt)


def on_connect(client, userdata, flags, rc):
    print("Connected with result code " +str(rc))
    client.subscribe("ctime")
    client.subscribe("cfeed")
    client.subscribe("calibrate")
    client.subscribe("deltaorder")
    client.subscribe("deltacal")

client = mqtt.Client()
cafilepath = "/etc/mosquitto/ca_certificates/ca.crt"
client.tls_set(cafilepath)
client.on_connect = on_connect
client.on_message = on_message

client.connect("www.killifeeder.com", 8883)# ,60

# need to incorporate this code for the server
# mosquitto_sub --cafile /etc/mosquitto/ca_certificates/my-ca.crt -h www.KilliFeeder.com -t test -p 8883

client.loop_forever()

#while True:
    ## get ctime back and decode battery life
 #   subscribe.callback(on_message, "ctime")
#    time.sleep(1)

