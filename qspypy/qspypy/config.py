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

#
# This file is the configuraton parameters for qutest, can be modifed here or 
# via another test start script
#

# Set to true to launch and connect to a local target 
USE_HOST_TARGET = True

# Set to true have QSpy automatically start at the beginning of a test session, qspy must be on system path
AUTOSTART_QSPY_HOST = True

if USE_HOST_TARGET:
    # Local targets communicate to qpsy via a TCP socket instead of a serial port
    QSPY_TARGET_PORT = '-t'

    # Set this to the target executible name (e.g. test_dpp), target must be on system path 
    TARGET_EXECUTABLE = 'test_dpp'  
    
    # Set to the IP address of where the QSpy resides, 
    TARGET_HOST_NAME = 'localhost'          
else:
    # Serial port that target is connected to for qspy
    # MODIFY FOR YOUR REMOTE TARGET
    QSPY_TARGET_PORT = '-cCOM3'

# How long we wait for the target to come up and send the target info record
TARGET_START_TIMEOUT_SEC = 1.000       

# How long to wait for expect calls to return (was TIMEOUT_MS in qutest.tcl)
EXPECT_TIMEOUT_SEC = 0.800

# Reset the target on every test setUp call that uses the qutest fixture
RESET_TARGET_ON_SETUP = True    