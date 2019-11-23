#!/usr/bin/python3

import signal
import serial
import random
import time     # import the time library for the sleep function
import brickpi3  # import the BrickPi3 drivers

from comInterface import initializeSerialCon, readSonicSensor, stop, moveForward, moveBackwards, rightTurn, leftTurn, turnOnLED

# Global variables
ser, BP = initializeSerialCon()

# Configure for an EV3 color sensor.
BP.set_sensor_type(BP.PORT_4, BP.SENSOR_TYPE.EV3_COLOR_COLOR)

power = 20
colors = {
    0: "none",
    1: "Black",
    2: "Blue",
    3: "Green",
    4: "Yellow",
    5: "Red",
    6: "White",
    7: "Brown"
}
stopColor = 'Blue'
currentZone = 'Green'
nextZone = 'Red'

turnTime = 1.25
backupTime = 0.5


def stopGoBackTurnAndMove():
    turnOnLED()
    stop()

    moveBackwards(power)
    time.sleep(backupTime)

    # Turn left/right
    if random.randint(0, 1):
        rightTurn(power)
    else:
        leftTurn(power)

    # Random time is the right/left degree turn
    time.sleep(turnTime)

    moveForward(power)
    turnOnLED(True)


def loop():
    global currentZone
    global nextZone

    distance = readSonicSensor()
    color = BP.get_sensor(BP.PORT_4)

    # On false positive reads continue with next loop
    if distance == 0:
        time.sleep(0.01)
        return

    if distance <= 20:
        stopGoBackTurnAndMove()
    elif colors[color] == currentZone:
        stopGoBackTurnAndMove()
    elif colors[color] == nextZone:
        currentZone = nextZone
        nextZone = 'Yellow'
    elif colors[color] == stopColor:
        turnOnLED(True)
        print("read blue exitting...")
        stop()
        exit(0)

    time.sleep(0.001)


# Wait for sensor to be ready
while readSonicSensor() == 0:
    time.sleep(0.1)

moveForward(power)
time.sleep(0.5)

while 1:
    loop()
