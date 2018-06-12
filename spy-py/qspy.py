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

from enum import IntFlag, IntEnum
import socket
import struct
import time
import threading


# Enumeration for packet IDs that are interpreted by QSPY
class QSPY(IntEnum):
    ATTACH = 128,
    DETACH = 129,
    SAVE_DICT = 130,
    SCREEN_OUT = 131,
    BIN_OUT = 132,
    MATLAB_OUT = 133,
    MSCGEN_OUT = 134,
    SEND_EVENT = 135,
    SEND_LOC_FILTER = 136,
    SEND_CURR_OBJ = 137,
    SEND_COMMAND = 138,
    SEND_TEST_PROBE = 139


# Enumeration for packet IDs that are sent directly to the target
class QS_RX(IntEnum):
    INFO = 0
    COMMAND = 1
    RESET = 2
    TICK = 3
    PEEK = 4
    POKE = 5
    FILL = 6
    TEST_SETUP = 7
    TEST_TEARDOWN = 8
    TEST_PROBE = 9
    GLB_FILTER = 10
    LOC_FILTER = 11
    AO_FILTER = 12
    CURR_OBJ = 13
    CONTINUE = 14
    RESERVED1 = 15
    EVENT = 16

# Records from client Must be kept in sync with qs_copy.h
class QSpyRecords(IntEnum): 
    #/* [0] QS session (not maskable) */
    QS_TEXT = 0,              #QS_EMPTY = 0,             #/*!< QS record for cleanly starting a session */

    #/* [1] SM records */
    QS_QEP_STATE_ENTRY = 1,   #/*!< a state was entered */
    QS_QEP_STATE_EXIT = 2,    #/*!< a state was exited */
    QS_QEP_STATE_INIT = 3,    #/*!< an initial transition was taken in a state */
    QS_QEP_INIT_TRAN = 4,     #/*!< the top-most initial transition was taken */
    QS_QEP_INTERN_TRAN = 5,   #/*!< an internal transition was taken */
    QS_QEP_TRAN = 6,          #/*!< a regular transition was taken */
    QS_QEP_IGNORED = 7,       #/*!< an event was ignored (silently discarded) */
    QS_QEP_DISPATCH = 8,      #/*!< an event was dispatched (begin of RTC step) */
    QS_QEP_UNHANDLED = 9,     #/*!< an event was unhandled due to a guard */

    #/* [10] AO records */
    QS_QF_ACTIVE_DEFER = 10,   #/*!< AO deferred an event */
    QS_QF_ACTIVE_RECALL = 11,  #/*!< AO recalled an event */
    QS_QF_ACTIVE_SUBSCRIBE = 12, #/*!< an AO subscribed to an event */
    QS_QF_ACTIVE_UNSUBSCRIBE = 13, #/*!< an AO unsubscribed to an event */
    QS_QF_ACTIVE_POST_FIFO = 14, #/*!< an event was posted (FIFO) directly to AO */
    QS_QF_ACTIVE_POST_LIFO = 15, #/*!< an event was posted (LIFO) directly to AO */
    QS_QF_ACTIVE_GET = 16,     #/*!< AO got an event and its queue is not empty */
    QS_QF_ACTIVE_GET_LAST = 17,#/*!< AO got an event and its queue is empty */
    QS_QF_ACTIVE_RECALL_ATTEMPT = 18, #/*!< AO attempted to recall an event */

    #/* [19] EQ records */
    QS_QF_EQUEUE_POST_FIFO = 19, #/*!< an event was posted (FIFO) to a raw queue */
    QS_QF_EQUEUE_POST_LIFO = 20, #/*!< an event was posted (LIFO) to a raw queue */
    QS_QF_EQUEUE_GET = 21,     #/*!< get an event and queue still not empty */
    QS_QF_EQUEUE_GET_LAST = 22,#/*!< get the last event from the queue */

    QS_QF_RESERVED2 = 23,

    #/* [24] MP records */
    QS_QF_MPOOL_GET = 24,      #/*!< a memory block was removed from memory pool */
    QS_QF_MPOOL_PUT = 25,      #/*!< a memory block was returned to memory pool */

    #/* [26] QF records */
    QS_QF_PUBLISH = 26,        #/*!< an event was published */
    QS_QF_NEW_REF = 27,        #/*!< new event reference was created */
    QS_QF_NEW = 28,            #/*!< new event was created */
    QS_QF_GC_ATTEMPT = 29,     #/*!< garbage collection attempt */
    QS_QF_GC = 30,             #/*!< garbage collection */
    QS_QF_TICK = 31,           #/*!< QF_tickX() was called */

    #/* [32] TE records */
    QS_QF_TIMEEVT_ARM = 32,    #/*!< a time event was armed */
    QS_QF_TIMEEVT_AUTO_DISARM = 33, #/*!< a time event expired and was disarmed */
    QS_QF_TIMEEVT_DISARM_ATTEMPT = 34,#/*!< attempt to disarm a disarmed QTimeEvt */
    QS_QF_TIMEEVT_DISARM = 35, #/*!< true disarming of an armed time event */
    QS_QF_TIMEEVT_REARM = 36,  #/*!< rearming of a time event */
    QS_QF_TIMEEVT_POST = 37,   #/*!< a time event posted itself directly to an AO */

    #/* [38] QF records */
    QS_QF_DELETE_REF = 38,     #/*!< an event reference is about to be deleted */
    QS_QF_CRIT_ENTRY = 39,     #/*!< critical section was entered */
    QS_QF_CRIT_EXIT = 40,      #/*!< critical section was exited */
    QS_QF_ISR_ENTRY = 41,      #/*!< an ISR was entered */
    QS_QF_ISR_EXIT = 42,       #/*!< an ISR was exited */
    QS_QF_INT_DISABLE = 43,    #/*!< interrupts were disabled */
    QS_QF_INT_ENABLE = 44,     #/*!< interrupts were enabled */

    #/* [45] AO records */
    QS_QF_ACTIVE_POST_ATTEMPT = 45,#/*!< attempt to post an evt to AO failed */

    #/* [46] EQ records */
    QS_QF_EQUEUE_POST_ATTEMPT = 46,#/*!< attempt to post an evt to QEQueue failed */

    #/* [47] MP records */
    QS_QF_MPOOL_GET_ATTEMPT = 47,  #/*!< attempt to get a memory block failed */

    #/* [48] SC records */
    QS_MUTEX_LOCK = 48,        #/*!< a mutex was locked */
    QS_MUTEX_UNLOCK = 49,      #/*!< a mutex was unlocked */
    QS_SCHED_LOCK = 50,        #/*!< scheduler was locked */
    QS_SCHED_UNLOCK = 51,      #/*!< scheduler was unlocked */
    QS_SCHED_NEXT = 52,        #/*!< scheduler found next task to execute */
    QS_SCHED_IDLE = 53,        #/*!< scheduler became idle */
    QS_SCHED_RESUME = 54,      #/*!< scheduler resumed previous task (not idle) */

    #/* [55] QEP records */
    QS_QEP_TRAN_HIST = 55,     #/*!< a tran to history was taken */
    QS_QEP_TRAN_EP = 56,       #/*!< a tran to entry point into a submachine */
    QS_QEP_TRAN_XP = 57,       #/*!< a tran to exit  point out of a submachine */

    #/* [58] Miscellaneous QS records (not maskable) */
    QS_TEST_PAUSED = 58,       #/*!< test has been paused */
    QS_TEST_PROBE_GET = 59,    #/*!< reports that Test-Probe has been used */
    QS_SIG_DICT = 60,          #/*!< signal dictionary entry */
    QS_OBJ_DICT = 61,          #/*!< object dictionary entry */
    QS_FUN_DICT = 62,          #/*!< function dictionary entry */
    QS_USR_DICT = 63,          #/*!< user QS record dictionary entry */
    QS_TARGET_INFO = 64,       #/*!< reports the Target information */
    QS_TARGET_DONE = 65,       #/*!< reports completion of a user callback */
    QS_RX_STATUS = 66,         #/*!< reports QS data receive status */
    QS_MSC_RESERVED1 = 67,
    QS_PEEK_DATA = 68,         #/*!< reports the data from the PEEK query */
    QS_ASSERT_FAIL = 69,       #/*!< assertion failed in the code */

    #/* [70] Application-specific (User) QS records */
    QS_USER = 70              #/*!< the first record available to QS users */


