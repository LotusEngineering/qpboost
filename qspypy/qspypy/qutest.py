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
import time
from threading import Event
from queue import Queue
from subprocess import Popen, CREATE_NEW_CONSOLE

from qspypy.qspy import qspy, QS_CHANNEL, QS_OBJ_KIND, FILTER, PRIO_COMMAND
import qspypy.config as CONFIG



@pytest.fixture(scope='session', autouse=True)
def qutest_session2():
    """ test fixture for a complete session (all test files)"""

    # Create the one and only qutest_context used through the session
    context = qutest_context()

    print("@@@@@@ context", context)

    # Do the context setup
    context.session_setup()

    # Yield context to subfixtures to pass along to tests
    yield context

    # Do the context teardown
    context.session_teardown()


@pytest.fixture()
def qutest(qutest_session):
    """ Default test fixture for each test function.
    
    This will reset the target before each test unless
    the RESET_TARGET_ON_SETUP is set to False
    """

    if CONFIG.RESET_TARGET_ON_SETUP:
        qutest_session.reset_target()

    return qutest_session

@pytest.fixture()
def qutest_noreset(qutest_session):
    """ Test fixture for each test function that does NOT reset the target. """

    return qutest_session

class qutest_context():
    """ This class provides the main pytest based context."""

 
    def __init__(self):
        self.qspy_process = None
        self.target_process = None
        self.attached_event = Event()
        self.have_target_event = Event()
        self.text_queue = Queue(maxsize = 0)


    def session_setup(self):
        """ Setup that should run on once per session. """

        # Automatically run qspy backend
        if CONFIG.AUTOSTART_QSPY:
            self.start_qspy()

        # Create qspy object and attach
        self.qspy = qspy()
        self.attached_event.clear()
        self.qspy.attach(self)
        # Wait for attach
        if not self.attached_event.wait(CONFIG.TARGET_START_TIMEOUT_SEC):
            __tracebackhide__ = True
            pytest.fail("Timeout waiting for Attach to QSpy (is QSpy running and QSPY_COM_PORT correct?)")


    def session_teardown(self):
        """ Teardown that runs at the end of a session. """

        self.qspy.detach()

        #if CONFIG.AUTOSTART_QSPY:
        #   self.stop_qspy()

        # Stop target executable
        if CONFIG.USE_LOCAL_TARGET:
            self.stop_target()

    def start_qspy(self):
        """ Helper to automatically start qspy. """

        # Local targets use tcp sockets
        if CONFIG.USE_LOCAL_TARGET:
            target_port = '-t'
        else:
            target_port = '-c' + CONFIG.QSPY_COM_PORT

        # Start qspy
        self.qspy_process = Popen(
            ['qspy', '-u', target_port], creationflags=CREATE_NEW_CONSOLE)

        time.sleep(1.0) # qspy doesn't appear to have it's ears on immediately


    def stop_qspy(self):
        """ Helper to stop qspy. """

        self.qspy_process.terminate()
        self.qspy_process.wait()
        self.qspy_process = None
    
    
    def start_target(self):
        """ Used to start a local target executable for dual targeting. """

        self.target_process = Popen(
            [CONFIG.LOCAL_TARGET_EXECUTABLE, CONFIG.LOCAL_TARGET_QSPY_HOST], creationflags=CREATE_NEW_CONSOLE)
        time.sleep(1.0)

    def stop_target(self):
        """ Stops local target. """

        self.target_process.terminate()
        self.target_process.wait()
        self.target_process = None

    def reset_target(self):
        """ Resets the target (local or remote). """

        # Clear have target flag
        self.have_target_event.clear()

        # Flush queue
        while not self.text_queue.empty():
            print("Flush:", self.text_queue.get())

        # If running with a local target, kill and restart it
        if CONFIG.USE_LOCAL_TARGET:        
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
        """ Sends a continue to a paused target. """

        self.qspy.sendContinue()
        self.expect('           Trg-Ack  QS_RX_TEST_CONTINUE')


    def expect_pause(self):
        """ Pause expectation. """

        self.expect('           TstPause')


    def glb_filter(self, *args):
        """ Sets the global filter.

        Args:
            args : One or more qspy.FILTER enumerations
        """
        self.qspy.sendGlobalFilters(*args)
        self.expect('           Trg-Ack  QS_RX_GLB_FILTER')


    def loc_filter(self, object_kind, object_id):
        """ Sets a local filter.

        Args:
          object_kind : kind of object from qspy.QS_OBJ_KIND
          object_id : the object which can be an address integer or a dictionary name string
        """

        self.qspy.sendLocalFilter(object_kind, object_id)
        self.expect('           Trg-Ack  QS_RX_LOC_FILTER')


    def current_obj(self, object_kind, object_id):
        """ Sets the current object in qspy.

        Arguments:
        object_kind : kind of object from qspy.QS_OBJ_KIND
        object_id : the object which can be an address integer or a dictionary name string
        """

        self.qspy.sendCurrentObject(object_kind, object_id)
        self.expect('           Trg-Ack  QS_RX_CURR_OBJ')


    def post(self, signal, parameters = None):
        """ Posts an event to the object selected with current_obj().

        Args:
          signal : signal string or number
          parameters : optional event payload defined using struct.pack
        """

        self.qspy.sendEvent(PRIO_COMMAND.POST.value,  signal, parameters)
        self.expect('           Trg-Ack  QS_RX_EVENT')


    def publish(self, signal, parameters = None):
        """ Publishes an event in the system.

        Args:
          signal : signal string or number
          parameters : optional event payload defined using struct.pack
        """

        self.qspy.sendEvent(PRIO_COMMAND.PUBLISH,  signal, parameters)
        self.expect('           Trg-Ack  QS_RX_EVENT')


    def dispatch(self, signal, parameters = None):
        """ Dispatches an event to the object selected with current_obj().

        Args:
          signal : signal string or number
          parameters : optional event payload defined using struct.pack
        """

        self.qspy.sendEvent(PRIO_COMMAND.DISPATCH.value,  signal, parameters)
        self.expect('           Trg-Ack  QS_RX_EVENT')


    def probe(self, function, data_word):
        """ Sends a test probe to the target.

        The Target collects these Test-Probe preserving the order in which they were sent.
        Subsequently, whenever a given API is called inside the Target, it can
        obtain the Test-Probe by means of the QS_TEST_PROBE_DEF() macro.
        The QS_TEST_PROBE_DEF() macro returns the Test-Probes in the same
        order as they were received to the Target. If there are no more Test-
        Probes for a given API, the Test-Probe is initialized to zero.

        Args:
          function : string function name or integer raw address
          data_word : a single uint 32 for the probe   
        """

        self.qspy.sendTestProbe(function, data_word)
        self.expect('           Trg-Ack  QS_RX_TEST_PROBE')


    def tick(self, rate = 0):
        """ Triggers a system clock tick.

        Args:
          rate : (optional) which clock rate to tick
        """

        self.qspy.sendTick(rate)
        self.expect('           Trg-Ack  QS_RX_TICK')


    def command(self, command_id, param1 = 0, param2 = 0, param3 = 0):
        """ Sends a qspy command to the target.

        Args:
          command_id : string command name or number
          param1 : (optional) integer argument
          param2 : (optional) integer argument
          param3 : (optional) integer argument
        """

        self.qspy.sendCommand(command_id, param1, param2, param3)
        self.expect('           Trg-Ack  QS_RX_COMMAND')


    def expect(self, match):
        """ asserts that match string is sent by the cut

        If no string is returned in EXPECT_TIMEOUT_SEC the test will fail

        Args:
          match : is either an entire string or one prepended with 
                  %timestamp to ignore timestamp and/or 
                  postpended with * to ignore ending
        """



        try:
            next_packet = self.text_queue.get(timeout=CONFIG.EXPECT_TIMEOUT_SEC)
        except:
            __tracebackhide__ = True
            pytest.fail('Expect Timeout for match:"{0}"'.format(match))
            #assert False, 'Expect Timeout for match:"{0}"'.format(match)

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
        #assert expected == actual, 'Expect Match Failed! \nExpected:\"{0}\"\nReceived:\"{1}\"'.format(expected, actual)
        if expected != actual:
            __tracebackhide__ = True
            pytest.fail('Expect Match Failed! \nExpected:\"{0}\"\nReceived:\"{1}\"'.format(expected, actual))
    
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




