# CS606_Project
MQTT Broker selection utilizing an election algorithm

# Running the project
Requires Python 3.6+ installed

Run the project by entering

`python Network_Sim.py`

# Display
## Devices
`Name (ID) [Xpos, YPos] >Range<`

For example:

`Thermostat (2) [-1.0, 0.0] >1.5<`

This denotes a device with name "Thermostat", device ID 2 (this can be thought of as a MAC Address), positioned at -1.0,0.0, and having a signal range of 1.5
## Brokers
```
Name - 'Broker' (ID) [Xpos, YPos] >Range<
    ->ID
    ->ID
```

For example:
```
Echo Dot - Broker (3) [0.0, 0.0] >6.0<
    ->1
    ->2
```
This denotes a device with name "Echo Dot", device ID 3, positioned at 0.0,0.0, and having a signal range of 6.0. The arrows denote clients that this broker is responsible for, so devices 1 and 2 are clients whose broker is device 3.


# Interacting with the Simulation
The simulation will start and you will be presented with a menu to utilize
1. Add Device
2. Simulate Direct Message
3. Simulate Subscribe
4. Simulate Publish
5. Kill Device
6. (-1) Kill Simulation

## Add Device
This is used to test our election algorithm and is the core simulation command for this project. It will ask for a location, name and signal range for the device. Once that information has been entered the device will attempt to connect to an in range broker. If no broker is found the device will elect and in range device to be a new broker. If no devices are in range the device will throw an error.

## Simulate Direct Message
This is used to test the voracity of the network. Simply enter the sender and receiver ID alongside the message to be sent. The message will attempt to send taking into account simulated network errors like dropping packets and corrupted data.

## Simulate Subscribe
Typically used after adding a new device to the network, this uses the network and simulated brokers to subscribe a client to a topic.

## Simulate Publish
Use this to test and ensure all subscribed clients do in fact receive the command sent by a publisher. This command will forward along all secondary brokers.

## Kill Device
This will kill a single device. If this device is a broker then upon its lack of response in a future subscribe/publish the network will attempt to elect a new broker. Note that due to the placement of brokers, a dead broker may mean that some devices are now out of range of the extended network.

## Kill simulation
This gracefully ends the program. All threads are joined and each device cleans itself as it gets removed from the network. Use this when you are done simulating rather than a keyboard interrupt for the smoothest experience.