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
# pytest configuration file
#

# Load common fixtures used throughout testing
from qspypy.fixtures import qutest_session, qutest, qutest_noreset

# Load default configuration so we can change it before running
import qspypy.config as CONFIG

# Automatically start/stop qspy for the session
CONFIG.AUTOSTART_QSPY = True

## NOTE: You must change this to be the port your target is connected to
# CONFIG.QSPY_COM_PORT = 'COM3'
CONFIG.QSPY_COM_PORT = '/dev/ttyACM0'

# IF you want to run a local target, uncomment the following lines and
# change the executable name to match (executable must be on your path)
# CONFIG.USE_LOCAL_TARGET = True
# CONFIG.LOCAL_TARGET_EXECUTABLE = 'test_dpp'


