#! /usr/bin/env python

import os, serial, rigol, time

def val2str(value):
    if isinstance(value, int):
        return "%d" % value
    elif isinstance(value, str):
        return "\"%s\"" % value
    else:
        print type(value)
        assert False

def testGeneralCommands(scope):

    print "General Commands (a.k.a. IEEE488.2 commands):"
    print

    identity = scope.getIdentity()
    print "    getIdentity() ................ : %s" % val2str(identity)

    scope.cmdReset()
    print "    cmdReset() ................... : %s" % "ok"

    print

def testAllGetterSetterValues(name, getter, setter, values):

    dots = "".join("." * (24 - len(name)))

    originalValue = getter()
    print "    get%s() %s : %s" % (name, dots, val2str(originalValue))

    progValues = values[:]
    if values[-1] != originalValue:
        progValues.append(originalValue)

    for progValue in progValues:
        setter(progValue)
        print "    set%s() %s : %s" % (name, dots, val2str(progValue))
        # Note: we need to wait for >= 55 ms before the setting takes effect!!!
        #time.sleep(0.020)
        checkValue = getter()
        print "    get%s() %s : %s" % (name, dots, val2str(checkValue))
        assert progValue == checkValue

def testAcquireCommands(scope):

    pass
    #testAllGetterSetterValues("AcquireType", scope.getAcquireType, scope.setAcquireType, ["NORMAL", "AVERAGE", ("PEAKDETECT", "Peak Detect")])
    #testAllGetterSetterValues("AcquireMode", scope.getDisplayGrid, scope.setDisplayGrid, ["FULL", "HALF", "NONE"])
    #testAllGetterSetterValues("AcquireAverages", scope.getDisplayPersist, scope.setDisplayPersist, ["ON", "OFF"])
    #testAllGetterSetterValues("AcquireSamplingRate", scope.getDisplayMenuDisplay, scope.setDisplayMenuDisplay, ["1s", "2s", "5s", "10s", "20s", "Infinite"])
    #testAllGetterSetterValues("AcquireMemDepth", scope.getDisplayMenuStatus, scope.setDisplayMenuStatus, ["ON", "OFF"])

def testDisplayCommands(scope):

    testAllGetterSetterValues("DisplayType", scope.getDisplayType, scope.setDisplayType, ["VECTORS", "DOTS"])
    testAllGetterSetterValues("DisplayGrid", scope.getDisplayGrid, scope.setDisplayGrid, ["FULL", "HALF", "NONE"])
    testAllGetterSetterValues("DisplayPersist", scope.getDisplayPersist, scope.setDisplayPersist, ["ON", "OFF"])
    testAllGetterSetterValues("DisplayMenuDisplay", scope.getDisplayMenuDisplay, scope.setDisplayMenuDisplay, ["1s", "2s", "5s", "10s", "20s", "Infinite"])
    testAllGetterSetterValues("DisplayMenuStatus", scope.getDisplayMenuStatus, scope.setDisplayMenuStatus, ["ON", "OFF"])

    scope.cmdDisplayClear()
    print "    cmdDisplayClear .............. : %s" % "ok"

    testAllGetterSetterValues("DisplayBrightness", scope.getDisplayBrightness, scope.setDisplayBrightness, range(0, 33))
    testAllGetterSetterValues("DisplayIntensity", scope.getDisplayIntensity, scope.setDisplayIntensity, range(0, 33))

def test(scope):

    print "========== Testing scope functionality =========="
    print

    testGeneralCommands(scope)
    time.sleep(0.200) # after the reset command
    #testSystemCommands(scope)
    #testAcquireCommands(scope)
    #testDisplayCommands(scope)
    #testTimebaseCommands(scope)
    #testTriggerCommands(scope)
    #testStorageCommands(scope)
    #testMathCommands(scope)
    #testChannelCommands(scope)
    #testMeasureAndCounterCommands(scope)
    #testWaveformCommand(scope)
    #testLogicalAnalyzerCommands(scope)
    #testKeyCommands(scope)
    #testOtherCommands(scope) # info, counter, beep
    for i in xrange(3):
        scope.cmdBeepAction()
        time.sleep(0.050)

def main():

    if True:
        device = serial.Serial("/dev/ttyUSB0", 9600, serial.EIGHTBITS, serial.PARITY_NONE, serial.STOPBITS_ONE, timeout = 5)
    else:
        device = os.fdopen(os.open("/dev/usbtmc0", os.O_RDWR), "rw")

    scope = rigol.RigolOscilloscope(device, verbosity = 0)

    test(scope)

    scope.close()

if __name__ == "__main__":
    main()
