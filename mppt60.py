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
            unit="-",         # VALUE unit
            value_decode=None   # value decode function, if any
            ):
        
        self.reg_name = reg_name
        self.reg_address = reg_address
        self.reg_type = reg_type
        self.unit = unit
        self.value_decode = value_decode

    def getRegName(self):
        return self.reg_name

    def getRegAddress(self):
        return self.reg_address

    def getRegType(self):
        return self.reg_type

    def getUnit(self):
        return self.unit

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

def decodeDevicePresent(value):
    return ["Inactive", "Active - Data Valid"][value]

def decodeChargeMode(value):
    return ["Stand Alone", "Primary", "Secondary"][value]

def decodeActiveFaults(value):
    return ["No Active Faults", "Has Active Faults"][value]

def decodeActiveWarnings(value):
    return ["No Active Warning", "Has Active Warnings"][value]

def decodeFaultBitMap0(value):
    faultMap = {
        1<<0:"F2:Capacitor Over-Temperature",
        1<<1:"F4:Battery Over-Temperature",
        1<<2:"F5:Ambient Over-Temperature",
        1<<3:"F9:DC Over-Voltage",
        1<<4:"F10:Output Under-Voltage Immediate",
        1<<5:"F11:Output Under-Voltage",
        1<<6:"F26:Auxiliary Power Supply",
        1<<7:"F30:Battery Under-Temperature",
        1<<8:"F54:Auxiliary Power Supply",
        1<<9:"F55:Heatsink Over-Temperature",
        1<<10:"F56:Ground Fault",
        1<<11:"F69:Configuration Fault",
        1<<12:"F70:DC Over-Voltage",
        1<<13:"F71:DC Over-current2",
        1<<14:"F72:SPS Overload",
        1<<15:"F73:Slow Output Over-Current",
    }

    result = ""

    # Scan each bit in the value, if set then map to a decoded string from the dict 
    for i in range (16):
        bitNum = 1 << i
        if value & bitNum:
            result += faultMap[bitNum] + " "

    return result



def decodeFaultBitMap1(value):
    faultMap = {
        1<<0:"F74:Input Over-Voltage",
        1<<1:"F75:Fan Over-Voltage",
        1<<2:"F76:Fan Over-Current",
        1<<3:"F77:Input Over-Current",
        1<<4:"F78:Output Over-Current",
        1<<5:"F79:Fan Over-Current",
        1<<6:"F80:Fan Under-Voltage",
        1<<7:"F81:Fan Under-Current",
        1<<8:"F82:Network Power Supply Failure",
        1<<9:"F90:External BMS Disconnected",
    }

    result = ""

    # Scan each bit in the value, if set then map to a decoded string from the dict 
    for i in range (16):
        bitNum = 1 << i
        if value & bitNum:
            result += faultMap[bitNum] + " "

    return result


def decodeWarningBitMap0(value):
    warningMap = {
        1<<0:"W11:DC Input Over Voltage Warning",
    }

    result = ""

    # Scan each bit in the value, if set then map to a decoded string from the dict 
    for i in range (16):
        bitNum = 1 << i
        if value & bitNum:
            result += warningMap[bitNum] + " "

    return result


def decodeChargerControllerStatus(value):
    statusMap = {
        768:"Not Charging",
        769:"Bulk",
        770:"Absorption",
        771:"Overcharge",
        772:"Equalize",
        773:"Float",
        774:"No Float",
        775:"Constant VI",
        776:"Charger Disabled",
        777:"Qualifying AC",
        778:"Qualifying APS",
        779:"Engaging Charger",
        780:"Charge Fault",
        781:"Charger Suspend",
        782:"AC Good",
        783:"APS Good",
        784:"AC Fault",
        785:"Charge",
        786:"Absorption Exit Pending",
        787:"Ground Fault",
        788:"AC Good Pending",
    }

    if value not in statusMap:
        return "Unknown Status"
    
    return statusMap[value]


