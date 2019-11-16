#!/usr/bin/python3

import serial
import time     # import the time library for the sleep function
import brickpi3  # import the BrickPi3 drivers

# Global constants
MOVE = 6
READ_SENSOR = 7
SET_LED_RED = 8
SET_LED_GREEN = 9

# Global variables
ser = None
BP = None


# Turns on LED red or green and turns off the other one
def turnOnLED(isGreen=False):
    cmd = SET_LED_RED
    if isGreen:
        cmd = SET_LED_GREEN

    sendCommand("{}".format(cmd))
    readReply()


# Moves robot in any direction based on power
def move(power1, power2):
    sendCommand("{} {} {}".format(MOVE, power1, power2))
    readReply()


# Move main helpers
def stop():
    move(125, 125)


def moveForward(power):
    move(power, power)


def moveBackwards(power):
    move(-power, -power)


def rightTurn(power):
    move(power, -power)


def leftTurn(power):
    move(-power, power)


#  Reads sonic sensor and returns the distance
def readSonicSensor():
    sendCommand("{}".format(READ_SENSOR))
    readReply()
    distance = readReply()

    return distance


def sendCommand(command: str):
    print("Sending " + command)
    command += ' \n'
    ser.write(command.encode())
    ser.flush()


def readReply():
    input = ser.readline()
    ackResult = int(input)
    print("Read input ::" + str(ackResult) + " from Arduino")
    input = ser.readline()  # eat the extra newline char

    # Print error
    if ackResult == -1:
        print("ERROR: Did not send recognized command to arduino")

    return ackResult


def initHandshake():
    # send out data to PRIZM until it reply
    cmd = 1
    while 1:
        cmdStr = str(cmd)
        cmdStr += '  100'
        print("Sending out handshaking signal ::" + cmdStr + " to Arduino")
        cmdStr += ' \n'
        ser.write(cmdStr.encode())
        ser.flush()
        input = ser.readline()
        if input == "" or len(input) == 0:
            print("Read NOTHING")
        else:
            ackResult = int(input)
            print("Read input ::" + str(ackResult) + " from Arduino")
            print(" ************************* \n\n\n\n")
            print(" Get Connected to PRIZM !! ")
            print(" ************************* ")
            input = ser.readline()  # eat the extra newline char

            # once receive the handshake message, exit
            return
        cmd = cmd+1
        if cmd == 5:
            cmd = 1

        time.sleep(0.1)


def initializeSerialCon():
    global ser
    global BP

    try:
        # Create an instance of the BrickPi3 class. BP will be the BrickPi3 object.
        BP = brickpi3.BrickPi3()
        print("BrickPi3 connected and running")
    except brickpi3.FirmwareVersionError as error:
        print(error)
    except:
        print("Communication with BrickPi3 unsuccessful")

    # test communication with Tetrix controller
    print("Pi: set up serial port; this will *** RESET *** PRIZM board !!!!")
    ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
    time.sleep(2)  # wait for 2 second for reset PRIZM

    print("***************************************************** ")
    print("Please press the GREEN button to start PRIZM board !!!!")
    print("***************************************************** ")

    initHandshake()

    return ser, BP
