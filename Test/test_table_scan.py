"""Unit test of the TableScan

   @author: Kay Kasemir
"""
import unittest
from scan.commands import Set
from scan.table import TableScan
from scan.util import ScanSettings

class MyScanSettings(ScanSettings):
    def __init__(self):
        super(MyScanSettings, self).__init__()
        # Define special settings for some devices
        self.defineDeviceClass("Motor.*", completion=True, readback=True, timeout=100)
        self.defineDeviceClass("InfiniteCounter", comparison="to increase by")
        
    def getReadbackName(self, device_name):
        # Motors use their *.RBV field for readback
        if "Motor" in device_name:
            return device_name + ".RBV"
        return device_name

# TODO Check the generated scan once the string representation of commands is fixed
# TODO 'Comment' column can be comment command or Set('SomeCommentPV')
# TODO Fix Log command
# TODO Devices to always log
# TODO Start by waiting for all motors to be idle
#         for motor in motors:
#             idle = self.settings.getMotorIdlePV(motor)
#             if idle:
#                 commands.insert(0, WaitCommand(idle, Comparison.EQUALS, 1, 0.1, 5.0))

settings = MyScanSettings()

def handle(table):
    print table
    cmds = table.createScan()
    print
    for cmd in cmds:
        print str(cmd)
    return cmds


