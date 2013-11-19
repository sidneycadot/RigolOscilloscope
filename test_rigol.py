#! /usr/bin/env python

import os, serial, rigol, time

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

def testAllGetterSetterValues(name, getter, setter, values):

    dots = "".join("." * (37 - len(name)))

    originalValue = getter()
    print "    get%s %s : %s" % (name, dots, val2str(originalValue))

    if setter is not None:

        progValues = values[:]
        if values[-1] != originalValue:
            progValues.append(originalValue)

        for progValue in progValues:
            setter(progValue)
            print "    set%s %s : %s" % (name, dots, val2str(progValue))
            # Note: we need to wait for >= 55 ms before the setting takes effect!!!
            #time.sleep(0.020)
            checkValue = getter()
            print "    get%s %s : %s" % (name, dots, val2str(checkValue))
            assert progValue == checkValue

def testGeneralCommands(scope):

    print "General Commands (a.k.a. IEEE488.2 commands):"
    print

    identity = scope.getIdentity()

    print "    getIdentity() ........................... : %s" % val2str(identity)

    scope.cmdReset()

    print "    cmdReset() .............................. : %s" % "ok"
    print

def testSystemCommands(scope):

    print "SYSTEM commands:"
    print

    scope.cmdSystemRun()
    time.sleep(0.200)

    print "    cmdSystemRun() .......................... : %s" % "ok"

    scope.cmdSystemStop()
    time.sleep(0.200)

    print "    cmdSystemStop() ......................... : %s" % "ok"

    scope.cmdSystemAuto()
    time.sleep(0.200)

    print "    cmdSystemAuto() ......................... : %s" % "ok"

    scope.cmdSystemHardcopy()
    time.sleep(0.200)

    print "    cmdSystemHardcopy() ..................... : %s" % "ok"

    scope.cmdSystemRun()
    time.sleep(0.200)

    print "    cmdSystemRun() .......................... : %s" % "ok"

    print

def testAcquireCommands(scope):

    print "ACQUIRE commands:"
    print

    testAllGetterSetterValues("AcquireType()", scope.getAcquireType, scope.setAcquireType, ["NORMAL", "AVERAGE", "PEAKDETECT"])
    testAllGetterSetterValues("AcquireMode()", scope.getAcquireMode, scope.setAcquireMode, ["REAL_TIME", "EQUAL_TIME"])
    testAllGetterSetterValues("AcquireAverages()", scope.getAcquireAverages, scope.setAcquireAverages, [2, 4, 8, 16, 32, 64, 128, 256])
    testAllGetterSetterValues("AcquireSamplingRate(\"CHANNEL1\")", lambda : scope.getAcquireSamplingRate("CHANNEL1"), None, None)
    testAllGetterSetterValues("AcquireSamplingRate(\"CHANNEL2\")", lambda : scope.getAcquireSamplingRate("CHANNEL2"), None, None)
    testAllGetterSetterValues("AcquireSamplingRate(\"DIGITAL\")", lambda : scope.getAcquireSamplingRate("DIGITAL"), None, None)
    testAllGetterSetterValues("AcquireMemDepth()", scope.getAcquireMemDepth, scope.setAcquireMemDepth, ["LONG", "NORMAL"])

    print

def testDisplayCommands(scope):

    print "DISPLAY commands:"
    print

    testAllGetterSetterValues("DisplayType()", scope.getDisplayType, scope.setDisplayType, ["VECTORS", "DOTS"])
    testAllGetterSetterValues("DisplayGrid()", scope.getDisplayGrid, scope.setDisplayGrid, ["FULL", "HALF", "NONE"])
    testAllGetterSetterValues("DisplayPersist()", scope.getDisplayPersist, scope.setDisplayPersist, ["ON", "OFF"])
    testAllGetterSetterValues("DisplayMenuDisplay()", scope.getDisplayMenuDisplay, scope.setDisplayMenuDisplay, ["1s", "2s", "5s", "10s", "20s", "Infinite"])
    testAllGetterSetterValues("DisplayMenuStatus()", scope.getDisplayMenuStatus, scope.setDisplayMenuStatus, ["ON", "OFF"])

    scope.cmdDisplayClear()

    print "    cmdDisplayClear ......................... : %s" % "ok"

    testAllGetterSetterValues("DisplayBrightness", scope.getDisplayBrightness, scope.setDisplayBrightness, range(0, 33))
    testAllGetterSetterValues("DisplayIntensity", scope.getDisplayIntensity, scope.setDisplayIntensity, range(0, 33))

    print

def testTimebaseCommands(scope):

    print "TIMEBASE commands:"
    print

    testAllGetterSetterValues("TimebaseMode()", scope.getTimebaseMode, scope.setTimebaseMode, ["MAIN", "DELAYED"])
    testAllGetterSetterValues("TimebaseFormat()", scope.getTimebaseFormat, scope.setTimebaseFormat, ["XY", "YT", "SCANNING"])

    print

def test(scope):

    print "========== Testing scope functionality =========="
    print

    testGeneralCommands(scope)
    #testSystemCommands(scope)
    #testAcquireCommands(scope)
    #testDisplayCommands(scope)
    testTimebaseCommands(scope)
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
