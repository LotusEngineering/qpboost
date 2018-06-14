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

import unittest
from subprocess import Popen, CREATE_NEW_CONSOLE
from qspy import qspy, QS_CHANNEL, QS_OBJ_KIND, FILTER
import time
import qutest_config as CONFIG
from threading import Event
from queue import Queue



class qutest(unittest.TestCase):
 
    def __init__(self, methodName='runTest'):
        unittest.TestCase.__init__(self, methodName)
        self.qspy = None
        self.target_process = None
        self.attached_event = Event()
        self.have_target_event = Event()
        self.text_queue = Queue(maxsize = 0)

    @classmethod
    def setUpClass(cls):
        # Start qspy
        cls.qspy_process = Popen(
            ['qspy', '-u', CONFIG.QSPY_TARGET_PORT], creationflags=CREATE_NEW_CONSOLE)

        time.sleep(1.0) # qspy doesn't appear to have it's ears on immediately


    @classmethod
    def tearDownClass(cls):
        # Detach from qspy
        #??????????? cls.qspy.detach(self)

        cls.qspy_process.terminate()
        cls.qspy_process.wait()

    def setUp(self):
        super().setUp()

        # Create and attach to qspy backend 
        if self.qspy is None:
            self.qspy = qspy()
            self.attached_event.clear()
            self.qspy.attach(self)
            # Wait for attach
            self.assertTrue(self.attached_event.wait(CONFIG.TARGET_START_TIMEOUT_SEC))

        # Clear have target flag
        self.have_target_event.clear()

        # If running with a local target, kill and restart it
        if CONFIG.TARGET_EXECUTABLE is not None:
            
            # Stop existing target executable
            if self.target_process is not None:
                self.qspy.sendReset()
                self.target_process.terminate()
                self.target_process.wait()
                self.target_process = None

            # Start new target
            self.target_process = Popen(
                [CONFIG.TARGET_EXECUTABLE, CONFIG.TARGET_HOST_NAME], creationflags=CREATE_NEW_CONSOLE)
            time.sleep(1.0) # Wait for applicaiton to start 
        else: 
            self.qspy.sendReset()

        # Wait for target to be back up
        self.assertTrue(self.have_target_event.wait(CONFIG.TARGET_START_TIMEOUT_SEC))

        # Call on reset if defined
        if hasattr(self, "on_reset"):
            on_reset_method = getattr(self, 'on_reset')
            on_reset_method()

    def Continue(self):
        """ Sends a continue to a paused target """

        self.qspy.sendContinue()
        self.expect('           Trg-Ack  QS_RX_TEST_CONTINUE')

    def tearDown(self):
        super().tearDown()

    def expect(self, matchstring):
        next_packet = self.text_queue.get(timeout=CONFIG.EXPECT_TIMEOUT_SEC)
        record, line = qspy.parse_QS_TEXT(next_packet)
        self.assertRegex(line, matchstring)

    def expect_pause(self):
        self.expect('           TstPause')

    def glb_filter(self, *args):
        self.qspy.sendGlobalFilters(*args)
        self.expect('           Trg-Ack  QS_RX_GLB_FILTER')

    def current_obj(self, object_kind, object_id):
        self.qspy.sendCurrentObject(object_kind, object_id)
        self.expect('           Trg-Ack  QS_RX_CURR_OBJ')

    def post(self, signal, parameters = None):
        self.qspy.sendEvent(253,  signal, parameters)
        self.expect('           Trg-Ack  QS_RX_EVENT')

       

    ################### qspy backend callbacks #######################
    
    def OnRecord_QS_TARGET_INFO(self, record):
        self.have_target_event.set()

    def OnPacket_ATTACH(self, packet):
        self.attached_event.set()

    def OnRecord_QS_TEXT(self, record):
        # put packet in text queue
        self.text_queue.put(record)
        #print("OnRecord_QS_TEXT record:{0}, line:{1}".format(record.name, line) )


