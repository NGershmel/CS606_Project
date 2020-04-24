#Noah Gershmel
#4/11/2020
#Internet of things Device Simulation

import time
import math
import Network_Functions

idCounter = 0 #Global variable to assign IDs to the devices
def nextID(): #Gets the next device ID to assign to a newly created device
    global idCounter
    idCounter = idCounter + 1
    return idCounter

#This class simulates an IOT device on a simulated network
class IOT_Device:
    #Initialize this class with the next ID
    def __init__(self, name):
        self.ID = nextID()
        self.name = name
        #Boolean to gracefully kill the device
        self.kill_device = False

        #Reference to the network simulation, this is necessary to simulate broadcasts
        self.network = None
        self.broker = None

        #Reference to the broker for this IOT device
        self.isBroker = False

        #This list should be used to track what messages have been given an OK
        #A 2D array of messages
            #Each message is an array of strings in the form:
            #[deviceID, deviceID/-1, type/-1, message_data]
            #A message must contain which deviceID sent the message
            #A message may or may not contain a deviceID that needs to retrieve it from the queue
            #A message may or may not contain a type to determine how that message should be handled
        self.messagesQueue = []
        #Tuple of form ("Topic", [IOT_Device]) 
        #Links topics to subscribers so that any message of a specific topic will get passed to all subscribers for that message
        self.subscribers = [] 

        #This list only contains the broker if this device is not a broker
        #This is a list of tuples for devices
            #Tuples are of the form (deviceId, IOT_Device)
        self.deviceList = []

        #Instance variables to ensure simulation of in and out of range devices
        #Default values mak sure all devices are in range of eachother
        self.locX = 0
        self.locY = 0
        self.signalRange = 1
        self.possibleBrokers = [] #Used during an election to find possible brokers

        #This value is used to determine if messages that expect a response do in fact get one
        self.activeMessages = []

    #Set the broker for this device, this is where all messages will be passed to for this device
    #Additionally, the broker will be where this device retrieves messages from
    def setBroker(self, broker_in):
        self.broker = broker_in
        if (self.isBroker):
            myList = self.flattenList()
            self.deviceList.append(self.broker.flattenList())
            self.broker.deviceList.append(myList)
        else:
            broker_in.addConnection(self.ID)
    #Sets this device as a broker
    def setAsBroker(self):
        self.isBroker = True

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

    #Removes a message from the list awaiting responses
    def clearFromQueue(self, messageData):
        for m in self.activeMessages:
            if m == messageData:
                self.activeMessages.remove(messageData)

    #Simulates detecting a downed broker
    def allOk(self):
        if len(self.activeMessages) > 0:
            return False
        return True

    #Simulates a device publishing a message to a topic
    def publishToTopic(self, topic, message):
        messageArray = [str(self.ID), topic, "PUBLISH", message]
        self.network.sendMessage(self, self.broker, messageArray)
        self.activeMessages.append(messageArray[3])
        time.sleep(1)
        if not self.allOk():
            print("No response from broker to device " + str(self.ID))
            self.startElection(False)

    #Simulates a device subscribing to an MQTT topic
    def subscribeToTopic(self, topic):
        messageArray = [str(self.ID), topic, "SUBSCRIBE", topic]
        self.activeMessages.append(topic)
        self.network.sendMessage(self, self.broker, messageArray)
        time.sleep(1)
        if not self.allOk():
            print("No response from broker to device " + str(self.ID))
            self.startElection(False)

    #Creates a 1 dimensional array of devices that are part of the brokers list to update another broker with
    def flattenList(self):
        flatList = [(str(self.ID), self)]
        for dList in self.deviceList:
            for d in dList:
                flatList.append(d)
        return flatList

    #Adds a new device to a brokers list
    def addConnection(self, dev):
        self.deviceList.append([(str(dev), self.network.getDevice(str(dev)))])

    #Sends a message to the broker that can be handled by any device that should handle such messages
    def sendMessage(self, devTo, message):
        self.network.sendMessage(self, self.network.getDevice(devTo), message)

    #This is done for any direct message received by a broker
    def forwardMessage(self, message):
        #If the device is in the list, send it
        for devList in self.deviceList:
            if devList[0][0] == message[1]:
                self.network.sendMessage(self, devList[0][1], message)
            else:
                #If the device is in a sublist, forward to the broker of that list
                for dev in devList:
                    if dev[0] == message[1]:
                        self.network.sendMessage(self, devList[0][1], message)

    #Returns a reference to another device (simulation a socket connection)
    def getDevice(self, devID):
        for dev in self.deviceList:
            if dev[0][0] == devID:
                return dev[0][1]

    #Scrapes the subscribers tuples and gets references to all devices subscribed to the topic
    def getSubscribersForTopic(self, topic):
        subList = []
        for dev in self.subscribers:
            if dev[0] == topic:
                subList.append(dev[1])
        return subList

    #Simulates an MQTT device publishing a message to a list of subscribers
    def publishToSubscribers(self, subscribers, message, sender):
        for sub in subscribers:
            if (not str(sub.ID) == sender):
                self.network.sendMessage(self, sub, [message[0], message[1], "COMMAND", message[3]])

    #Function to handle the receipt of a message
    def receiveMessage(self, message):
        if not self.kill_device:
            if self.isBroker:
                print("Received on " + str(self.ID) + " (Broker): " + str(message))
            else:
                print("Received on " + str(self.ID) + ": " + str(message))

            #Default kill message to break down threads and allow the network to clean up
            if message[2] == "KILL":
                self.kill_device = True

            #If the device is a broker it needs to handle messages differently
            if self.isBroker:
                #If the device is marked as a direct message, then it should be passed forward to the correct device
                if (message[2] == "DIRECT"):
                    self.forwardMessage(message)
                elif (message[2] == "SEARCH"):
                    self.sendMessage(message[0], [str(self.ID), message[0], "IN-RANGE", "IN-RANGE"])
                elif (message[2] == "PUBLISH"):
                    self.publishToSubscribers(self.getSubscribersForTopic(message[1]), message, message[0])
                    self.network.sendMessage(self, self.network.getDevice(message[0]), [str(self.ID), message[0], "OK", message[3]]) #Confirms that the broker received the message
                    for devL in self.deviceList:
                        if len(devL) > 1: #Check for a broker list with subsequent devices, that broker may need to publish this message
                            self.network.sendMessage(self, devL[0][1], [message[0] + ">" + str(self.ID) , message[1], "PUBLISH-FORWARD", message[3]])
                elif (message[2] == "PUBLISH-FORWARD"):
                    forwarder = message[0].split(">")[1]
                    sender = message[0].split(">")[0]
                    self.network.sendMessage(self, self.network.getDevice(forwarder), [str(self.ID), forwarder, "OK", message[3]])
                    self.publishToSubscribers(self.getSubscribersForTopic(message[1]), message, sender)
                    for devL in self.deviceList:
                        if devL[0][0] != forwarder and len(devL) > 1:
                            self.network.sendMessage(self, devL[0][1], [sender + ">" + str(self.ID), message[1], "PUBLISH-FORWARD", message[3]])
                elif (message[2] == "SUBSCRIBE"):
                    devRef = self.network.getDevice(message[0])
                    self.subscribers.append((message[3], devRef))
                    self.network.sendMessage(self, devRef, [str(self.ID), message[0], "OK", message[3]])
                elif message[2] == "OK":
                    self.clearFromQueue(message[3])
            else:
                if message[2] == "ELECTION":
                    self.sendMessage(message[0], [str(self.ID), message[0], "VIABLE", "VIABLE"])
                elif message[2] == "IN-RANGE":
                    self.setBroker(self.network.getDevice(message[0]))
                elif message[2] == "OK":
                    self.clearFromQueue(message[3])
                elif message[2] == "VIABLE":
                    self.possibleBrokers.append(int(message[0]))

    #This is the device function, it continuosly polls the broker to check for messages
    def mainLoop(self):
        while True:
            if self.kill_device:
                return
            if self.broker == None:
                pass #Possibly set to find a new broker here
            

    #The flag will be true if the device is a new device attempting to find a broker
    def startElection(self, flag):
        #Example of newly added device searching for a broker
        if flag:
            self.broadcastMessage([str(self.ID), "-1", "SEARCH", "FIND_BROKER"])
            time.sleep(1)
            if self.broker == None:
                self.election()
            else:
                print("Connecting to broker with ID " + str(self.broker.ID))
        else:
            self.election()
        #If the flag is true the device should broadcast searching for a broker with its ID
            #All broker devices that are in range will return a message entitled (IN-RANGE:ID:BROKER)
                #Here the ID is the ID of this device, in case multiple elections are running concurrently
                #Upon receiving an in-range ID, this device will set the BROKER to be this devices broker
                #No election needs to be run in this case
        #If the broadcast fails to find a broker in range or the flag is false, run the election algorithm
            #This version of the election algorithm should elevate another node to broker that is in range of this node
            #Find an in-range device that contacts the largest number of devices? and has contact to another broker
            #Verify against the main broker to see if there are out of range devices and attempt to find a device that can reach them

    def election(self):
        self.possibleBrokers = []
        self.broadcastMessage([str(self.ID), "-1", "ELECTION", "VIABLE_BROKER"])
        time.sleep(2)
        candidate = None
        maxStrength = 0.0
        for d in self.possibleBrokers:
            dev = self.network.getDevice(str(d))
            if Network_Functions.signalStrength(self, dev) > maxStrength:
                maxStrength = Network_Functions.signalStrength(self, dev)
                candidate = dev
        if candidate == None:
            print("Error, no devices in range")
            self.kill_device = True
        else:
            print("Electing " + str(candidate.ID) + " as a broker")
            candidate.setAsBroker()
            self.setBroker(candidate)
            candidate.broker.deviceList.remove([(str(candidate.ID), candidate)])
            visibleDevices = candidate.flattenList()
            parentDevices = candidate.broker.flattenList()
            candidate.broker.deviceList.append(visibleDevices)
            candidate.deviceList.append(parentDevices)
        