import IOT_Sim as iot
import threading
import Network_Functions as nf

#This class simulates an entire network
class Network_Sim:
    devices = []    #List of devices on the network
    connections = []    #List of direct connections on the network, this should only be used for debugging purposes
    threads = []    #List of threads spawned by the network to simulate devices, tracked so they can be joined

    #Blank initialization function
    def __init__(self):
        self.name = "Network"

    #Adds a new device to the network during setup
    def addDevice(self, device_in):
        self.devices.append(device_in)

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
        for d in self.devcies:
            if (d.ID == int_id):
                return d
        return None

    #Simulates sending a message from a device to its broker
    def sendMessage(self, message):
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
    def sendMessage(self, deviceFrom, deviceTo):
        print("Sending message from " + deviceFrom.ID + " to " + deviceTo.ID)

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
        for t in self.threads:
            if not t[0]:
                t[1].join()

        #Information and menu
        print("Active IOT Devices:")
        for d in self.devices:
            print("Devcie ID: " + str(d.ID))
        print("1: Add device to network")
        print("2: Send Command")
        print("-1: Kill Simulation")
        val = input("")
        if val == "-1":
            return -1
        if val == "1":
            x = float(input("X Location: "))
            y = float(input("Y Location: "))
            r = float(input("Signal Range: "))
            newDevice = iot.IOT_Device()
            newDevice.locX = x
            newDevice.locY = y
            newDevice.signalRange = r
            self.addDeviceLive(newDevice)

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
d1 = iot.IOT_Device()
d2 = iot.IOT_Device()
b1 = iot.IOT_Device()
d1.setBroker(b1)
d2.setBroker(b1)
b1.setAsBroker()
n1 = Network_Sim()
n1.addDevice(d1)
n1.addDevice(d2)
n1.addDevice(b1)
n1.simulate()
print("Simulation Closed Properly")