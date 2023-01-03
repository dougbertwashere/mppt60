

class Register(object):

    OneReg = 1
    TwoReg = 2
    String16 = 8
    String20 = 10


    def __init__(self, 
            reg_name,           # Name of register
            reg_address,        # Register Address value
            reg_type,           # Register Type:  number of 16 bit values to request -> 1, 2.   For strings:  8 for 16 chars, 10 for 20 chars
            unit="-",           # VALUE unit
            value_decode=None,  # value decode function, if any
            offset=None         # Temp offset value
            ):
        
        self.reg_name = reg_name
        self.reg_address = reg_address
        self.reg_type = reg_type
        self.unit = unit
        self.value_decode = value_decode
        self.offset = offset

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

    def getOffset(self):
        return self.offset

