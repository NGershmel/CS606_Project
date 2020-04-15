#Noah Gershmel
#4/11/2020
#Internet of things Device Simulation

import time

idCounter = 0 #Global variable to assign IDs to the devices
def nextID(): #Gets the next device ID to assign to a newly created device
    global idCounter
    idCounter = idCounter + 1
    return idCounter

#This class simulates an IOT device on a simulated network
class IOT_Device:
    #Boolean to gracefully kill the device
    kill_device = False

    #Reference to the network simulation, this is necessary to simulate broadcasts
    network = None
    broker = None

    '''These instance variables are utilized only if device is selected as a broker'''
    #Reference to the broker for this IOT device
    isBroker = False

    #This list should not be used unless the device is promoted to a broker
    #A 2D array of messages
        #Each message is an array of strings in the form:
        #[deviceID, deviceID/-1, type/-1, message_data]
        #A message must contain which deviceID sent the message
        #A message may or may not contain a deviceID that needs to retrieve it from the queue
        #A message may or may not contain a type to determine how that message should be handled
    messagesQueue = []
    #Tuple of form ("Topic", [IOT_Device]) 
    #Links topics to subscribers so that any message of a specific topic will get passed to all subscribers for that message
    subscribers = [] 

    #This list only contains the broker if this device is not a broker
    #This is a list of tuples for devices
        #Tuples are of the form (deviceId, IOT_Device)
    deviceList = []

    #Instance variables to ensure simulation of in and out of range devices
    #Default values mak sure all devices are in range of eachother
    locX = 0
    locY = 0
    signalRange = 1

    #This value is used to determine if messages that expect a response do in fact get one
    messageID = 0
    activeMessages = []

    #Initialize this class with the next ID
    def __init__(self):
        self.ID = nextID()

    #Set the broker for this device, this is where all messages will be passed to for this device
    #Additionally, the broker will be where this device retrieves messages from
    def setBroker(self, broker_in):
        self.broker = broker_in

    #Sets this device as a broker
    def setAsBroker(self):
        self.isBroker = True
        #TODO Noah will add functionality for the devices to be added to the brokers list

    #Sets a reference to the network so that in-range calculations can be made
    def setNetwork(self, network_in):
        self.network = network_in

    #broadcastMessage(IOT_Device self, string message)
    #Sends a message to all devices in range
    def broadcastMessage(self, message):
        self.network.broadcastMessage(self, message)

    #Sends a message to the broker with the intended deviceID that should retrieve it
    def sendMessage(self, message, deviceID):
        messageArray = [str(self.ID), str(deviceID), "NO_TYPE", message]
        self.network.sendMessage(messageArray)

    #Sends a message to the broker that can be handled by any device that should handle such messages
    def sendMessage(self, message):
        thisMessageID = messageID
        self.activeMessages.append(thisMessageID)
        self.network.sendMessage(message)
        time.sleep(2)
        for m_id in self.activeMessages:
            if m_id == thisMessageID:
                self.startElection(False)

    #Function to handle the receipt of a message
    def receiveMessage(self, message):
        print("Received on " + str(self.ID) + ": " + str(message))
        if message[2] == "KILL":
            self.kill_device = True

        if self.isBroker:
            #TODO the broker should pass the message to the correct broker or store it in its Queue if the message is for one of its devices
            self.messagesQueue.insert(0, message)
        else:
            if message[2] == "ELECTION":
                sendMessage([self.ID, message[0], "ELECTION_DATA", "VISIBLE"])
            elif message[2] == "COMMAND":
                print("Doing command")

    #This is the device function, it continuosly polls the broker to check for messages
    def mainLoop(self):
        while True:
            if self.kill_device:
                return

            if self.broker == None:
                pass #Possibly set to find a new broker here
            elif not self.isBroker and len(self.messagesQueue) > 0:
                #TODO handle the messages passed to this device from the broker and reply if necessary
                pass
            

    #TODO here is where our core algorithm should run
    #The flag will be true if the device is a new device attempting to find a broker
    def startElection(self, flag):
        #Example of newly added device searching for a broker
        if flag:
            self.broadcastMessage([str(self.ID), "-1", "SEARCH", "FIND_BROKER"])
            time.sleep(2)
            if self.broker == None:
                self.broadcastMessage([str(self.ID), "-1", "ELECTION", "VIABLE_BROKER"])
        #If the flag is true the device should broadcast searching for a broker with its ID
            #All broker devices that are in range will return a message entitled (IN-RANGE:ID:BROKER)
                #Here the ID is the ID of this device, in case multiple elections are running concurrently
                #Upon receiving an in-range ID, this device will set the BROKER to be this devices broker
                #No election needs to be run in this case
        #If the broadcast fails to find a broker in range or the flag is false, run the election algorithm
            #This version of the election algorithm should elevate another node to broker that is in range of this node
            #Find an in-range device that contacts the largest number of devices? and has contact to another broker
            #Verify against the main broker to see if there are out of range devices and attempt to find a device that can reach them