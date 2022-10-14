#!/usr/bin/env python 

from pyModbusTCP.client import ModbusClient


InsightLocalHost = "insightlocal.lan"       #  Hostname or IP of Conext InsightLocal Gateway - modify/specify for other than default
mppt_id = [ 30, 31, 32, 33 ]                # Modbus IDs of the Conext CCsa

OneReg = 1
TwoReg = 2
String16 = 8
String20 = 10

debug = False

class Register(object):
    def __init__(self, 
            reg_name,       # Name of register
            reg_address,    # Register Address value
            reg_type        # Register Type:  number of 16 bit values to request -> 1, 2.   For strings:  8 for 16 chars, 10 for 20 chars
            ):
        
        self.reg_name = reg_name
        self.reg_address = reg_address
        self.reg_type = reg_type
        self.reg_value = None

    def setRegValue(self, reg_value):
        self.reg_value = reg_value

    def getRegValue(self):
        return self.reg_value

    def getRegName(self):
        return self.reg_name

    def getRegAddress(self):
        return self.reg_address

    def getRegType(self):
        return self.reg_type


# 
# Table of registers with name, address and length
#
registers = [
   Register("DeviceName",                   0x0000, String16),
   Register("FGA_Number",                   0x000A, String20),
   Register("UniqueUD_Number",              0x0014, TwoReg),
   Register("FirmwareVersion",              0x001E, TwoReg),
   Register("ModbusAddress",                0x0028, OneReg),
   Register("DeviceNumber",                 0x0029, OneReg),
   Register("SystemInstance",               0x002A, OneReg),
   Register("HW_SerialNumber",              0x002B, String20),
   Register("ConfigStatus",                 0x0035, OneReg),
   Register("ConfigRefreshCounter",         0x0036, TwoReg),
   Register("DeviceState",                  0x0040, OneReg),
   Register("ChargerEnabledStatus",         0x0041, OneReg),
   Register("DevicePresent",                0x0042, OneReg),
   Register("ChargeModStatus",              0x0043, OneReg),
   Register("ActiveFaults",                 0x0044, OneReg),
   Register("ActiveWarnings",               0x0045, OneReg),
   Register("FaultBitmap0",                 0x0046, OneReg),
   Register("FaultBitmap1",                 0x0047, OneReg),
   Register("WarningBitmap0",               0x0048, OneReg),
   Register("ChargerStatus",                0x0049, OneReg),
   Register("ConfigurationErrors",          0x004A, TwoReg),
   Register("PV_Voltage",                   0x004C, TwoReg),
   Register("PV_Current",                   0x004E, TwoReg),
   Register("PV_Power",                     0x0050, TwoReg),
   Register("BatteryTemp",                  0x0056, OneReg),
   Register("DC_OutputVoltage",             0x0058, TwoReg),
   Register("DC_OutputCurrent",             0x005A, TwoReg),
   Register("DC_OutputPower",               0x005C, TwoReg),
   Register("DC_OutputPowerPercent",        0x005E, OneReg),
   Register("AuxOutputStatus",              0x005F, OneReg),
   Register("AuxOutputVoltage",             0x0060, TwoReg),
   

   Register("EnergyFromPV_Today",           0x006A, TwoReg),
   ]

#
# toString a List of int16 values
#
#   String is encoded into the List,  2 chars per int16, decode to a proper string
#
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

#
# Number is encoded in a List of int16 - 1 or 2, convert to a proper integer
#
def intListToNumber(intList):
    ret_int = 0

    for i in intList:
        ret_int <<= 16

        ret_int |= i

    return ret_int


# 
# Retrieve info on the specified CC (by Modbus ID)
#
# Iterate over the 'register' list (containing Register instances) for attributes to retrieve
#
def getInfoFromCC(id):
    global InsightLocalHost
    global registers
    global debug

    results = []    # Init the results List to be returned
    
    # Open client socket to gateway server
    try:
        c = ModbusClient(host=InsightLocalHost, port=503, unit_id=id, timeout=10, auto_close=True)
    except ValueError:
        print("Error with Host or Port parms")
        return None


    for reg in registers:

        # get register (encoded) value
        regValue = c.read_input_registers(reg.reg_address, reg.reg_type)

        # Determine if 
        #       1 or 2 int16 type
        # OR
        #       must be string type
        if reg.reg_type == OneReg or reg.reg_type == TwoReg:
            # Form final value from the register contents
            value = intListToNumber(regValue)
        else:
            # Form final string from the register contents
            value = intListToString(regValue)
            
        reg.setRegValue( value )

        results.append(reg)
    
        if debug == True:
            print("Address: %s   Type:  %s   value: %s" % (reg.reg_address, reg.reg_type, value))

    c.close()

    return results



# Main entry point
def main():

    global mppt_id 

    mppts = {}

    # gather info from each of the MMPTs
    for id in mppt_id:

        reg_list = getInfoFromCC(id)

        print("MPPT %s" % id)

        for reg in reg_list:
            print("    Name: '%22s' --->   Value: '%s'" % (reg.getRegName(), reg.getRegValue()))

        mppts[id] = reg_list

    return 0


if __name__ == "__main__":
    main()
