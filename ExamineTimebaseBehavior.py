#! /usr/bin/env python

import os, serial, rigol, time, random

def val2str(value):
    if isinstance(value, int):
        return "%d" % value
    elif isinstance(value, float):
        return "%f" % value
    elif isinstance(value, str):
        return "\"%s\"" % value
    else:
        print type(value)
        assert False

def main():

    if True:
        device = serial.Serial("/dev/ttyUSB0", 9600, serial.EIGHTBITS, serial.PARITY_NONE, serial.STOPBITS_ONE, timeout = 5)
    else:
        device = os.fdopen(os.open("/dev/usbtmc0", os.O_RDWR), "rw")

    scope = rigol.RigolOscilloscope(device, verbosity = 1)

    scope.setTimebaseMode("MAIN")
    scope.setTimebaseFormat("YT")

    for i in xrange(20):

        print "=============="

        #identity = scope.getIdentity()
        #assert identity.startswith("Rigol")
        #time.sleep(0.500)

        scale_value = random.uniform(1, 1)
        offset_value = random.uniform(0.1, 0.1)

        #scope.setTimebaseScale(1.0, delayed = False)
        scope.setTimebaseOffset(i / 1000.0, delayed = False)

        scale_readback = scope.getTimebaseScale(delayed = False)
        offset_readback = scope.getTimebaseOffset(delayed = False)

        #print "%20.9f %20.9f %20.9f %20.9f" % (scale_value, offset_value, scale_readback, offset_readback)

        time.sleep(0.100)

    #off1 = 0.217
    #scope.setTimebaseOffset(off1, delayed = False)

    #off2 = scope.getTimebaseOffset(delayed = False)
    #print off1, off2


    scope.close()

if __name__ == "__main__":
    main()
