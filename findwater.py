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
currentZone = 'White'
nextZone = 'Yellow'
prevZone = 'White'

RIGHT = 0
LEFT = 1
prevDirection = RIGHT

turnTime = 1.25
backupTime = 0.5

edgeCounter = 0


def stopGoBackTurnAndMove(turnTime=turnTime, isRandom=True):
    global prevDirection

    turnOnLED()
    stop()

    moveBackwards(power)
    time.sleep(backupTime)

    # Turn left/right randomly
    if isRandom:
        if random.randint(0, 1):
            rightTurn(power)
        else:
            leftTurn(power)
    # Turn based on the previous direction
    else:
        if prevDirection == LEFT:
            rightTurn(power)
            prevDirection = RIGHT
        else:
            leftTurn(power)
            prevDirection = LEFT

    time.sleep(turnTime)

    moveForward(power)
    turnOnLED(True)


def loop():
    global currentZone
    global nextZone
    global prevZone

    global edgeCounter

    distance = readSonicSensor()
    color = BP.get_sensor(BP.PORT_4)

    # On false positive reads continue with next loop
    if distance == 0:
        time.sleep(0.01)
        return

    # Obstacle found
    if distance <= 10:
        print("LOG found obstacle")
        stopGoBackTurnAndMove(isRandom=False)

    #  Got out of the current zone try to get back into it
    elif colors[color] == currentZone:
        if edgeCounter >= 3 and currentZone != 'Red':
            print("LOG turning 180")
            stopGoBackTurnAndMove(2)
            edgeCounter = 0
        else:
            stopGoBackTurnAndMove()
        edgeCounter += 1
        print("LOG backing up for color ", currentZone, colors[color])

    # Crossed the next zone update zone variables
    elif colors[color] == nextZone:
        prevZone = currentZone
        currentZone = nextZone
        nextZone = 'Red'
        edgeCounter = 0
        time.sleep(0.1)
        print("LOG found next zone should be in {} color".format(
            currentZone), colors[color])

    # Handle going back to the previous zone
    elif colors[color] == prevZone:
        nextZone = currentZone
        currentZone = prevZone
        print("LOG should back up for color in prev zone", colors[color])

    # Found water exit
    elif colors[color] == stopColor and currentZone == 'Red':
        turnOnLED(True)
        stop()
        print("LOG read blue exitting...")
        exit(0)

    time.sleep(0.001)


# Wait for sensor to be ready
while readSonicSensor() == 0:
    time.sleep(0.1)

moveForward(power)
time.sleep(0.5)

while 1:
    loop()