# Enumeration for channel type, this must match enum in "be.c"
class QS_CHANNEL(IntFlag):
    BINARY = 1,
    TEXT = 2


class QS_OBJ_KIND(IntEnum):
    SM = 0, #State Machine
    AO = 1, #Active Object
    MP = 2, #Memory Pool
    EQ = 3, #Event Queue
    TE = 4, #Time Event 
    AP = 5, #Application-Specific 
    SM_AO = 6 #Active object and state machine


# Port specific formats used in struct.pack
theFmt = {
    'objPtr': 'I',
    'funPtr': 'I',
    'tstamp': 'I',
    'sig': 'h',
    'evtSize': 'h',
    'queueCtr': 'B',
    'poolCtr': 'h',
    'poolBlk': 'h',
    'tevtCtr': 'h'
    }

class qspy(threading.Thread):

    def __init__(self):
        super().__init__()
        self.tx_packet_sequence = 0
        self.socket = None
        self.alive = threading.Event()
        self.alive.set()

    def __del__(self):
        if self.socket is not None:
            self.socket.close

    # Socket receive thread
    def run(self):
        while self.alive.isSet():
            try:
                data = self.socket.recv(1024)
               # print( "{0}({1})".format(data, data.hex()) )

                sequence = data[0]
                recordID = data[1]
                if recordID < 128:
                    record_name = QSpyRecords(recordID).name
                else:
                    record_name = QSPY(recordID).name
                print("Seq:{0}, Record :{1}, {2}".format(sequence, record_name, data))

                try:
                    method_name = "_".join(("On", record_name))
                    method = getattr(self.client, method_name)
                    method(data)
                except AttributeError:
                    raise NotImplementedError("Class `{}` does not implement `{}`".format(self.client.__class__.__name__, method_name))

            except IOError as e:
                print("QSpy Socket error:", str(e) )
            pass

                

    def attach(self, client, host='localhost', port=7701, channels=QS_CHANNEL.TEXT, local_port=None):
        """ Attach to the QSpy backend

        Keyword arguments:
        host -- host IP address of QSpy (default 'local host')
        port -- socket port of QSpy (default 7701)
        channels -- what channels to attach to (default QPChannels.TEXT)
        local_port -- the local/client port to use (default None for automatic)
        """

        self.client = client

        # Store address info
        self.host = host
        self.port = port
        self.channels = channels
        self.local_port = local_port

        # Create socket and connect
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if local_port is not None:
            self.socket.bind(('', local_port))
        self.socket.connect((host, port))

        # Start receive thread
        self.start()

        self.sendAttach(channels)

    def detach(self):
        self.sendPacket(struct.pack('< B', QSPY.DETACH.value))
        time.sleep(0.300)
        self.alive.clear()
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()
        self.socket = None
        threading.Thread.join(self)
        pass
    
    def sendAttach(self, channels):
        self.sendPacket(struct.pack(
            '< B B', QSPY.ATTACH.value, channels.value))
    
    def sendLocalFilter(self, object_kind, object_id):
        """ Sends a local filter

        Arguments:
        object_kind -- kind of object from QS_OBJ_KIND
        object_id -- the object which can be an address integer or a dictionary name string
        """

        format_string = '< B B ' + theFmt['objPtr']

        if isinstance(object_id, int): 
            # Send directly to Target
            packet = struct.pack(format_string, QS_RX.LOC_FILTER, object_kind.value, object_id)
        else:
            # Have QSpy interpret object_id string and send filter
            packet = bytearray(struct.pack(format_string, QSPY.SEND_LOC_FILTER, object_kind.value, 0))
            packet.extend(qspy.string_to_binary(object_id))

        self.sendPacket(packet)

    def sendGlobalFilters(self, filter0, filter1, filter2, filter3):
        self.sendPacket(struct.pack('< B B L L L L', QS_RX.GLB_FILTER,  16, filter0, filter1, filter2, filter3))

 
    def sendCommand(self, command_id, param1 = 0, param2 = 0, param3 = 0):
        format_string = '< B B I I I'

        if isinstance(command_id, int):
            packet = struct.pack(format_string, QS_RX.COMMAND, command_id, param1, param2, param3)
        else:
            packet = bytearray(struct.pack(format_string, QSPY.SEND_COMMAND, 0, param1, param2, param3))
            # Add string command ID to end
            packet.extend(qspy.string_to_binary(command_id))

        self.sendPacket(packet)
    

    def sendCurrentObject(self, object_kind, object_id):

        format_string = '< B B ' + theFmt['objPtr']

        # Build packet according to object_id type
        if isinstance(object_id, int):
            packet = struct.pack(format_string, QS_RX.CURR_OBJ, object_kind.value, object_id)
        else:
            packet = bytearray(struct.pack(format_string, QSPY.SEND_CURR_OBJ, object_kind.value, 0))
            # add string object ID to end
            packet.extend(qspy.string_to_binary(object_id))

        self.sendPacket(packet)

    def sendTestProbe(self):
        pass

    def sendEvent(self, ao_priority, signal, parameters = None):

        format_string = '< B B ' + theFmt['sig'] + 'h'

        if parameters is not None:
            length = len(parameters)
        else:
            length = 0

        if isinstance(signal, int): 
            packet = bytearray(struct.pack(format_string, QS_RX.EVENT, ao_priority, signal, length))
            if parameters is not None:
                packet.extend(parameters)
        else:
            packet = bytearray(struct.pack(format_string, QSPY.SEND_EVENT, ao_priority, 0, length))
            if parameters is not None:
                packet.extend(parameters)
            packet.extend(qspy.string_to_binary(signal))

        self.sendPacket(packet)

 
    def sendReset(self):
        self.sendPacket(struct.pack('< B', QS_RX.RESET))

    def sendContinue(self):
        self.sendPacket(struct.pack('< B', QS_RX.CONTINUE))

    def sendPacket(self, packet):
        """ sends a packet

        Arguments:
        packet -- packet to send either a bytes() or bytearray() object
        """
        
        tx_packet = bytearray({self.tx_packet_sequence})
        tx_packet.extend(packet)

        self.socket.send(tx_packet)

        self.tx_packet_sequence += 1
        self.tx_packet_sequence = self.tx_packet_sequence % 256


    def _origsendPacket(self, binary_packet, string_packet = None):
        tx_packet = bytearray({self.tx_packet_sequence})
        tx_packet.extend(binary_packet)

        if string_packet is not None:
            # extend packet with null terminated string
            tx_packet.extend(_stringToBinaryPacket(string_packet))

        self.socket.send(tx_packet)

        self.tx_packet_sequence += 1
        self.tx_packet_sequence = self.tx_packet_sequence % 256


    @staticmethod
    def string_to_binary(string_packet):
        packed_string = bytes(string_packet, 'utf-8')
        format_string = '{0}sB'.format(len(packed_string) + 1)
        # Null terminate and return
        return(struct.pack(format_string, packed_string, 0))
        
