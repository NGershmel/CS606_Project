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

    #This list should be used to track what messages have been given an OK
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
        self.broker.deviceList.append([(str(self.ID), self)])

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
        for m in self.messagesQueue:
            if m == messageData:
                self.messagesQueue.remove(messageData)

    #Simulates detecting a downed broker
    def allOk(self):
        if len(self.messagesQueue) > 0:
            return False
        return True

    #Simulates a device publishing a message to a topic
    def publishToTopic(self, topic, message):
        messageArray = [str(self.ID), topic, "PUBLISH", message]
        self.network.sendMessage(self, self.broker, messageArray)
        time.sleep(1)
        if not self.allOk():
            print("No response from broker to device " + str(self.ID))
            self.startElection(False)

    #Simulates a device subscribing to an MQTT topic
    def subscribeToTopic(self, topic):
        messageArray = [str(self.ID), topic, "SUBSCRIBE", topic]
        self.network.sendMessage(self, self.broker, messageArray)

    #Sends a message to the broker that can be handled by any device that should handle such messages
    def sendMessage(self, message):
        thisMessageID = messageID
        self.activeMessages.append(thisMessageID)
        self.network.sendMessage(message)
        time.sleep(2)
        for m_id in self.activeMessages:
            if m_id == thisMessageID:
                self.startElection(False)

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
    def publishToSubscribers(self, subscribers, message):
        for sub in subscribers:
            self.network.sendMessage(self, sub, message)

    #Function to handle the receipt of a message
    def receiveMessage(self, message):
        print("Received on " + str(self.ID) + ": " + str(message))
        #Default kill message to break down threads and allow the network to clean up
        if message[2] == "KILL":
            self.kill_device = True

        #If the device is a broker it needs to handle messages differently
        if self.isBroker:
            #If the device is marked as a direct message, then it should be passed forward to the correct device
            if (message[2] == "DIRECT"):
                forwardMessage(message)
            elif (message[2] == "SEARCH"):
                sendMessage([str(self.ID), message[0], "IN-RANGE", "IN-RANGE"])
            elif (message[2] == "PUBLISH"):
                self.publishToSubscribers(self.getSubscribersForTopic(message[1]), message)
                self.network.sendMessage(self, self.getDevice(message[0]), [str(self.ID), message[0], "OK", message[3]]) #Confirms that the broker received the message
                for devL in self.deviceList:
                    if len(devL) > 1: #Check for a broker list with subsequent devices, that broker may need to publish this message
                        self.network.sendMessage(self, devL[0][1], [str(self.ID), devL[0][0], "PUBLISH-FORWARD", message[3]])
            elif (message[2] == "PUBLISH-FORWARD"):
                self.network.sendMessage(self, self.getDevice(message[0]), [str(self.ID), message[0], "OK", message[3]])
                self.publishToSubscribers(self.getSubscribersForTopic(message[1]), message)
                for devL in self.deviceList:
                    if devL[0][0] != message[0] and len(devL) > 1:
                        self.network.sendMessage(self, devL[0][1], [str(self.ID), devL[0][0], "PUBLISH-FORWARD", message[3]])
            elif (message[2] == "SUBSCRIBE"):
                devRef = self.network.getDevice(message[0])
                self.subscribers.append((message[3], devRef))
                self.network.sendMessage(self, devRef, [str(self.ID), message[0], "OK", message[3]])
        else:
            if message[2] == "ELECTION":
                #TODO possibly send back information regarding signal strength or other prioity based values
                sendMessage([str(self.ID), message[0], "ELECTION_DATA", "VISIBLE"])
            elif message[2] == "IN-RANGE":
                self.broker = self.network.getDevice(message[0])
                self.broker.deviceList.append((str(self.ID), self))
            elif message[2] == "OK":
                self.clearFromQueue(message[3])
            elif message[2] == "COMMAND":
                print("Doing command: " + message[3])

    #This is the device function, it continuosly polls the broker to check for messages
    def mainLoop(self):
        while True:
            if self.kill_device:
                return
            if self.broker == None:
                pass #Possibly set to find a new broker here
            

    #TODO here is where our core algorithm should run
    #The flag will be true if the device is a new device attempting to find a broker
    def startElection(self, flag):
        #Example of newly added device searching for a broker
        if flag:
            self.broadcastMessage([str(self.ID), "-1", "SEARCH", "FIND_BROKER"])
            time.sleep(2)
            if self.broker == None:
                self.broadcastMessage([str(self.ID), "-1", "ELECTION", "VIABLE_BROKER"])
                election()
        else:
            self.broadcastMessage([str(self.ID), "-1", "ELECTION", "VIABLE_BROKER"])
            election()
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
        distance=[]
        for d in self.devices:
            distance.append(math.power(self.locX - d.locX, 2) + math.power(self.locY - d.locY, 2))
            d.priority = distance 
        neard = min(distance)
        for d in self.device:
            if (math.power(self.locX - d.locX, 2) + math.power(self.locY - d.locY, 2))>=d.priority:
                d.setAsBroker()
                self.setBroker(d)
                break
        