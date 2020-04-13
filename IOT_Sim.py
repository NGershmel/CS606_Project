#Noah Gershmel
#4/11/2020
#Internet of things Device Simulation


idCounter = 0 #Global variable to assign IDs to the devices
def nextID(): #Gets the next device ID to assign to a newly created device
    global idCounter
    idCounter = idCounter + 1
    return idCounter

#This class simulates an IOT device on a simulated network
class IOT_Device:
    #Reference to the network simulation, this is necessary to simulate broadcasts
    network = None

    '''These instance variables are utilized only if device is selected as a broker'''
    #Reference to the broker for this IOT device
    isBroker = False

    #This list should not be used unless the device is promoted to a broker
    #A 2D array of messages
        #Each message is an array of strings in the form:
        #[deviceID/-1, type/-1, message_data]
        #A message may or may not contain a deviceID that needs to retrieve it from the queue
        #A message may or may not contain a type to determine how that message should be handled
    messagesQueue = []

    #This list only contains the broker if this device is not a broker
    #This is a list of tuples for devices
        #Tuples are of the form (deviceId, IOT_Device)
    deviceList = []

    #Instance variables to ensure simulation of in and out of range devices
    locX = 0
    locY = 0
    signalRange = 0

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

    #Sets a reference to the network so that in-range calculations can be made
    def setNetwork(self, network_in):
        self.network = network_in

    #broadcastMessage(IOT_Device self, string message)
    #Sends a message to all devices in range
    def broadcastMessage(self, message):
        #TODO implemented in another python file to handle network issues,
        #Additionally, using the network and location this will only be sent to in range devices
        print("Broadcasting")

    #Sends a message to the broker with the intended deviceID that should retrieve it
    def sendMessage(self, message, deviceID):
        #TODO implemented in another python file to handle network issues
        print("Sending message to " + deviceID)

    #Sends a message to the broker that can be handled by any device that should handle such messages
    def sendMessage(self, message):
        #TODO implemented in another python file to handle network issues
        print("Sending message to broker")


#TODO ignore this for now, I will move it to another file
#This class simulates an entire network
#TODO this is where I (Noah) will handle MQTT style message passing
class Network_Sim:
    devices = []
    connections = []

    def __init__(self):
        self.name = "Network!"

    def addDevice(self, device_in):
        self.devices.append(device_in)
    
d1 = IOT_Device()
d2 = IOT_Device()
b1 = IOT_Device()
d1.setBroker(b1)
d2.setBroker(b1)
b1.setAsBroker()
n1 = Network_Sim()
n1.addDevice(d1)
n1.addDevice(d2)
n1.addDevice(b1)
print("Success")