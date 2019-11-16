#include <Wire.h>  // include the PRIZM library in the sketch
#include <PRIZM.h> // include the PRIZM library in the sketch
PRIZM prizm;       // instantiate a PRIZM object “prizm” so we can use its functions

// Commands
#define MOVE 6
#define READ_SENSOR 7
#define SET_LED_RED 8
#define SET_LED_GREEN 9

// Global variables
String inputString = "";        // a string to hold incoming data
boolean stringComplete = false; // whether the string is complete
int cmd = 0;
int paraOne = 0;
int paraTwo = 0;
int inputIndex = 0;
String cmdStr = "";
String paraStr = "";
int cmdStrIndex = 0;

int ackValue = 0;
String outputString = "";

void setup()
{
    // initialize serial:
    Serial.begin(9600);

    // init prizm
    prizm.PrizmBegin();
    prizm.setMotorInvert(1, 1);

    // reserve 200 bytes for the inputString:
    inputString.reserve(200);
    outputString.reserve(200);
    cmdStr.reserve(20);
    paraStr.reserve(20);
}

void loop()
{
    // print the string when a newline arrives:
    if (stringComplete)
    {
        //at this moment, the single line command is in inputString
        inputString.trim();
        cmdStr = getValue(inputString, ' ', 0);

        executeCommand(cmdStr.toInt());
        sendResponse(cmdStr);
        cleanup();
    }
}

void executeCommand(int cmd)
{
    switch (cmd)
    {
    case MOVE:
        move();
        break;
    case READ_SENSOR:
        readSensor();
        break;
    case SET_LED_RED:
        prizm.setGreenLED(LOW);
        prizm.setRedLED(HIGH);
        break;
    case SET_LED_GREEN:
        prizm.setGreenLED(HIGH);
        prizm.setRedLED(LOW);
        break;
    default:
        // Unrecognized command
        sendResponse("-1");
    }
}

void move()
{
    String power1 = getValue(inputString, ' ', 1);
    String power2 = getValue(inputString, ' ', 2);

    prizm.setMotorPowers(power1.toInt(), power2.toInt());
}

void readSensor()
{
    int distance = prizm.readSonicSensorCM(3);

    sendResponse(String(distance));
}

void sendResponse(String res)
{
    //prepare the acknowledge message, end with '\n'
    res += " \n";
    Serial.println(res);
}

// clear the string for next round:
void cleanup()
{
    inputString = "";
    outputString = "";
    stringComplete = false;
}

/*
  SerialEvent occurs whenever a new data comes in the
 hardware serial RX.  This routine is run between each
 time loop() runs, so using delay inside loop can delay
 response.  Multiple bytes of data may be available.
 */
void serialEvent()
{
    while (Serial.available())
    {
        // get the new byte:
        char inChar = (char)Serial.read();
        // add it to the inputString:
        inputString += inChar;
        // if the incoming character is a newline, set a flag
        // so the main loop can do something about it:
        if (inChar == '\n')
        {
            stringComplete = true;
        }
    }
}

// Split string at the separator and return the index sent in the string
String getValue(String data, char separator, int index)
{
    int found = 0;
    int strIndex[] = {0, -1};
    int maxIndex = data.length() - 1;

    for (int i = 0; i <= maxIndex && found <= index; i++)
    {
        if (data.charAt(i) == separator || i == maxIndex)
        {
            found++;
            strIndex[0] = strIndex[1] + 1;
            strIndex[1] = (i == maxIndex) ? i + 1 : i;
        }
    }
    return found > index ? data.substring(strIndex[0], strIndex[1]) : "";
}
