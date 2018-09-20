# Proximity Occupation Sensor
# Main Server
# Version 1.4
# By Daniel Osmond 13197963
#
# 5/08/18
#
# This python script is written for a host server to be able to connect to MQTT and download information from the remote clients, then display that information in a html webpage
#
# 

#Libraries

#AWS MQTT IoT SDK
import AWSIoTPythonSDK.MQTTLib as AWSIoTPyMQTT

#time libraries
import time
import datetime

#json encoding/decoding libraries
import json
import jsonpickle

#commandline argument parsing
import argparse

#sqllite
import sqlite3

#Connect to SQL DB
sqlDB = sqlite3.connect("seating.db", check_same_thread=False)
cursor = sqlDB.cursor()
#Check to see if table exits, if not, create table
cursor.execute('''CREATE TABLE  IF NOT EXISTS seating (
   location TEXT PRIMARY KEY,
   status TEXT NOT NULL,
   date TEXT NOT NULL)''')

#Variable Declarations

seatList = dict()
debug = False
#Class Definitions

############################################################################
#   Class: Seat                                                            #
#   This class is used to store information about an available desk        #
#                                                                          #
#   Variables                                                              #
#   location: the physical location of the desk (i.e. CB11.08.600)         #
#   status: the occupancy status of the desk. 0 - unoccupied, 1 - occupied #
#   date: the time of the last occupancy status change                     #
############################################################################

class seat:
    def __init__(self, location, status, date):
        self.location = location
        self.status = status
        self.date = date


#Function definitions

###########################################################################
#   Function:dataRX                                                       #
#   This function is used to process incoming messages                    #
#                                                                         #
#   Variables (N.B. client and userdata are unused, pending depreciation) #
#   client : Client that sent the messages                                #
#   userdata: userdata that can be used in the processing of the callback #
#   payload: the main contents of the incoming messages                   #
###########################################################################


def dataRX(client, userdata, message):

     
    #verbose notification
    global debug
    if debug:
        print("[NOTICE] MQTT message recieved")

    #Pulls the payload from the message
    payloadJSON = message.payload
    #converts the message from json
    payload = json.loads(payloadJSON)
    #if the payload is a seat message

    if(payload[:4] == "seat"):
        #remove encoding
        pickledSeat = payload[4:]
        seat = jsonpickle.decode(pickledSeat)

        #add/update seat in dictionary
        seatList[seat.location] = seat
        
        #update SQL database & push changes
        params = (seat.location, seat.status, seat.date)
        cursor.execute('''INSERT OR REPLACE INTO seating  VALUES(?,?,?)''', params)
        sqlDB.commit()