def decodeAuxOutputStatus(value):
    return ["Auto On", "Auto Off", "Manual On", "Manual Off"][value]


def decodeAuxOutputOnReason(value):
    return ["Not on", 
            "Manual On", 
            "Battery Voltage Low", "Battery Voltage High", 
            "Array Voltage High", 
            "Battery Temp Low", "Battery Temp High", 
            "Heat Sink Temp High", 
            "Fault"][value]


def decodeAuxOutputOffReason(value):
    return ["Not on", 
            "Manual Off", 
            "No Active Trigger",
            "Trigger Override",
            "Fault",
            "Bulk Exit",
            "Absporption Exit"][value]

def decodeMPPT(value):
    return ["Disabled", "Enabled"][value]

def decodeBatteryType(value):
    return ["Flooded", "Gel", "AGM", "Custom"][value]


def decodeNominalBatteryVoltage(value):
    return str(int(value / 1000)) + "V"

def decodeOperatingMode(value):
    return ["", "", "Standby", "Operating"][value]

def decodeChargeCycle(value):
    return ["", "3 Stage", "2 Stage (No Float)"][value]

def decodeChargeMode(value):
    return ["Stand-Alone", "Primary", "Secondary", "Echo"][value]

def decodeAuxOutputTriggerSource(value):
    result = {
            1:"Low Battery Voltage",
            2:"High Battery Voltage",
            4:"High Array Voltage",
            8:"Low Battery Temperature",
            16:"High Battery Temperature",
            32:"High Heatsink Temperature",
            64:"Fault",
            }

    return result[value]

def decodeDCInputAssociation(value):
    return "Solar Array " + str(value - 20)

