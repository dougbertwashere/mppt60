
from pyModbusTCP.client import ModbusClient
from Register import Register


#
#  Conext MPPT 60 150 charge controller
#       valueDecode functions
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
# Table of mppt60_registers with name, address, length, units, decode functions, offset values
#
mppt60_registers = [
   Register("DeviceName",                   0x0000, Register.String16),
   Register("FGA_Number",                   0x000A, Register.String20),
   Register("UniqueUD_Number",              0x0014, Register.TwoReg),
   Register("FirmwareVersion",              0x001E, Register.TwoReg),
   Register("ModbusAddress",                0x0028, Register.OneReg),
   Register("DeviceNumber",                 0x0029, Register.OneReg),
   Register("SystemInstance",               0x002A, Register.OneReg),
   Register("HW_SerialNumber",              0x002B, Register.String20),
   Register("ConfigStatus",                 0x0035, Register.OneReg, value_decode=decodeConfigStatus),
   Register("ConfigRefreshCounter",         0x0036, Register.TwoReg),
   Register("DeviceState",                  0x0040, Register.OneReg, value_decode=decodeDeviceState),
   Register("ChargerEnabledStatus",         0x0041, Register.OneReg, value_decode=decodeChargerStatus),
   Register("DevicePresent",                0x0042, Register.OneReg, value_decode=decodeDevicePresent),
   Register("ChargeModeStatus",             0x0043, Register.OneReg, value_decode=decodeChargeMode),
   Register("ActiveFaults",                 0x0044, Register.OneReg, value_decode=decodeActiveFaults),
   Register("ActiveWarnings",               0x0045, Register.OneReg, value_decode=decodeActiveWarnings),
   Register("FaultBitmap0",                 0x0046, Register.OneReg, value_decode=decodeFaultBitMap0),
   Register("FaultBitmap1",                 0x0047, Register.OneReg, value_decode=decodeFaultBitMap1),
   Register("WarningBitmap0",               0x0048, Register.OneReg, value_decode=decodeWarningBitMap0),
   Register("ChargerStatus",                0x0049, Register.OneReg, value_decode=decodeChargerControllerStatus),
   Register("ConfigurationErrors",          0x004A, Register.TwoReg),
   Register("PV_Voltage",                   0x004C, Register.TwoReg, unit="mV"),
   Register("PV_Current",                   0x004E, Register.TwoReg, unit="mA"),
   Register("PV_Power",                     0x0050, Register.TwoReg, unit="W"),
   Register("BatteryTemp",                  0x0056, Register.OneReg, unit="degC"),
   Register("DC_OutputVoltage",             0x0058, Register.TwoReg, unit="mV"),
   Register("DC_OutputCurrent",             0x005A, Register.TwoReg, unit="mA"),
   Register("DC_OutputPower",               0x005C, Register.TwoReg, unit="W"),
   Register("DC_OutputPowerPercent",        0x005E, Register.OneReg, unit="%"),
   Register("AuxOutputStatus",              0x005F, Register.OneReg, value_decode=decodeAuxOutputStatus),
   Register("AuxOutputVoltage",             0x0060, Register.TwoReg, unit="mV"),
   Register("AuxOutputOnReason",            0x0064, Register.OneReg, value_decode=decodeAuxOutputOnReason),
   Register("AuxOutputOffReason",           0x0065, Register.OneReg, value_decode=decodeAuxOutputOffReason),
   Register("EnergyFromPV_ThisHour",        0x0066, Register.TwoReg, unit="Wh"),
   Register("PV_InputActiveThisHour",       0x0068, Register.TwoReg, unit="sec"),
   Register("EnergyFromPV_Today",           0x006A, Register.TwoReg, unit="Wh"),
   Register("PV_InputActiveToday",          0x006C, Register.TwoReg, unit="sec"),
   Register("EnergyFromPV_ThisWeek",        0x006E, Register.TwoReg, unit="Wh"),
   Register("PV_InputActiveThisWeek",       0x0070, Register.TwoReg, unit="sec"),
   Register("EnergyFromPV_ThisMonth",       0x0072, Register.TwoReg, unit="Wh"),
   Register("PV_InputActiveThisMonth",      0x0074, Register.TwoReg, unit="sec"),
   Register("EnergyFromPV_ThisYear",        0x0076, Register.TwoReg, unit="Wh"),
   Register("PV_InputActiveThisYear",       0x0078, Register.TwoReg, unit="sec"),
   Register("EnergyFromPV_Lifetime",        0x007A, Register.TwoReg, unit="Wh"),
   Register("PV_InputActiveLifetime",       0x007C, Register.TwoReg, unit="sec"),
   Register("EnergyToBatteryThisHour",      0x007E, Register.TwoReg, unit="Wh"),
   Register("BatteryChareActiveThisHour",   0x0080, Register.TwoReg, unit="sec"),
   Register("EnergyToBatteryToday",         0x0082, Register.TwoReg, unit="Wh"),
   Register("EnergyChargeActiveToday",      0x0084, Register.TwoReg, unit="sec"),
   Register("EnergyToBatteryThisWeek",      0x0086, Register.TwoReg, unit="Wh"),
   Register("EnergyChargeActiveThisWeek",   0x0088, Register.TwoReg, unit="sec"),
   Register("EnergyToBatteryThisMonth",     0x008A, Register.TwoReg, unit="Wh"),
   Register("EnergyChargeActiveThisMonth",  0x008C, Register.TwoReg, unit="sec"),
   Register("EnergyToBatteryThisYear",      0x008E, Register.TwoReg, unit="Wh"),
   Register("EnergyChargeActiveThisYear",   0x0090, Register.TwoReg, unit="sec"),
   Register("EnergyToBatteryLifetime",      0x0092, Register.TwoReg, unit="Wh"),
   Register("EnergyChargeActiveLifetime",   0x0094, Register.TwoReg, unit="sec"),
   Register("MPPT",                         0x00A0, Register.OneReg, value_decode=decodeMPPT),
   Register("MPPTReferenceVoltage",         0x00A2, Register.TwoReg, unit="mV"),
   Register("BatteryType",                  0x00A5, Register.OneReg, value_decode=decodeBatteryType),
   Register("NominalBatteryVoltage",        0x00A6, Register.TwoReg, unit="mV", value_decode=decodeNominalBatteryVoltage),
   Register("BatteryBankCapacity",          0x00A8, Register.OneReg, unit="Ah"),
   Register("BatteryTempCoefficient",       0x00A9, Register.OneReg, unit="mV/degC"),
   Register("ForceChargerState",            0x00AA, Register.OneReg),
   Register("Reset",                        0x00AB, Register.OneReg),
   Register("OperatingMode",                0x00AC, Register.OneReg, value_decode=decodeOperatingMode),
   Register("Clear",                        0x00AD, Register.OneReg),
   Register("EqualizeVoltageSetPoint",      0x00AE, Register.TwoReg, unit="mV"),
   Register("BulkVoltageSetPoint",          0x00B0, Register.TwoReg, unit="mV"),
   Register("FloatVoltageSetPoint",         0x00B2, Register.TwoReg, unit="mV"),
   Register("RechargeVoltage",              0x00B4, Register.TwoReg, unit="mV"),
   Register("AbsorptionVoltageSetPoint",    0x00B6, Register.TwoReg, unit="mV"),
   Register("AbsorptionTime",               0x00B8, Register.OneReg, unit="min"),
   Register("ChargeCycle",                  0x00B9, Register.OneReg, value_decode=decodeChargeCycle),
   Register("MaximumChargeRate",            0x00BA, Register.OneReg, unit="%"),
   Register("EqualizeNow",                  0x00BB, Register.OneReg),
   Register("ChargeMode",                   0x00BE, Register.OneReg, value_decode=decodeChargeMode),
   Register("DefaultBatteryTemperature",    0x00BF, Register.OneReg),
   Register("IdentifyEnable",               0x00C0, Register.OneReg),
   Register("AuxOutputActiveLevel",         0x00C1, Register.OneReg),
   Register("AuxOutputVoltage",             0x00C2, Register.TwoReg, unit="mV"),
   Register("ManualAux",                    0x00C4, Register.OneReg),
   Register("AuxOutputTriggerSource",       0x00C6, Register.OneReg, value_decode=decodeAuxOutputTriggerSource),
   Register("LowBatteryVoltageTriggerSet",         0x00C8, Register.TwoReg, unit="mV"),
   Register("LowBatteryVoltageTriggerSetDelay",    0x00CA, Register.OneReg, unit="sec"),
   Register("LowBatteryVoltageTriggerClear",       0x00CC, Register.TwoReg, unit="mV"),
   Register("LowBatteryVoltageTriggerClearDelay",  0x00CE, Register.OneReg, unit="sec"),
   Register("HighBatteryVoltageTriggerSet",        0x00D0, Register.TwoReg, unit="mV"),
   Register("HighBatteryVoltageTriggerSetDelay",   0x00D2, Register.OneReg, unit="sec"),
   Register("HighBatteryVoltageTriggerClear",      0x00D4, Register.TwoReg, unit="mV"),
   Register("HighBatteryVoltageTriggerClearDelay", 0x00D6, Register.OneReg, unit="sec"),
   Register("HighArrayVoltageTriggerSet",          0x00D8, Register.TwoReg, unit="mV"),
   Register("HighArrayVoltageTriggerSetDelay",     0x00DA, Register.OneReg, unit="sec"),
   Register("HighArrayVoltageTriggerClear",        0x00DC, Register.TwoReg, unit="mV"),
   Register("HighArrayVoltageTriggerClearDelay",   0x00DE, Register.OneReg, unit="sec"),
   Register("LowBatteryTempTriggerSet",            0x00E0, Register.TwoReg, unit="degC", offset=-273),
   Register("LowBatteryTempTriggerSetDelay",       0x00E2, Register.OneReg, unit="sec"),
   Register("LowBatteryTempTriggerClear",          0x00E4, Register.TwoReg, unit="degC", offset=-273),
   Register("LowBatteryTempTriggerClearDelay",     0x00E6, Register.OneReg, unit="sec"),
   Register("HighBatteryTempTriggerSet",           0x00E8, Register.TwoReg, unit="degC", offset=-273),
   Register("HighBatteryTempTriggerSetDelay",      0x00EA, Register.OneReg, unit="sec"),
   Register("HighBatteryTempTriggerClear",         0x00EC, Register.TwoReg, unit="degC", offset=-273),
   Register("HighBatteryTempTriggerClearDelay",    0x00EE, Register.OneReg, unit="sec"),
   Register("HighHeatSinkTempTriggerSet",          0x00F0, Register.TwoReg, unit="degC", offset=-273),
   Register("HighHeatSinkTempTriggerSetDelay",     0x00F2, Register.OneReg, unit="sec"),
   Register("HighHeatSinkTempTriggerClear",        0x00F4, Register.TwoReg, unit="degC", offset=-273),
   Register("HighHeatSinkTempTriggerClearDelay",   0x00F6, Register.OneReg, unit="sec"),
   Register("RefreshConfigurationData",            0x00F8, Register.OneReg),
   Register("DCInputAssociation",                  0x00F9, Register.OneReg, value_decode=decodeDCInputAssociation),
   Register("BatteryAssociation",                  0x00FA, Register.OneReg, value_decode=decodeBatteryAssociation),
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
def getInfoFromCC(id, interface_host, debug):
    global mppt60_registers

    results = {}        # create a new empty results dict
    
    # Open client socket to gateway server
    try:
        c = ModbusClient(host=interface_host, port=503, unit_id=id, timeout=10, auto_close=True)
    except ValueError:
        print("Error with Host or Port parms")
        return None


    for reg in mppt60_registers:

        regName = reg.getRegName()
        regAddress = reg.getRegAddress()
        regType = reg.getRegType()
        regUnit = reg.getUnit()
        regOffset = reg.getOffset()

        # get register (encoded) value from server
        regValue = c.read_input_registers(regAddress, regType)

        # Determine if 
        #       1 or 2 int16 type
        # OR
        #       must be string type
        if regType == Register.OneReg or regType == Register.TwoReg:
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
        newAttributes["offset"] = regOffset 
        newAttributes["valueDecoded"] = valueDecoded

        # and add new entry keyed on the name of the register
        results[regName] = newAttributes
    
        if debug == True:
            print("Address: %s   Type:  %s   value: %s" % (regAddress, regType, value))

    c.close()

    return results
