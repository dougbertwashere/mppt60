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
            reg_name,           # Name of register
            reg_address,        # Register Address value
            reg_type,           # Register Type:  number of 16 bit values to request -> 1, 2.   For strings:  8 for 16 chars, 10 for 20 chars
            value_decode=None   # value decode function, if any
            ):
        
        self.reg_name = reg_name
        self.reg_address = reg_address
        self.reg_type = reg_type
        self.value_decode = value_decode

    def getRegName(self):
        return self.reg_name

    def getRegAddress(self):
        return self.reg_address

    def getRegType(self):
        return self.reg_type

    def getValueDecode(self):
        return self.value_decode

#
#  valueDecode functions
#
def decodeConfigStatus(value):
    return ["Refreshing", "Done"][value]

def decodeDeviceState(value):
    if value == 255:
        return "Data Not Available"

    if value < 0 or value > 5:
        return "Invalid State Value"

    return ["Hibernate", "Power Save", "Safe Mode", "Operating", "Diagnostic Mode", "Remote Power OFff"][value]

def decodeChargerStatus(value):
    return ["Disabled", "Enabled"][value]

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
   Register("ConfigStatus",                 0x0035, OneReg, decodeConfigStatus),
   Register("ConfigRefreshCounter",         0x0036, TwoReg),
   Register("DeviceState",                  0x0040, OneReg, decodeDeviceState),
   Register("ChargerEnabledStatus",         0x0041, OneReg, decodeChargerStatus),
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
   Register("AuxOutputOnReason",            0x0064, OneReg),
   Register("AuxOutputOffReason",           0x0065, OneReg),
   Register("EnergyFromPV_ThisHour",        0x0066, TwoReg),
   Register("PV_InputActiveThisHour",       0x0068, TwoReg),
   Register("EnergyFromPV_Today",           0x006A, TwoReg),
   Register("PV_InputActiveToday",          0x006C, TwoReg),
   Register("EnergyFromPV_ThisWeek",        0x006E, TwoReg),
   Register("PV_InputActiveThisWeek",       0x0070, TwoReg),
   Register("EnergyFromPV_ThisMonth",       0x0072, TwoReg),
   Register("PV_InputActiveThisMonth",      0x0074, TwoReg),
   Register("EnergyFromPV_ThisYear",        0x0076, TwoReg),
   Register("PV_InputActiveThisYear",       0x0078, TwoReg),
   Register("EnergyFromPV_Lifetime",        0x007A, TwoReg),
   Register("PV_InputActiveLifetime",       0x007C, TwoReg),
   Register("EnergyToBatteryThisHour",      0x007E, TwoReg),
   Register("BatteryChareActiveThisHour",   0x0080, TwoReg),
   Register("EnergyToBatteryToday",         0x0082, TwoReg),
   Register("EnergyChargeActiveToday",      0x0084, TwoReg),
   Register("EnergyToBatteryThisWeek",      0x0086, TwoReg),
   Register("EnergyChargeActiveThisWeek",   0x0088, TwoReg),
   Register("EnergyToBatteryThisMonth",     0x008A, TwoReg),
   Register("EnergyChargeActiveThisMonth",  0x008C, TwoReg),
   Register("EnergyToBatteryThisYear",      0x008E, TwoReg),
   Register("EnergyChargeActiveThisYear",   0x0090, TwoReg),
   Register("EnergyToBatteryLifetime",      0x0092, TwoReg),
   Register("EnergyChargeActiveLifetime",   0x0094, TwoReg),
   Register("MPPT",                         0x00A0, OneReg),
   Register("MPPTReferenceVoltage",         0x00A2, TwoReg),
   Register("BatteryType",                  0x00A5, OneReg),
   Register("NominalBatteryVoltage",        0x00A6, TwoReg),
   Register("BatteryBankCapacity",          0x00A8, OneReg),
   Register("BatteryTempCoefficient",       0x00A9, OneReg),
   Register("ForceChargerState",            0x00AA, OneReg),
   Register("Reset",                        0x00AB, OneReg),
   Register("OperatingMode",                0x00AC, OneReg),
   Register("Clear",                        0x00AD, OneReg),
   Register("EqualizeVoltageSetPoint",      0x00AE, TwoReg),
   Register("BulkVoltageSetPoint",          0x00B0, TwoReg),
   Register("FloatVoltageSetPoint",         0x00B2, TwoReg),
   Register("RechargeVoltage",              0x00B4, TwoReg),
   Register("AbsorptionVoltageSetPoint",    0x00B6, TwoReg),
   Register("AbsorptionTime",               0x00B8, OneReg),
   Register("ChargeCycle",                  0x00B9, OneReg),
   Register("MaximumChargeRate",            0x00BA, OneReg),
   Register("EqualizeNow",                  0x00BB, OneReg),
   Register("ChargeMode",                   0x00BE, OneReg),
   Register("DefaultBatteryTemperature",    0x00BF, OneReg),
   Register("IdentifyEnable",               0x00C0, OneReg),
   Register("AuxOutputActiveLevel",         0x00C1, OneReg),
   Register("AuxOutputVoltage",             0x00C2, TwoReg),
   Register("ManualAux",                    0x00C4, OneReg),
   Register("AuxOutputTriggerSource",       0x00C6, OneReg),
   Register("LowBatteryVoltageTriggerSet",         0x00C8, TwoReg),
   Register("LowBatteryVoltageTriggerSetDelay",    0x00CA, OneReg),
   Register("LowBatteryVoltageTriggerClear",       0x00CC, TwoReg),
   Register("LowBatteryVoltageTriggerClearDelay",  0x00CE, OneReg),
   Register("HighBatteryVoltageTriggerSet",        0x00D0, TwoReg),
   Register("HighBatteryVoltageTriggerSetDelay",   0x00D2, OneReg),
   Register("HighBatteryVoltageTriggerClear",      0x00D4, TwoReg),
   Register("HighBatteryVoltageTriggerClearDelay", 0x00D6, OneReg),
   Register("HighArrayVoltageTriggerSet",          0x00D8, TwoReg),
   Register("HighArrayVoltageTriggerSetDelay",     0x00DA, OneReg),
   Register("HighArrayVoltageTriggerClear",        0x00DC, TwoReg),
   Register("HighArrayVoltageTriggerClearDelay",   0x00DE, OneReg),
   Register("LowBatteryTempTriggerSet",            0x00E0, TwoReg),
   Register("LowBatteryTempTriggerSetDelay",       0x00E2, OneReg),
   Register("LowBatteryTempTriggerClear",          0x00E4, TwoReg),
   Register("LowBatteryTempTriggerClearDelay",     0x00E6, OneReg),
   Register("HighBatteryTempTriggerSet",           0x00E8, TwoReg),
   Register("HighBatteryTempTriggerSetDelay",      0x00EA, OneReg),
   Register("HighBatteryTempTriggerClear",         0x00EC, TwoReg),
   Register("HighBatteryTempTriggerClearDelay",    0x00EE, OneReg),
   Register("HighHeatSinkTempTriggerSet",          0x00F0, TwoReg),
   Register("HighHeatSinkTempTriggerSetDelay",     0x00F2, OneReg),
   Register("HighHeatSinkTempTriggerClear",        0x00F4, TwoReg),
   Register("HighHeatSinkTempTriggerClearDelay",   0x00F6, OneReg),
   Register("RefreshConfigurationData",            0x00F8, OneReg),
   Register("DCInputAssociation",                  0x00F9, OneReg),
   Register("BatteryAssociation",                  0x00FA, OneReg),
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
# Return a dict, with 'register names' as the key, and an attribute dict as the value 
# 
def getInfoFromCC(id):
    global InsightLocalHost
    global registers
    global debug

    results = {}        # create a new empty results dict
    
    # Open client socket to gateway server
    try:
        c = ModbusClient(host=InsightLocalHost, port=503, unit_id=id, timeout=10, auto_close=True)
    except ValueError:
        print("Error with Host or Port parms")
        return None


    for reg in registers:

        regName = reg.getRegName()
        regAddress = reg.getRegAddress()
        regType = reg.getRegType()

        # get register (encoded) value from server
        regValue = c.read_input_registers(regAddress, regType)

        # Determine if 
        #       1 or 2 int16 type
        # OR
        #       must be string type
        if regType == OneReg or regType == TwoReg:
            # Form final value from the register contents
            value = intListToNumber(regValue)
        else:
            # Form final string from the register contents
            value = intListToString(regValue)
            
         
        decoder = reg.getValueDecode()
        valueDecoded = ""

        # If there is a decode function for value, run it
        if decoder != None:
            valueDecoded = decoder(value)

        # get new dict for the attributes
        newAttributes = {}
        newAttributes["reg_address"] = regAddress
        newAttributes["reg_type"] = regType
        newAttributes["value"] = value 
        newAttributes["valueDecoded"] = valueDecoded

        # and add new entry keyed on the name of the register
        results[regName] = newAttributes
    
        if debug == True:
            print("Address: %s   Type:  %s   value: %s" % (regAddress, regType, value))

    c.close()

    return results



# Main entry point
def main():

    global mppt_id 

    mppts = {}

    # gather info from each of the MMPTs
    for id in mppt_id:

        reg_dict = getInfoFromCC(id)

        print("MPPT %s" % id)

        for reg in reg_dict:
            strHex = "0x%0.4X" % reg_dict[reg]["reg_address"]

            decoded = reg_dict[reg]["valueDecoded"]
            if decoded != "":
                decoded = "[Decode: %s]" % decoded
            
            print("    %s Name: '%35s' --->   Value: '%s'  %s" % (strHex, reg, reg_dict[reg]["value"], decoded))

        mppts[id] = reg_dict

    return 0

if __name__ == "__main__":
    main()
