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


import config # This is just needed because qutest is in parent directory
import unittest
from qutest import qutest, FILTER, QS_OBJ_KIND
import time

class test_philo(qutest):

    def on_reset(self):
        self.expect_pause()
        self.Continue()  # note continue in lower case. is a reserved word in python
        self.glb_filter(FILTER.SM, FILTER.AO, FILTER.UA)
        self.current_obj(QS_OBJ_KIND.SM_AO, 'l_philo<2>')


    def test_TIMEOUT_Philo_post(self):
        self.post('TIMEOUT_SIG')
        self.expect("%timestamp AO-Post  Sdr=QS_RX,Obj=l_philo<2>,Evt<Sig=TIMEOUT_SIG,*")
        self.expect("%timestamp AO-GetL  Obj=l_philo<2>,Evt<Sig=TIMEOUT_SIG,*")
        self.expect("%timestamp Disp===> Obj=l_philo<2>,Sig=TIMEOUT_SIG,State=Philo_thinking")
        self.expect("===RTC===> St-Exit  Obj=l_philo<2>,State=Philo_thinking")
        self.expect("%timestamp AO-Post  Sdr=l_philo<2>,Obj=l_table,Evt<Sig=HUNGRY_SIG,*")
        self.expect("===RTC===> St-Entry Obj=l_philo<2>,State=Philo_hungry")
        self.expect("%timestamp ===>Tran Obj=l_philo<2>,Sig=TIMEOUT_SIG,State=Philo_thinking->Philo_hungry")
        self.expect("%timestamp Trg-Done QS_RX_EVENT")

    def test_dummy1(self):
        time.sleep(5)

    #def test_dummy2(self):
    #    time.sleep(5)

    #def test_dummy3(self):
    #    time.sleep(5)

if __name__ == "__main__":
    unittest.main(verbosity=2)
