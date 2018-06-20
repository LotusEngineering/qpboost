# MIT License
#
# Copyright (c) 2018 Lotus Engineering, LLC
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import config
import unittest
from subprocess import Popen, CREATE_NEW_CONSOLE
from qspy import qspy, QS_CHANNEL, QS_OBJ_KIND, FILTER
import time
import struct


class test_qspy(unittest.TestCase):

    #@classmethod
    def _setUpClass(cls):
        # Start qspy
        cls.qspy_process = Popen(
            ['qspy', '-u', config.QSPY_TARGET_PORT], creationflags=CREATE_NEW_CONSOLE)

        # Start test_dpp if local
        if config.USE_LOCAL_DPP_TEST:
            cls.dpp_process = Popen(
                ['test_dpp', config.DPP_HOST_NAME], creationflags=CREATE_NEW_CONSOLE)
        else:
            cls.dpp_process = None


    #@classmethod
    def _tearDownClass(cls):
        if config.USE_LOCAL_DPP_TEST:
            cls.dpp_process.terminate()
            cls.dpp_process.wait()

        cls.qspy_process.terminate()
        cls.qspy_process.wait()

    def setUp(self):
        # Start qspy
        self.qspy_process = Popen(
            ['qspy', '-u', config.QSPY_TARGET_PORT], creationflags=CREATE_NEW_CONSOLE)
        
        time.sleep(1.0)

        # Start test_dpp if local
        if config.USE_LOCAL_DPP_TEST:
            self.dpp_process = Popen(
                ['test_dpp', config.DPP_HOST_NAME], creationflags=CREATE_NEW_CONSOLE)
            time.sleep(1.0) # Wait for applicaiton to start 
        else:
            self.dpp_process = None 

        # Create cut and attach test
        self.cut = qspy()
        self.cut.attach(self)

        # Need to reset embedded targets so that dictionary goes out
        if not config.USE_LOCAL_DPP_TEST:
            self.cut.sendReset()
            time.sleep(1)

        # DPP test starts with a pause so we must continue
        self.cut.sendContinue()
        time.sleep(1)  # Wait for dictionaries to come out

    def tearDown(self):
        self.cut.detach()
        time.sleep(1)
        self.cut = None

        self.qspy_process.terminate()
        self.qspy_process.wait() 
        
        if config.USE_LOCAL_DPP_TEST:
            self.dpp_process.terminate()
            self.dpp_process.wait()

    def OnPacket_ATTACH(self, packet):
        print("OnPacket_ATTACH callback:", packet)
    
    def OnRecord_QS_TARGET_INFO(self, packet):
        print("OnRecord_QS_TARGET_INFO callback:", packet)

    def OnRecord_QS_TEXT(self, packet):
        record, line = qspy.parse_QS_TEXT(packet)
        print("OnRecord_QS_TEXT record:{0}, line:{1}".format(record.name, line) )
    
    def OnRecord_QS_OBJ_DICT(self, data):
        print("OnRecord_QS_OBJ_DICT callback:", data)


    #@unittest.skip("")
    def test_sendCommand(self):
        self.cut.sendCommand(0) #pause
        self.cut.sendCommand(1) #resume

    @unittest.skip("")
    def test_sendLocalFilter(self):
        self.cut.sendLocalFilter(QS_OBJ_KIND.SM_AO, "l_philo<2>")

    @unittest.skip("")
    def test_sendCurrentObject(self):
        self.cut.sendCurrentObject(QS_OBJ_KIND.SM_AO, "l_philo<2>")

    def test_sendEvent(self):
        self.cut.sendGlobalFilters(FILTER.SM, FILTER.AO, FILTER.UA)        
        self.cut.sendCurrentObject(QS_OBJ_KIND.SM_AO, "l_philo<2>")
        #self.cut.sendLocalFilter(QS_OBJ_KIND.SM_AO, "l_philo<2>")
        
        #signal = 'EAT_SIG'
        #parameters = struct.pack('B', 2)
        #self.cut.sendEvent(ao_priority, signal, parameters)

        self.cut.sendEvent(ao_priority = 3, signal = "TIMEOUT_SIG")
        pass

        
if __name__ == "__main__":
    unittest.main(verbosity=2)
