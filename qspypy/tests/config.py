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

import os
import sys

# Append the top level directory to the system path since python doesn't allow a relative imports there
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


# Set to true to have test suite launch dpp test application on host, false to run over serial port
# You must have the dpp_test executible on your path if you set this to true
USE_LOCAL_DPP_TEST = True

if USE_LOCAL_DPP_TEST: 
    QSPY_TARGET_PORT = '-t' 
    DPP_HOST_NAME = 'localhost' # Change to remote IP if dpp runs on another PC
else:
    # Change to port that qspy connects to the physciall target with, e.g.:  -cCOM3, -c/dev/ttyO4
    QSPY_TARGET_PORT = '-cCOM3'
    

