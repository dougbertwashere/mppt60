#!/usr/bin/env python 

from mppt60 import getInfoFromCC

InsightLocalHost = "insightlocal.lan"       #  Hostname or IP of Conext InsightLocal Gateway - modify/specify for other than default
mppt_id = [ 30, 31, 32, 33 ]                # Modbus IDs of the Conext CCsa


debug = False


#
# Main entry point
#
def main():

    global mppt_id 
    global debug 

    mppts = {}

    # gather info from each of the MMPTs
    for id in mppt_id:

        reg_dict = getInfoFromCC(id, InsightLocalHost, debug)

        print("MPPT %s" % id)

        for reg in reg_dict:
            strHex = "0x%0.4X" % reg_dict[reg]["reg_address"]

            decoded = reg_dict[reg]["valueDecoded"]
            if decoded != "":
                decoded = "[Decode: %s]" % decoded
            
            value = reg_dict[reg]["value"]
            unit = reg_dict[reg]["unit"]
            offset = reg_dict[reg]["offset"]

            if offset != None:
                value = (value / 1000) + offset
            
            print("    %s Name: '%35s' --->   Value: '%s' (%s)  %s" % (strHex, reg, value, unit, decoded))

        mppts[id] = reg_dict

    return 0

if __name__ == "__main__":
    main()
