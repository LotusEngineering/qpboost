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
# preamble...

#
# This file is an example rewrite of test_table.tcl using qspypy
# NOTE: This script is compatible with the qutest DPP example in qpcpp 6.3.2
#

import sys
import pytest
import struct
from qspypy.qspy import FILTER, QS_OBJ_KIND


@pytest.fixture
def on_reset(qutest):
    """ Common fixture to handle reset """
    
    qutest.expect_pause()
    qutest.Continue()  # note continue in lower case. is a reserved word in python
    qutest.glb_filter(FILTER.SM, FILTER.AO, FILTER.UA)
    qutest.loc_filter(QS_OBJ_KIND.AO, 'AO_Table')
    qutest.current_obj(QS_OBJ_KIND.SM_AO, 'AO_Table')

# tests...


def test_PAUSE_Table(qutest, on_reset):
    qutest.dispatch('PAUSE_SIG')
    qutest.expect(
        "%timestamp Disp===> Obj=AO_Table,Sig=PAUSE_SIG,State=serving")
    qutest.expect("%timestamp BSP_CALL BSP::displayPaused 1")
    qutest.expect("===RTC===> St-Entry Obj=AO_Table,State=paused")
    qutest.expect(
        "%timestamp ===>Tran Obj=AO_Table,Sig=PAUSE_SIG,State=serving->paused")
    qutest.expect("%timestamp Trg-Done QS_RX_EVENT")


def test_SERVE_Table_1(qutest, on_reset):
    qutest.command(1)
    qutest.expect(
        "%timestamp Disp===> Obj=AO_Table,Sig=SERVE_SIG,State=serving")
    qutest.expect(
        "%timestamp =>Ignore Obj=AO_Table,Sig=SERVE_SIG,State=serving")
    qutest.expect("%timestamp Trg-Done QS_RX_COMMAND")


def test_SERVE_Table_2(qutest_noreset):
    qutest = qutest_noreset  # name change
    qutest.probe('BSP::displayPaused', 1)
    qutest.dispatch('PAUSE_SIG')
    qutest.expect(
        "%timestamp Disp===> Obj=AO_Table,Sig=PAUSE_SIG,State=serving")
    qutest.expect("%timestamp TstProbe Fun=BSP::displayPaused,Data=1")
    qutest.expect("%timestamp =ASSERT= Mod=bsp,Loc=100")


if __name__ == "__main__":
    options = ['-x', '-v', '--tb=short']
    options.extend(sys.argv)
    pytest.main(options)
