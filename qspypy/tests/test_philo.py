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
# This file is an example rewrite of test_philo.tcl using qspypy
#

# The following 2 imports are only needed from if running this file from a source distributon
import sys
import config 

import pytest
import struct
from qspypy.qspy import FILTER, QS_OBJ_KIND
from qspypy.qutest import qutest, qutest_noreset, qutest_session


@pytest.fixture
def on_reset(qutest):
    """ Additional test fixture that we want to run before each test """

    qutest.expect_pause()
    qutest.Continue()  # note continue in lower case. is a reserved word in python
    qutest.glb_filter(FILTER.SM, FILTER.AO, FILTER.UA)
    qutest.current_obj(QS_OBJ_KIND.SM_AO, 'l_philo<2>')


def test_TIMEOUT_Philo_post(qutest, on_reset):
    qutest.post('TIMEOUT_SIG')
    qutest.expect("%timestamp AO-Post  Sdr=QS_RX,Obj=l_philo<2>,Evt<Sig=TIMEOUT_SIG,*")
    qutest.expect("%timestamp AO-GetL  Obj=l_philo<2>,Evt<Sig=TIMEOUT_SIG,*")
    qutest.expect("%timestamp Disp===> Obj=l_philo<2>,Sig=TIMEOUT_SIG,State=Philo::thinking")
    qutest.expect("===RTC===> St-Exit  Obj=l_philo<2>,State=Philo::thinking")
    qutest.expect("%timestamp AO-Post  Sdr=l_philo<2>,Obj=l_table,Evt<Sig=HUNGRY_SIG,*")
    qutest.expect("===RTC===> St-Entry Obj=l_philo<2>,State=Philo::hungry")
    qutest.expect("%timestamp ===>Tran Obj=l_philo<2>,Sig=TIMEOUT_SIG,State=Philo::thinking->Philo::hungry")
    qutest.expect("%timestamp Trg-Done QS_RX_EVENT")

def test_publish_EAT_2(qutest_noreset): 
    qutest = qutest_noreset # Rename for consistancy
    qutest.loc_filter(QS_OBJ_KIND.SM_AO, 'l_philo<2>')
    qutest.publish('EAT_SIG',  struct.pack('< B', 2)) # Send byte of value 2
    qutest.expect("%timestamp AO-Post  Sdr=QS_RX,Obj=l_philo<2>,Evt<Sig=EAT_SIG,*")
    qutest.expect("%timestamp Trg-Done QS_RX_EVENT")
    qutest.expect("%timestamp AO-GetL  Obj=l_philo<2>,Evt<Sig=EAT_SIG,*")
    qutest.expect("%timestamp Disp===> Obj=l_philo<2>,Sig=EAT_SIG,State=Philo::hungry")
    qutest.expect("===RTC===> St-Entry Obj=l_philo<2>,State=Philo::eating")
    qutest.expect("%timestamp ===>Tran Obj=l_philo<2>,Sig=EAT_SIG,State=Philo::hungry->Philo::eating")
    qutest.expect("%timestamp Trg-Done QS_RX_EVENT")

def test_TIMEOUT_Philo_thinking_ASSERT(qutest, on_reset):
    qutest.probe('QActive::post_', 1)
    qutest.dispatch('TIMEOUT_SIG')
    qutest.expect("%timestamp Disp===> Obj=l_philo<2>,Sig=TIMEOUT_SIG,State=Philo::thinking")
    qutest.expect("===RTC===> St-Exit  Obj=l_philo<2>,State=Philo::thinking")
    qutest.expect("%timestamp TstProbe Fun=QActive::post_,Data=1")
    qutest.expect("%timestamp =ASSERT= Mod=qf_actq,Loc=110")

def test_TIMEOUT_Philo_eating_PUBLISH_from_AO(qutest, on_reset):
    qutest.glb_filter(FILTER.OFF)
    qutest.dispatch('TIMEOUT_SIG')
    qutest.expect("%timestamp Trg-Done QS_RX_EVENT")
    qutest.dispatch('EAT_SIG', struct.pack('< B', 2))
    qutest.expect("%timestamp Trg-Done QS_RX_EVENT")
    qutest.glb_filter(FILTER.SM, FILTER.AO, FILTER.QF)
    qutest.dispatch('TIMEOUT_SIG')
    qutest.expect("%timestamp QF-New   Sig=TIMEOUT_SIG,*")
    qutest.expect("%timestamp Disp===> Obj=l_philo<2>,Sig=TIMEOUT_SIG,State=Philo::eating")
    qutest.expect("%timestamp QF-New   Sig=DONE_SIG,*")
    qutest.expect("%timestamp QF-Pub   Sdr=l_philo<2>,Evt<Sig=DONE_SIG,Pool=1,Ref=0>")
    qutest.expect("%timestamp AO-Post  Sdr=l_philo<2>,Obj=l_table,Evt<Sig=DONE_SIG,Pool=1,Ref=2>,*")
    qutest.expect("%timestamp QF-gcA   Evt<Sig=DONE_SIG,Pool=1,Ref=2>")
    qutest.expect("===RTC===> St-Exit  Obj=l_philo<2>,State=Philo::eating")
    qutest.expect("===RTC===> St-Entry Obj=l_philo<2>,State=Philo::thinking")
    qutest.expect("%timestamp ===>Tran Obj=l_philo<2>,Sig=TIMEOUT_SIG,State=Philo::eating->Philo::thinking")
    qutest.expect("%timestamp QF-gc    Evt<Sig=TIMEOUT_SIG,Pool=1,Ref=1>")
    qutest.expect("%timestamp Trg-Done QS_RX_EVENT")

def test_timeEvt_Philo_tick(qutest, on_reset):
    qutest.glb_filter(FILTER.SM, FILTER.AO, FILTER.TE)
    qutest.current_obj(QS_OBJ_KIND.TE, 'l_philo<2>.m_timeEvt')
    qutest.tick()
    qutest.expect("           TE0-ADis Obj=l_philo<2>.m_timeEvt,AO=l_philo<2>")
    qutest.expect("%timestamp TE0-Post Obj=l_philo<2>.m_timeEvt,Sig=TIMEOUT_SIG,AO=l_philo<2>")
    qutest.expect("%timestamp AO-Post  Sdr=QS_RX,Obj=l_philo<2>,Evt<Sig=TIMEOUT_SIG*")
    qutest.expect("%timestamp AO-GetL  Obj=l_philo<2>,Evt<Sig=TIMEOUT_SIG*")
    qutest.expect("%timestamp Disp===> Obj=l_philo<2>,Sig=TIMEOUT_SIG,State=Philo::thinking")
    qutest.expect("%timestamp TE0-DisA Obj=l_philo<2>.m_timeEvt,AO=l_philo<2>")
    qutest.expect("===RTC===> St-Exit  Obj=l_philo<2>,State=Philo::thinking")
    qutest.expect("%timestamp AO-Post  Sdr=l_philo<2>,Obj=l_table,Evt<Sig=HUNGRY_SIG*")
    qutest.expect("===RTC===> St-Entry Obj=l_philo<2>,State=Philo::hungry")
    qutest.expect("%timestamp ===>Tran Obj=l_philo<2>,Sig=TIMEOUT_SIG,State=Philo::thinking->Philo::hungry")
    qutest.expect("%timestamp Trg-Done QS_RX_TICK")


if __name__ == "__main__":

    # stop on first failure, verbose output but small stack trace
    options = ['-x', '-v', '--tb=short']
    options.extend(sys.argv)
    pytest.main(options)

