#Noah Gershmel
#4/14/2020
#Helper functions to simulate network interactions
#Functions help simulate wireless signals by calculating range, corruption and dropped messages

import IOT_Sim as iot
import math
import random

#Returns whether or not deviceTwo is within the signal range of deviceOne
def inRange(deviceOne, deviceTwo):
    if math.sqrt(math.pow(deviceOne.locX - deviceTwo.locX, 2) + math.pow(deviceOne.locY - deviceTwo.locY, 2)) < deviceOne.signalRange:
        return True
    return False

#Simulates randomly dropping messages
def dropMessage(threshold):
    value = random.randrange(100)
    return value < threshold

#Simulates randomly losing or corrupting data over a network
def corrupt(message, threshold):
    value = random.randrange(100)
    if (value < threshold):
        portion = random.randrange(4)
        position = random.randrange(len(message[portion]))
        message[portion][position] = '!'
    return message

#Computes the strength of a signal between 2 devices
def signalStrength(deviceOne, deviceTwo):
    if (deviceOne.locX - deviceTwo.locX) + (deviceOne.locY - deviceTwo.locY) == 0:
        return 999999
    return 1 / (math.sqrt(math.pow(deviceOne.locX - deviceTwo.locX, 2) + math.pow(deviceOne.locY - deviceTwo.locY, 2)))