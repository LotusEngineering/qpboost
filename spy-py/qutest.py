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

import pytest
from subprocess import Popen, CREATE_NEW_CONSOLE
from qspy import qspy, QS_CHANNEL, QS_OBJ_KIND, FILTER, PRIO_COMMAND
import time
import qutest_config as CONFIG
from threading import Event
from queue import Queue



@pytest.fixture(scope='session')
def qutest_session():
    """ test fixture for a complete session (all test files)"""

    context = qutest_context()
    context.session_setup()

    # Return context to subfixtures to pass along to tests
    yield context

    # Clean up
    context.session_teardown()

@pytest.fixture()
def qutest(qutest_session):
    """ test fixture for each test function, does a target reset by default """

    qutest_session.reset_target()

    return qutest_session

@pytest.fixture()
def qutest_noreset(qutest_session):
    """ test fixture for each test function that does NOT reset the target """

    return qutest_session

class qutest_context():
 
    def __init__(self):
        self.qspy_process = None
        self.target_process = None
        self.attached_event = Event()
        self.have_target_event = Event()
        self.text_queue = Queue(maxsize = 0)


    def session_setup(self):
        # Automatically run qspy backend
        if CONFIG.AUTOSTART_QSPY_HOST:
            self.start_qspy()

        # Create qspy object and attach
        self.qspy = qspy()
        self.attached_event.clear()
        self.qspy.attach(self)
        # Wait for attach
        assert self.attached_event.wait(CONFIG.TARGET_START_TIMEOUT_SEC), "Timeout waiting for Attach to QSpy (is QSpy running?)"


    def session_teardown(self):
        self.qspy.detach()

        if CONFIG.AUTOSTART_QSPY_HOST:
            self.stop_qspy()

        # Stop target executable
        if CONFIG.USE_HOST_TARGET:
            self.stop_target()

    def start_qspy(self):
        # Start qspy
        self.qspy_process = Popen(
            ['qspy', '-u', CONFIG.QSPY_TARGET_PORT], creationflags=CREATE_NEW_CONSOLE)

        time.sleep(1.0) # qspy doesn't appear to have it's ears on immediately


    def stop_qspy(self):
        self.qspy_process.terminate()
        self.qspy_process.wait()
        self.qspy_process = None
    
    
    def start_target(self):
        self.target_process = Popen(
            [CONFIG.TARGET_EXECUTABLE, CONFIG.TARGET_HOST_NAME], creationflags=CREATE_NEW_CONSOLE)
        time.sleep(1.0)

    def stop_target(self):
        self.target_process.terminate()
        self.target_process.wait()
        self.target_process = None

    def reset_target(self):

        # Clear have target flag
        self.have_target_event.clear()

        # If running with a local target, kill and restart it
        if CONFIG.USE_HOST_TARGET:        
            if self.target_process is not None:
                self.qspy.sendReset()
                # Let the target executable finish
                time.sleep(CONFIG.TARGET_START_TIMEOUT_SEC)
                self.stop_target()
            self.start_target()
        else: 
            self.qspy.sendReset()

        # Wait for target to be back up
        assert self.have_target_event.wait(CONFIG.TARGET_START_TIMEOUT_SEC), "Timeout waiting for target to reset"

        # Call on_reset if defined
        if hasattr(self, "on_reset"):
            on_reset_method = getattr(self, 'on_reset')
            on_reset_method(self)

    def Continue(self):
        """ Sends a continue to a paused target """

        self.qspy.sendContinue()
        self.expect('           Trg-Ack  QS_RX_TEST_CONTINUE')


    def expect_pause(self):
        self.expect('           TstPause')


    def glb_filter(self, *args):
        self.qspy.sendGlobalFilters(*args)
        self.expect('           Trg-Ack  QS_RX_GLB_FILTER')


    def loc_filter(self, object_kind, object_id):
        """ Sets a local filter

        Arguments:
        object_kind -- kind of object from QS_OBJ_KIND
        object_id -- the object which can be an address integer or a dictionary name string
        """

        self.qspy.sendLocalFilter(object_kind, object_id)
        self.expect('           Trg-Ack  QS_RX_LOC_FILTER')


    def current_obj(self, object_kind, object_id):
        self.qspy.sendCurrentObject(object_kind, object_id)
        self.expect('           Trg-Ack  QS_RX_CURR_OBJ')


    def post(self, signal, parameters = None):
        self.qspy.sendEvent(PRIO_COMMAND.POST.value,  signal, parameters)
        self.expect('           Trg-Ack  QS_RX_EVENT')


    def publish(self, signal, parameters = None):
        self.qspy.sendEvent(PRIO_COMMAND.PUBLISH,  signal, parameters)
        self.expect('           Trg-Ack  QS_RX_EVENT')


    def dispatch(self, signal, parameters = None):
        self.qspy.sendEvent(PRIO_COMMAND.DISPATCH.value,  signal, parameters)
        self.expect('           Trg-Ack  QS_RX_EVENT')


    def probe(self, function, data):
        self.qspy.sendTestProbe(function, data)
        self.expect('           Trg-Ack  QS_RX_TEST_PROBE')


    def tick(self, rate = 0):
        self.qspy.sendTick(rate)
        self.expect('           Trg-Ack  QS_RX_TICK')


    def command(self, command_id, param1 = 0, param2 = 0, param3 = 0):
        self.qspy.sendCommand(command_id, param1, param2, param3)
        self.expect('           Trg-Ack  QS_RX_COMMAND')


    def expect(self, match):

        try:
            next_packet = self.text_queue.get(timeout=CONFIG.EXPECT_TIMEOUT_SEC)
        except:
            assert False, 'Expect Timeout for match:"{0}"'.format(match)

        _, line = qspy.parse_QS_TEXT(next_packet)

        magic_string = '%timestamp'
        
        if match.startswith(magic_string):
            line_start = len(magic_string) 
        else:
            line_start = 0

        if match.endswith('*'):
            line_end = match.find('*', line_start)
            match = match.rstrip('*')
        else:
            line_end = len(match)

        expected = match[line_start:] 
        actual = line[line_start:line_end]
        assert expected == actual, 'Expect Match Failed! \nExpected:\"{0}\"\nReceived:\"{1}\"'.format(expected, actual)


    ################### qspy backend callbacks #######################
    
    def OnRecord_QS_TARGET_INFO(self, packet):
        self.have_target_event.set()

    def OnPacket_ATTACH(self, packet):
        self.attached_event.set()

    def OnRecord_QS_TEXT(self, record):
        # put packet in text queue
        self.text_queue.put(record)
        #recordId, line = self.qspy.parse_QS_TEXT(record)
        #print('OnRecord_QS_TEXT record:{0}, line:"{1}"'.format(recordId.name, line) )




