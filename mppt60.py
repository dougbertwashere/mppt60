#!/usr/bin/env python 

from pyModbusTCP.client import ModbusClient


# String are encoded,  2 chars per int16, in a List of int16, decode to a string
def intListToString(intList):
    ret_str = ""

    for i in intList:
        c1 = (i >> 8) & 0xff
        if c1 == 0:
            break
        ret_str += chr(c1)

        c1 = i & 0xFF
        if c1 == 0:
            break
        ret_str += chr(c1)

    return ret_str

# Number is encoded in a List of int16 - 1 or 2, convert to an integer
def intListToNumber(intList):
    ret_int = 0

    for i in intList:
        ret_int <<= 16

        ret_int |= i

    return ret_int


# Get info on a specified CC

def getInfoFromCC(id):

    results = {}
    
    # Open client socket to gateway server
    try:
        c = ModbusClient(host="insightlocal.lan", port=503, unit_id=id, timeout=10, auto_close=True)
    except ValueError:
        print("Error with Host or Port parms")
        return None


    # get name
    deviceName = c.read_input_registers(0x0000,8)

    deviceNameString = intListToString(deviceName)
    results['deviceName']= deviceNameString

    # get Unique ID Number
    uniqueIDList = c.read_input_registers(0x0014,2)

    uniqueID = intListToNumber(uniqueIDList)
    results['uniqueID'] = uniqueID

    # get kwh produced today - in watt-hour
    wattHoursList = c.read_input_registers(0x006A,2)

    wattHours = intListToNumber(wattHoursList)
    results['wattHours'] = wattHours

    return results


# Main entry point
def main():

    mppt_id = [ 30, 31, 32, 33 ]

    wattHours = 0

    for id in mppt_id:

        results = getInfoFromCC(id)

        print("MPPT %s" % id)
        print("    Name: '%s'" % results['deviceName'])
#        print("    Unique ID: '%s'" % results['uniqueID'])
        print("    watt-hours: %s" % results['wattHours'])

        wattHours += results['wattHours']

    print("")
    print("Total Watt-Hours: %s" % wattHours)
    return 0


if __name__ == "__main__":
    main()