def main():
    
    #ensure database is globally accessible
    global seatList


    #Use argparse to take in CLI arguments

    cliArgs = argparse.ArgumentParser()

    cliArgs.add_argument("-end", action="store", required =True, dest="endpoint", help="AWS IoT Endpoint")
    cliArgs.add_argument("-root", action="store", required = True, dest = "rootCA", help="AWS Root CA")
    cliArgs.add_argument("-cert", action="store", required=True, dest = "userCert", help ="Device Certificate")
    cliArgs.add_argument("-key", action="store", required=True, dest = "privateKey", help ="Device Private Key")
    cliArgs.add_argument("-id", action="store", required=True, dest = "clientID", help = "Device Client ID")
    cliArgs.add_argument("-top", action="store", dest="topic", default="studio/seating", help ="Topic Channel to Post")
    cliArgs.add_argument("-verbose", action="store_true", dest="debug", help="Enable verbose mode")

    args = cliArgs.parse_args()

    endpoint = args.endpoint #the endpoint/server that the mqtt connection is made to
    rootCA = args.rootCA #AWS's root certificate (Class 3 Public Primary)
    userCert = args.userCert
    privateKey = args.privateKey
    clientID = args.clientID
    topic = args.topic
    debug = args.debug



    # AWS MQTT Client Setup

    #Default port for auth'ed connection is 8883, 443 for websocket however codebase needs to be changed to implement
    port = 8883

    #Client Security config
    MQTTClient = None
    MQTTClient = AWSIoTPyMQTT.AWSIoTMQTTClient(clientID)
    MQTTClient.configureEndpoint(endpoint, port)
    MQTTClient.configureCredentials(rootCA, privateKey, userCert)

    #Client Server Connection Settings
    #Reconnect in event of temporary connection failure. (Initial time to wait before attempting to reconnect, maximum time to wait before attempting to reconnect, time for a connection to be considered stable (resets wait time to minimum)) All given in seconds
    MQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)

    #Configure queue size in event of connection offline. (size of queue, action to complete when queue full).
    #As the server only needs the latest data which will overwrite older data, no need to send older data, risks confusion
    MQTTClient.configureOfflinePublishQueueing(1, AWSIoTPyMQTT.DROP_OLDEST)

    #Configure rate at which to send queued messages (per second)
    MQTTClient.configureDrainingFrequency(2)

    #Configure time to wait for disconnect to complete (in seconds)
    MQTTClient.configureConnectDisconnectTimeout(10)

    #Configure publish, subscribe, unsubscribe operation timeout for QoS 1 service (seconds)
    MQTTClient.configureMQTTOperationTimeout(10)

    if debug:
        print("[NOTICE] MQTT configuration complete")
    #MQTT CONFIG COMPLETE


    #MQTT subscribe to check for incoming commands

    #Connect to MQTT service
    connectCheck = MQTTClient.connect()

    #Verbose connection notifiers
    if debug:
        if connectCheck:
            print("[NOTICE] Successfully connected to MQTT")
        else:
            print("[ERROR] Unsuccessful connection to MQTT")

    #subscribe to given topic channel
    subscribeCheck = MQTTClient.subscribe(topic, 0, dataRX)

    #Verbose subscription notifiers
    if debug:
        if subscribeCheck:
            print("[NOTICE] Successfully subscribed to %s" %(topic))
        else:
            print("[ERROR] Subscription to %s failed" %(topic))


    print("[NOTICE] Started Successfully")

    #if debug:
        #seatList["test"] = seat(location = "testLoc", status = "testStatus", date = time.asctime(time.localtime()))
    

    #set to automatically request an update upon startup
    userInput = "update"
    #progam runs while the user input is not "quit"
    while (userInput != "quit"):

        
        
        #since python doesn't support switch statements like C, if & elif used for command structure
        
        #send update request to remote clients
        if(userInput == "update"):
            #create JSON encoded update request
            messageJSON = json.dumps("update")
            #push request
            publishCheck = MQTTClient.publish(topic, messageJSON, 1)
            #notify user of result        
            if publishCheck:
                print("[NOTICE] Update request successfully sent")
            elif not publishCheck:
                print("[NOTICE] Update request was not sent successfully")

        #send shutdown request to remote clients
        elif(userInput == "shutdown"):
            #create JSON encoded update request
            messageJSON = json.dumps("stop")
            #push request
            publishCheck = MQTTClient.publish(topic, messageJSON, 1)
            #notify user of result        
            if publishCheck:
                print("[NOTICE] Shutdown request successfully sent")
            elif not publishCheck:
                print("[NOTICE] Shutdown request was not sent successfully")

        #print list of seats
        elif(userInput == "seating"):
            #cant iterate over an empty dict
            if (len(seatList) == 0):
                print("[ERROR] Seat Database is currently empty")
            else:
                #header
                print("Seat Location    Occupation    Timestamp")
                #for loop w/ formatting
                for chair in seatList:
                    chair = seatList[chair]
                    print("%-17s%-14s%s" %(chair.location, chair.status, chair.date))

        #allows the user to delete the database
        elif(userInput =="purgedb"):
            #doublecheck that they actually want this
            userInput = (input("This will delete the current database, are you sure (y/n)? "))
            #nuke database, commit changes, recreate, commit changes
            if(userInput=="y"):
                cursor.execute('''DROP TABLE seating''')
                sqlDB.commit()
                cursor.execute('''CREATE TABLE seating (
    location TEXT PRIMARY KEY,
   status TEXT NOT NULL,
   date TEXT NOT NULL)''')
                sqlDB.commit()
                seatList = dict() 
                print("DB deleted and recreated")

        #prints list of commands
        elif(userInput == "help"):
            print("\"update\" - sends a request to all remote sensors, requesting an occupancy status update, regardless of whether the occupancy has changed")
            print("\"shutdown\" - sends a request to all remote sensors to disconnect from MQTT and exit \"client.py\", this will require each remote sensor script to be restarted manually")
            print("\"seating\" - prints the lastest version of the seating status database")
            print("\"purgedb\" - deletes the current seating database, THIS CANNOT BE UNDONE")
            print("\"help\" - prints this menu")
            print("\"quit\" - disconnects this server from MQTT, and exits the current script")

        #if the command isnt recognised
        else:
            print("[NOTICE] Invalid command, type \"help\" for all commands") 



        #get user input
        userInput = (input("Enter a command> ")).lower()


    #user has input quit
    #disconnect from MQTT
    MQTTClient.disconnect()

    #disconnect database
    sqlDB.commit()
    sqlDB.close()
    #notify user, even if not in verbose mode
    print("[NOTICE] Shutting Down")



if (__name__== "__main__"):
    main()
