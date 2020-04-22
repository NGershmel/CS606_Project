import IOT_Sim as iot
import threading
import Network_Functions as nf
import time
import random

#This class simulates an entire network
class Network_Sim:
    devices = []    #List of devices on the network
    connections = []    #List of direct connections on the network, this should only be used for debugging purposes
    threads = []    #List of threads spawned by the network to simulate devices, tracked so they can be joined

    drop_level = 0  #Percentage of messages that should be dropped in the network
    corruption_level = 0 #Percentage of messages that should be corrupted in the network

    #Blank initialization function
    def __init__(self):
        self.name = "Network"

    #Adds a new device to the network during setup
    def addDevice(self, device_in):
        self.devices.append(device_in)
        device_in.setNetwork(self)

    #Adds a device to the active network, must either elect a new broker or attach to an in-range broker
    def addDeviceLive(self, device_in):
        self.devices.append(device_in)
        device_in.setNetwork(self)
        newThread = threading.Thread(target=device_in.mainLoop)
        newThread.start()
        self.threads.append((True, newThread))

        #Begin a possible election to search for a broker to handle this new device
        electionThread = threading.Thread(target=device_in.startElection, args=(True,))
        electionThread.start()
        self.threads.append((False, electionThread))

    #Gets a reference to the device based on ID
    def getDevice(self, device_id):
        int_id = int(device_id)
        for d in self.devices:
            if (d.ID == int_id):
                return d
        return None

    #Simulates sending a message from a device to its broker
    def sendMessageDirect(self, message):
        device = self.getDevice(message[0])
        if not device.isBroker and not device.broker == None:
            if nf.dropMessage(self.drop_level):
                return
            message = nf.corrupt(message, self.corruption_level)
            bThread = threading.Thread(target=device.broker.receiveMessage, args=(message,))
            bThread.start()
            self.threads.append((False, bThread))
        elif nf.inRange(device, self.getDevice(message[1])):
            if nf.dropMessage(self.drop_level):
                return
            message = nf.corrupt(message, self.corruption_level)
            dThread = threading.Thread(target=self.getDevice(message[1]).receiveMessage, args=(message,))
            dThread.start()
            self.threads.append((False, dThread))

    #Simulates sending a message across a real network
    def sendMessage(self, deviceFrom, deviceTo, message):
        if nf.dropMessage(self.drop_level):
            return
        message = nf.corrupt(message, self.corruption_level)
        bThread = threading.Thread(target=deviceTo.receiveMessage, args=(message,))
        bThread.start()
        self.threads.append((False, bThread))

    #Simulates a device broadcasting a message across a real network
    def broadcastMessage(self, deviceFrom, message):
        print(str(deviceFrom.ID) + " is broadcasting " + str(message))
        for d in self.devices:
            if not d == deviceFrom and nf.inRange(deviceFrom, d):
                dThread = threading.Thread(target=d.receiveMessage, args=(message,))
                dThread.start()
                self.threads.append((False, dThread))

    #Simulation only broadcast, used for debugging and forcing network changes
    def broadcastMessageFromNetwork(self, message):
        for d in self.devices:
            dThread = threading.Thread(target=d.receiveMessage, args=(message,))
            dThread.start()
            self.threads.append((False, dThread))

    #Input from the user to run different simulation scenarios
    def simulateCommands(self):
        #This loops finishes all active simulation scenarios before allowing the user to introduce more
        print("Simulating...")
        time.sleep(2)
        for t in self.threads:
            if not t[0]:
                t[1].join()
        
        #Information and menu
        print("\n\n\n")
        print("Active IOT Devices:")
        for d in self.devices:
            if d.isBroker:
                print(d.name + " - Broker (" + str(d.ID) + ") [" + str(d.locX) + "," + str(d.locY) + "] >" + str(d.signalRange) + "<")
                for dList in d.deviceList:
                    print("    ->" + dList[0][0])
            else:
                if d.broker == None:
                    self.devices.remove(d)
                else:
                    print(d.name + " (" + str(d.ID) + ") [" + str(d.locX) + "," + str(d.locY) + "] >" + str(d.signalRange) + "<")
        print("\n\n1: Add device to network")
        print("2: Simulate Direct Message")
        print("3: Simulate Subscribe")
        print("4: Simulate Publish")
        print("5: Kill Device")
        print("-1: Kill Simulation")
        val = input("")
        if val == "-1":
            return -1
        if val == "1":
            x = float(input("X Location: "))
            y = float(input("Y Location: "))
            r = float(input("Signal Range: "))
            n = input("Name for this device: ")
            newDevice = iot.IOT_Device(n)
            newDevice.locX = x
            newDevice.locY = y
            newDevice.signalRange = r
            self.addDeviceLive(newDevice)
        elif val == "2":
            deviceFrom = input("Device sending message: ")
            deviceTo = input("Device to send message to: ")
            mType = input("Message Type: ")
            message = input("Message: ")
            self.sendMessage(getDevice(deviceFrom), getDevice(deviceTo), [deviceFrom, deviceTo, mType, message])
        elif val == "3":
            deviceFrom = input("Device to subscribe: ")
            topic = input("Topic to subscribe to: ")
            deviceRef = self.getDevice(deviceFrom)
            dThread = threading.Thread(target=deviceRef.subscribeToTopic, args=(topic,))
            dThread.start()
        elif val=="4":
            deviceFrom = input("Device to publish with: ")
            topic = input("Topic to publish to: ")
            message = input("Message: ")
            deviceRef = self.getDevice(deviceFrom)
            dThread = threading.Thread(target=deviceRef.publishToTopic, args=(topic, message,))
            dThread.start()
        elif val == "5":
            devKill = input("Device ID to kill: ")
            self.getDevice(devKill).receiveMessage(["-1", str(d.ID), "KILL", "KILL"])
            self.devices.remove(self.getDevice(devKill))


    #Network mainloop
    def simulate(self):
        for d in self.devices:
            d.setNetwork(self)
            newThread = threading.Thread(target=d.mainLoop)
            newThread.start()
            self.threads.append((True, newThread))
        while True:
            if self.simulateCommands() == -1:
                for d in self.devices:
                    d.receiveMessage(["-1", str(d.ID), "KILL", "KILL"])
                for t in self.threads:
                    t[1].join()
                break
    

#Set up an initial network to test with
#TODO move to another function with parameters for number of devices
random.seed()
n1 = Network_Sim()
d1 = iot.IOT_Device("Thermometer")
d1.locX = -1.0
d1.locY = 1.0
d1.signalRange = 4.0
d2 = iot.IOT_Device("Thermostat")
d2.locX = -1.0
d2.locY = 0.0
d2.signalRange = 4.0
d3 = iot.IOT_Device("Clock")
d3.locX = -1.0
d3.locY = -1.0
d3.signalRange = 4.0
b1 = iot.IOT_Device("Echo Dot")
b1.locX = 0.0
b1.locY = 0.0
b1.signalRange = 3.0
n1.addDevice(d1)
n1.addDevice(d2)
n1.addDevice(d3)
n1.addDevice(b1)
b1.setAsBroker()
d1.setBroker(b1)
d2.setBroker(b1)
d3.setBroker(b1)
d2.subscribeToTopic("Home/Temperature")
d1.subscribeToTopic("Home/Temperature")
n1.simulate()
print("Simulation Closed Properly")