class TableScanTest(unittest.TestCase):
    def testBasics(self):
        print "\n=== Basic Table ==="
        table_scan = TableScan(settings,
          (   "Comment", "X ",  "Y", "Speed", "Wavelength" ),
          [
            [ "Setup",  "  1",  "2",    "30",           "" ],
            [ "Count",     "",   "",      "",        "100" ],
            [ "Wait",      "",   "",      "",        "200" ],
          ]
        )
        cmds = handle(table_scan)
        self.assertEqual(str(cmds), "[Comment('Setup'), Set('X', 1.0), Set('Y', 2.0), Set('Speed', 30.0), Comment('Count'), Set('Wavelength', 100.0), Comment('Wait'), Set('Wavelength', 200.0)]")

        print "\n=== Wait for time ==="
        table_scan = TableScan(settings,
          (   "X",  "Y", "Wait For", "Value" ),
          [
            [ "1",  "2", "seconds", "10" ],
            [ "3",  "4", "seconds", "20" ],
          ]
        )
        cmds = handle(table_scan)
        self.assertEqual(str(cmds), "[Set('X', 1.0), Set('Y', 2.0), Delay(10), Log('X', 'Y'), Set('X', 3.0), Set('Y', 4.0), Delay(20), Log('X', 'Y')]")


        print "\n=== Wait for PV ==="
        table_scan = TableScan(settings,
          (   "X",  "Y", "Wait For", "Value" ),
          [
            [ "1",  "2", "Counter1", "10" ],
            [ "3",  "4", "Counter1", "20" ],
          ]
        )
        cmds = handle(table_scan)
        #self.assertEqual(str(cmds), "")


        print "\n=== Wait for PV using 'increment' ==="
        table_scan = TableScan(settings,
          (   "X",  "Y", "Wait For",        "Value" ),
          [
            [ "1",  "2", "Counter1",        "10" ],
            [ "3",  "4", "InfiniteCounter", "20" ],
          ]
        )
        cmds = handle(table_scan)
        #self.assertEqual(str(cmds), "")


        print "\n=== Wait for PV or Max Time ==="
        table_scan = TableScan(settings,
          (   "X",  "Y", "Wait For", "Value", "Or Time" ),
          [
            [ "1",  "2", "Counter1", "10",    "500" ],
            [ "3",  "4", "Counter1", "20",    "" ],
          ]
        )
        cmds = handle(table_scan)
        #self.assertEqual(str(cmds), "")


    def testStartStop(self):
        print "\n=== Start/stop at each step ==="
        table_scan = TableScan(settings,
          (   "X",  "Y", "Wait For", "Value" ),
          [
            [ "1",  "2", "counter", "10" ],
            [ "3",  "4", "counter", "10" ],
          ],
          pre = Set('shutter', 1),
          post = Set('shutter', 0),
          start = [ Set('counter:reset', 1, completion=True),
                    Set('counter:enable', 1, completion=True),
                    Set('daq:enable', 1, completion=True)
                  ],
          stop  = [ Set('daq:enable', 0, completion=True),
                    Set('counter:enable', 0, completion=True)
                  ],
        )
        cmds = handle(table_scan)
        self.assertEqual(str(cmds), "[Set('shutter', 1), Set('X', 1.0), Set('Y', 2.0), Set('counter:reset', 1, completion=true), Set('counter:enable', 1, completion=true), Set('daq:enable', 1, completion=true), Wait('counter', 10.0, comparison='>='), Log('X', 'Y', 'counter'), Set('daq:enable', 0, completion=true), Set('counter:enable', 0, completion=true), Set('X', 3.0), Set('Y', 4.0), Set('counter:reset', 1, completion=true), Set('counter:enable', 1, completion=true), Set('daq:enable', 1, completion=true), Wait('counter', 10.0, comparison='>='), Log('X', 'Y', 'counter'), Set('daq:enable', 0, completion=true), Set('counter:enable', 0, completion=true), Set('shutter', 0)]")


    def testScanSettings(self):
        print "\n=== ScanSettings configure Motor for completion and RBV ==="
        table_scan = TableScan(settings,
          (   "X ",  "Motor1" ),
          [
            [ "  1",  "2" ],
          ]
        )
        cmds = handle(table_scan)
        self.assertEqual(str(cmds), "[Set('X', 1.0), Set('Motor1', 2.0, completion=true, readback='Motor1.RBV', timeOut=100)]")


        print "\n=== Override ScanSettings for Motor ==="
        table_scan = TableScan(settings,
          (   "Motor1",  "-cr Motor2" ),
          [
            [ "  1",  "2" ],
          ]
        )
        cmds = handle(table_scan)
        self.assertEqual(str(cmds), "[Set('Motor1', 1.0, completion=true, readback='Motor1.RBV', timeOut=100), Set('Motor2', 2.0)]")


    def testParallel(self):
        print "\n=== Parallel without Wait ==="
        table_scan = TableScan(settings,
          (   "X", "+p Y", "+p Z" ),
          [
            [ "1", "2",    "3" ],
          ]
        )
        cmds = handle(table_scan)
        self.assertEqual(str(cmds), "[Set('X', 1.0), Parallel(Set('Y', 2.0), Set('Z', 3.0))]")

        print "\n=== Parallel with Wait ==="
        table_scan = TableScan(settings,
          (   "X", "+p Y", "+p Z", "Wait For", "Value" ),
          [
            [ "1", "2",    "3",    "Seconds",  "10" ],
            [ "4", "5",    "6",    "completion", "" ],
          ]
        )
        cmds = handle(table_scan)
        # self.assertEqual(str(cmds), "")


    def testRange(self):
        print "\n=== Range Cells ==="
        table_scan = TableScan(settings,
          (   " X ",  "Y", ),
          [
            [ "  1",  "", ],
            [ "   ",  "range(5)", ],
            [ "[ 0, 1]", "range(2)", ],
          ]
        )
        cmds = handle(table_scan)
        self.assertEqual(str(cmds), "[Set('X', 1.0), Set('Y', 0.0), Set('Y', 1.0), Set('Y', 2.0), Set('Y', 3.0), Set('Y', 4.0), Set('X', 0.0), Set('Y', 0.0), Set('X', 0.0), Set('Y', 1.0), Set('X', 1.0), Set('Y', 0.0), Set('X', 1.0), Set('Y', 1.0)]")



if __name__ == "__main__":
    unittest.main()