def decodeBatteryAssociation(value):
    return "House Battery Bank " + str(value - 2)



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
   Register("ConfigStatus",                 0x0035, OneReg, value_decode=decodeConfigStatus),
   Register("ConfigRefreshCounter",         0x0036, TwoReg),
   Register("DeviceState",                  0x0040, OneReg, value_decode=decodeDeviceState),
   Register("ChargerEnabledStatus",         0x0041, OneReg, value_decode=decodeChargerStatus),
   Register("DevicePresent",                0x0042, OneReg, value_decode=decodeDevicePresent),
   Register("ChargeModeStatus",             0x0043, OneReg, value_decode=decodeChargeMode),
   Register("ActiveFaults",                 0x0044, OneReg, value_decode=decodeActiveFaults),
   Register("ActiveWarnings",               0x0045, OneReg, value_decode=decodeActiveWarnings),
   Register("FaultBitmap0",                 0x0046, OneReg, value_decode=decodeFaultBitMap0),
   Register("FaultBitmap1",                 0x0047, OneReg, value_decode=decodeFaultBitMap1),
   Register("WarningBitmap0",               0x0048, OneReg, value_decode=decodeWarningBitMap0),
   Register("ChargerStatus",                0x0049, OneReg, value_decode=decodeChargerControllerStatus),
   Register("ConfigurationErrors",          0x004A, TwoReg),
   Register("PV_Voltage",                   0x004C, TwoReg, unit="mV"),
   Register("PV_Current",                   0x004E, TwoReg, unit="mA"),
   Register("PV_Power",                     0x0050, TwoReg, unit="W"),
   Register("BatteryTemp",                  0x0056, OneReg, unit="degC"),
   Register("DC_OutputVoltage",             0x0058, TwoReg, unit="mV"),
   Register("DC_OutputCurrent",             0x005A, TwoReg, unit="mA"),
   Register("DC_OutputPower",               0x005C, TwoReg, unit="W"),
   Register("DC_OutputPowerPercent",        0x005E, OneReg, unit="%"),
   Register("AuxOutputStatus",              0x005F, OneReg, value_decode=decodeAuxOutputStatus),
   Register("AuxOutputVoltage",             0x0060, TwoReg, unit="mV"),
   Register("AuxOutputOnReason",            0x0064, OneReg, value_decode=decodeAuxOutputOnReason),
   Register("AuxOutputOffReason",           0x0065, OneReg, value_decode=decodeAuxOutputOffReason),
   Register("EnergyFromPV_ThisHour",        0x0066, TwoReg, unit="Wh"),
   Register("PV_InputActiveThisHour",       0x0068, TwoReg, unit="sec"),
   Register("EnergyFromPV_Today",           0x006A, TwoReg, unit="Wh"),
   Register("PV_InputActiveToday",          0x006C, TwoReg, unit="sec"),
   Register("EnergyFromPV_ThisWeek",        0x006E, TwoReg, unit="Wh"),
   Register("PV_InputActiveThisWeek",       0x0070, TwoReg, unit="sec"),
   Register("EnergyFromPV_ThisMonth",       0x0072, TwoReg, unit="Wh"),
   Register("PV_InputActiveThisMonth",      0x0074, TwoReg, unit="sec"),
   Register("EnergyFromPV_ThisYear",        0x0076, TwoReg, unit="Wh"),
   Register("PV_InputActiveThisYear",       0x0078, TwoReg, unit="sec"),
   Register("EnergyFromPV_Lifetime",        0x007A, TwoReg, unit="Wh"),
   Register("PV_InputActiveLifetime",       0x007C, TwoReg, unit="sec"),
   Register("EnergyToBatteryThisHour",      0x007E, TwoReg, unit="Wh"),
   Register("BatteryChareActiveThisHour",   0x0080, TwoReg, unit="sec"),
   Register("EnergyToBatteryToday",         0x0082, TwoReg, unit="Wh"),
   Register("EnergyChargeActiveToday",      0x0084, TwoReg, unit="sec"),
   Register("EnergyToBatteryThisWeek",      0x0086, TwoReg, unit="Wh"),
   Register("EnergyChargeActiveThisWeek",   0x0088, TwoReg, unit="sec"),
   Register("EnergyToBatteryThisMonth",     0x008A, TwoReg, unit="Wh"),
   Register("EnergyChargeActiveThisMonth",  0x008C, TwoReg, unit="sec"),
   Register("EnergyToBatteryThisYear",      0x008E, TwoReg, unit="Wh"),
   Register("EnergyChargeActiveThisYear",   0x0090, TwoReg, unit="sec"),
   Register("EnergyToBatteryLifetime",      0x0092, TwoReg, unit="Wh"),
   Register("EnergyChargeActiveLifetime",   0x0094, TwoReg, unit="sec"),
   Register("MPPT",                         0x00A0, OneReg, value_decode=decodeMPPT),
   Register("MPPTReferenceVoltage",         0x00A2, TwoReg, unit="mV"),
   Register("BatteryType",                  0x00A5, OneReg, value_decode=decodeBatteryType),
   Register("NominalBatteryVoltage",        0x00A6, TwoReg, unit="mV", value_decode=decodeNominalBatteryVoltage),
   Register("BatteryBankCapacity",          0x00A8, OneReg, unit="Ah"),
   Register("BatteryTempCoefficient",       0x00A9, OneReg, unit="mV/degC"),
   Register("ForceChargerState",            0x00AA, OneReg),
   Register("Reset",                        0x00AB, OneReg),
   Register("OperatingMode",                0x00AC, OneReg, value_decode=decodeOperatingMode),
   Register("Clear",                        0x00AD, OneReg),
   Register("EqualizeVoltageSetPoint",      0x00AE, TwoReg, unit="mV"),
   Register("BulkVoltageSetPoint",          0x00B0, TwoReg, unit="mV"),
   Register("FloatVoltageSetPoint",         0x00B2, TwoReg, unit="mV"),
   Register("RechargeVoltage",              0x00B4, TwoReg, unit="mV"),
   Register("AbsorptionVoltageSetPoint",    0x00B6, TwoReg, unit="mV"),
   Register("AbsorptionTime",               0x00B8, OneReg, unit="min"),
   Register("ChargeCycle",                  0x00B9, OneReg, value_decode=decodeChargeCycle),
   Register("MaximumChargeRate",            0x00BA, OneReg, unit="%"),
   Register("EqualizeNow",                  0x00BB, OneReg),
   Register("ChargeMode",                   0x00BE, OneReg, value_decode=decodeChargeMode),
   Register("DefaultBatteryTemperature",    0x00BF, OneReg),
   Register("IdentifyEnable",               0x00C0, OneReg),
   Register("AuxOutputActiveLevel",         0x00C1, OneReg),
   Register("AuxOutputVoltage",             0x00C2, TwoReg, unit="mV"),
   Register("ManualAux",                    0x00C4, OneReg),
   Register("AuxOutputTriggerSource",       0x00C6, OneReg, value_decode=decodeAuxOutputTriggerSource),
   Register("LowBatteryVoltageTriggerSet",         0x00C8, TwoReg, unit="mV"),
   Register("LowBatteryVoltageTriggerSetDelay",    0x00CA, OneReg, unit="sec"),
   Register("LowBatteryVoltageTriggerClear",       0x00CC, TwoReg, unit="mV"),
   Register("LowBatteryVoltageTriggerClearDelay",  0x00CE, OneReg, unit="sec"),
   Register("HighBatteryVoltageTriggerSet",        0x00D0, TwoReg, unit="mV"),
   Register("HighBatteryVoltageTriggerSetDelay",   0x00D2, OneReg, unit="sec"),
   Register("HighBatteryVoltageTriggerClear",      0x00D4, TwoReg, unit="mV"),
   Register("HighBatteryVoltageTriggerClearDelay", 0x00D6, OneReg, unit="sec"),
   Register("HighArrayVoltageTriggerSet",          0x00D8, TwoReg, unit="mV"),
   Register("HighArrayVoltageTriggerSetDelay",     0x00DA, OneReg, unit="sec"),
   Register("HighArrayVoltageTriggerClear",        0x00DC, TwoReg, unit="mV"),
   Register("HighArrayVoltageTriggerClearDelay",   0x00DE, OneReg, unit="sec"),
   Register("LowBatteryTempTriggerSet",            0x00E0, TwoReg, unit="degC"),
   Register("LowBatteryTempTriggerSetDelay",       0x00E2, OneReg, unit="sec"),
   Register("LowBatteryTempTriggerClear",          0x00E4, TwoReg, unit="degC"),
   Register("LowBatteryTempTriggerClearDelay",     0x00E6, OneReg, unit="sec"),
   Register("HighBatteryTempTriggerSet",           0x00E8, TwoReg, unit="degC"),
   Register("HighBatteryTempTriggerSetDelay",      0x00EA, OneReg, unit="sec"),
   Register("HighBatteryTempTriggerClear",         0x00EC, TwoReg, unit="degC"),
   Register("HighBatteryTempTriggerClearDelay",    0x00EE, OneReg, unit="sec"),
   Register("HighHeatSinkTempTriggerSet",          0x00F0, TwoReg, unit="degC"),
   Register("HighHeatSinkTempTriggerSetDelay",     0x00F2, OneReg, unit="sec"),
   Register("HighHeatSinkTempTriggerClear",        0x00F4, TwoReg, unit="degC"),
   Register("HighHeatSinkTempTriggerClearDelay",   0x00F6, OneReg, unit="sec"),
   Register("RefreshConfigurationData",            0x00F8, OneReg),
   Register("DCInputAssociation",                  0x00F9, OneReg, value_decode=decodeDCInputAssociation),
   Register("BatteryAssociation",                  0x00FA, OneReg, value_decode=decodeBatteryAssociation),
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
        regUnit = reg.getUnit()

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
        newAttributes["unit"] = regUnit 
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
            
            print("    %s Name: '%35s' --->   Value: '%s' (%s)  %s" % (strHex, reg, reg_dict[reg]["value"], reg_dict[reg]["unit"], decoded))

        mppts[id] = reg_dict

    return 0

if __name__ == "__main__":
    main()
