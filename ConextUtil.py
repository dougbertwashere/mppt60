

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

