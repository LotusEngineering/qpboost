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
# This file is an example rewrite of test_blinky.tcl using qspypy
# NOTE: This script is compatible with the qutest blinky example in qpcpp 6.3.2
#
import sys
import pytest
import struct
from qspypy.qspy import FILTER, QS_OBJ_KIND

# preamble...
def on_reset(qutest):
    qutest.expect_pause()
    qutest.glb_filter(FILTER.ON) 
    qutest.Continue()
    qutest.expect("%timestamp TE0-Arm  Obj=l_blinky.m_timeEvt,AO=l_blinky,*")
    qutest.expect("===RTC===> St-Init  Obj=l_blinky,State=QHsm::top->off")
    qutest.expect("%timestamp LED 0")
    qutest.expect("===RTC===> St-Entry Obj=l_blinky,State=off")
    qutest.expect("%timestamp Init===> Obj=l_blinky,State=off")
    qutest.current_obj( QS_OBJ_KIND.SM_AO, 'l_blinky')


# tests...
def test_TIMEOUT_SIG_l_blinky(qutest):
    qutest.post('TIMEOUT_SIG')
    qutest.expect("%timestamp QF-New   Sig=TIMEOUT_SIG,*")
    qutest.expect("%timestamp MP-Get   Obj=smlPoolSto,*")
    qutest.expect("%timestamp AO-Post  Sdr=QS_RX,Obj=l_blinky,Evt<Sig=TIMEOUT_SIG,*")
    qutest.expect("%timestamp AO-GetL  Obj=l_blinky,Evt<Sig=TIMEOUT_SIG,*")
    qutest.expect("%timestamp Disp===> Obj=l_blinky,Sig=TIMEOUT_SIG,State=off")
    qutest.expect("%timestamp LED 1")
    qutest.expect("===RTC===> St-Entry Obj=l_blinky,State=on")
    qutest.expect("%timestamp ===>Tran Obj=l_blinky,Sig=TIMEOUT_SIG,State=off->on")
    qutest.expect("%timestamp QF-gc    Evt<Sig=TIMEOUT_SIG,*")
    qutest.expect("%timestamp MP-Put   Obj=smlPoolSto,*")
    qutest.expect("%timestamp Trg-Done QS_RX_EVENT")

def test_timeEvt_Blinky_tick(qutest):
    qutest.current_obj(QS_OBJ_KIND.TE, 'l_blinky.m_timeEvt')
    qutest.tick()
    qutest.expect("%timestamp TE0-Post Obj=l_blinky.m_timeEvt,Sig=TIMEOUT_SIG,AO=l_blinky")
    qutest.expect("%timestamp AO-Post  Sdr=QS_RX,Obj=l_blinky,Evt<Sig=TIMEOUT_SIG,*")
    qutest.expect("%timestamp AO-GetL  Obj=l_blinky,Evt<Sig=TIMEOUT_SIG,*")
    qutest.expect("%timestamp Disp===> Obj=l_blinky,Sig=TIMEOUT_SIG,State=off")
    qutest.expect("%timestamp LED 1")
    qutest.expect("===RTC===> St-Entry Obj=l_blinky,State=on")
    qutest.expect("%timestamp ===>Tran Obj=l_blinky,Sig=TIMEOUT_SIG,State=off->on")
    qutest.expect("%timestamp Trg-Done QS_RX_TICK")

def test_timeEvt_Blinky_tick2(qutest_noreset):
    qutest = qutest_noreset #rename
    qutest.tick()
    qutest.expect("%timestamp TE0-Post Obj=l_blinky.m_timeEvt,Sig=TIMEOUT_SIG,AO=l_blinky")
    qutest.expect("%timestamp AO-Post  Sdr=QS_RX,Obj=l_blinky,Evt<Sig=TIMEOUT_SIG,*")
    qutest.expect("%timestamp AO-GetL  Obj=l_blinky,Evt<Sig=TIMEOUT_SIG,*")
    qutest.expect("%timestamp Disp===> Obj=l_blinky,Sig=TIMEOUT_SIG,State=on")
    qutest.expect("%timestamp LED 0")
    qutest.expect("===RTC===> St-Entry Obj=l_blinky,State=off")
    qutest.expect("%timestamp ===>Tran Obj=l_blinky,Sig=TIMEOUT_SIG,State=on->off")
    qutest.expect("%timestamp Trg-Done QS_RX_TICK")


if __name__ == "__main__":
    options = ['-x', '-v', '--tb=short']
    options.extend(sys.argv)
    pytest.main(options)
 