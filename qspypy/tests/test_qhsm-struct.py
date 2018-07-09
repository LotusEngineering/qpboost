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

import sys
import pytest
import struct
from qspypy.qspy import FILTER, QS_OBJ_KIND

# QUTEST test of QHsmTst structural

# preamble...
def on_reset(qutest):
    qutest.glb_filter(FILTER.SM)
    qutest.current_obj(QS_OBJ_KIND.SM,"the_hsm")


# tests...
def test_QHsmTst_init(qutest):
    qutest.init()
    qutest.expect("===RTC===> St-Init  Obj=the_hsm,State=QHsm::top->s2")
    qutest.expect("===RTC===> St-Entry Obj=the_hsm,State=s")
    qutest.expect("===RTC===> St-Entry Obj=the_hsm,State=s2")
    qutest.expect("===RTC===> St-Init  Obj=the_hsm,State=s2->s211")
    qutest.expect("===RTC===> St-Entry Obj=the_hsm,State=s21")
    qutest.expect("===RTC===> St-Entry Obj=the_hsm,State=s211")
    qutest.expect("%timestamp Init===> Obj=the_hsm,State=s211")
    qutest.expect("%timestamp Trg-Done QS_RX_EVENT")

#------------------
def test_QHsmTst_dispatch(qutest_noreset):
    qutest = qutest_noreset # name change

    qutest.dispatch("A_SIG")
    qutest.expect("%timestamp Disp===> Obj=the_hsm,Sig=A_SIG,State=s211")
    qutest.expect("===RTC===> St-Exit  Obj=the_hsm,State=s211")
    qutest.expect("===RTC===> St-Exit  Obj=the_hsm,State=s21")
    qutest.expect("===RTC===> St-Entry Obj=the_hsm,State=s21")
    qutest.expect("===RTC===> St-Init  Obj=the_hsm,State=s21->s211")
    qutest.expect("===RTC===> St-Entry Obj=the_hsm,State=s211")
    qutest.expect("%timestamp ===>Tran Obj=the_hsm,Sig=A_SIG,State=s21->s211")
    qutest.expect("%timestamp Trg-Done QS_RX_EVENT")

    qutest.dispatch("B_SIG")
    qutest.expect("%timestamp Disp===> Obj=the_hsm,Sig=B_SIG,State=s211")
    qutest.expect("===RTC===> St-Exit  Obj=the_hsm,State=s211")
    qutest.expect("===RTC===> St-Entry Obj=the_hsm,State=s211")
    qutest.expect("%timestamp ===>Tran Obj=the_hsm,Sig=B_SIG,State=s21->s211")
    qutest.expect("%timestamp Trg-Done QS_RX_EVENT")

    qutest.dispatch("D_SIG")
    qutest.expect("%timestamp Disp===> Obj=the_hsm,Sig=D_SIG,State=s211")
    qutest.expect("===RTC===> St-Exit  Obj=the_hsm,State=s211")
    qutest.expect("===RTC===> St-Init  Obj=the_hsm,State=s21->s211")
    qutest.expect("===RTC===> St-Entry Obj=the_hsm,State=s211")
    qutest.expect("%timestamp ===>Tran Obj=the_hsm,Sig=D_SIG,State=s211->s211")
    qutest.expect("%timestamp Trg-Done QS_RX_EVENT")

    qutest.dispatch("E_SIG")
    qutest.expect("%timestamp Disp===> Obj=the_hsm,Sig=E_SIG,State=s211")
    qutest.expect("===RTC===> St-Exit  Obj=the_hsm,State=s211")
    qutest.expect("===RTC===> St-Exit  Obj=the_hsm,State=s21")
    qutest.expect("===RTC===> St-Exit  Obj=the_hsm,State=s2")
    qutest.expect("===RTC===> St-Entry Obj=the_hsm,State=s1")
    qutest.expect("===RTC===> St-Entry Obj=the_hsm,State=s11")
    qutest.expect("%timestamp ===>Tran Obj=the_hsm,Sig=E_SIG,State=s->s11")
    qutest.expect("%timestamp Trg-Done QS_RX_EVENT")

    qutest.dispatch("I_SIG")
    qutest.expect("%timestamp Disp===> Obj=the_hsm,Sig=I_SIG,State=s11")
    qutest.expect("%timestamp =>Intern Obj=the_hsm,Sig=I_SIG,State=s1")
    qutest.expect("%timestamp Trg-Done QS_RX_EVENT")

    qutest.dispatch("F_SIG")
    qutest.expect("%timestamp Disp===> Obj=the_hsm,Sig=F_SIG,State=s11")
    qutest.expect("===RTC===> St-Exit  Obj=the_hsm,State=s11")
    qutest.expect("===RTC===> St-Exit  Obj=the_hsm,State=s1")
    qutest.expect("===RTC===> St-Entry Obj=the_hsm,State=s2")
    qutest.expect("===RTC===> St-Entry Obj=the_hsm,State=s21")
    qutest.expect("===RTC===> St-Entry Obj=the_hsm,State=s211")
    qutest.expect("%timestamp ===>Tran Obj=the_hsm,Sig=F_SIG,State=s1->s211")
    qutest.expect("%timestamp Trg-Done QS_RX_EVENT")

    qutest.dispatch("I_SIG")
    qutest.expect("%timestamp Disp===> Obj=the_hsm,Sig=I_SIG,State=s211")
    qutest.expect("%timestamp =>Intern Obj=the_hsm,Sig=I_SIG,State=s2")
    qutest.expect("%timestamp Trg-Done QS_RX_EVENT")

    qutest.dispatch("I_SIG")
    qutest.expect("%timestamp Disp===> Obj=the_hsm,Sig=I_SIG,State=s211")
    qutest.expect("===RTC===> St-Unhnd Obj=the_hsm,Sig=I_SIG,State=s2")
    qutest.expect("%timestamp =>Intern Obj=the_hsm,Sig=I_SIG,State=s")
    qutest.expect("%timestamp Trg-Done QS_RX_EVENT")

    qutest.dispatch("F_SIG")
    qutest.expect("%timestamp Disp===> Obj=the_hsm,Sig=F_SIG,State=s211")
    qutest.expect("===RTC===> St-Exit  Obj=the_hsm,State=s211")
    qutest.expect("===RTC===> St-Exit  Obj=the_hsm,State=s21")
    qutest.expect("===RTC===> St-Exit  Obj=the_hsm,State=s2")
    qutest.expect("===RTC===> St-Entry Obj=the_hsm,State=s1")
    qutest.expect("===RTC===> St-Entry Obj=the_hsm,State=s11")
    qutest.expect("%timestamp ===>Tran Obj=the_hsm,Sig=F_SIG,State=s2->s11")
    qutest.expect("%timestamp Trg-Done QS_RX_EVENT")

    qutest.dispatch("A_SIG")
    qutest.expect("%timestamp Disp===> Obj=the_hsm,Sig=A_SIG,State=s11")
    qutest.expect("===RTC===> St-Exit  Obj=the_hsm,State=s11")
    qutest.expect("===RTC===> St-Exit  Obj=the_hsm,State=s1")
    qutest.expect("===RTC===> St-Entry Obj=the_hsm,State=s1")
    qutest.expect("===RTC===> St-Init  Obj=the_hsm,State=s1->s11")
    qutest.expect("===RTC===> St-Entry Obj=the_hsm,State=s11")
    qutest.expect("%timestamp ===>Tran Obj=the_hsm,Sig=A_SIG,State=s1->s11")
    qutest.expect("%timestamp Trg-Done QS_RX_EVENT")

    qutest.dispatch("B_SIG")
    qutest.expect("%timestamp Disp===> Obj=the_hsm,Sig=B_SIG,State=s11")
    qutest.expect("===RTC===> St-Exit  Obj=the_hsm,State=s11")
    qutest.expect("===RTC===> St-Entry Obj=the_hsm,State=s11")
    qutest.expect("%timestamp ===>Tran Obj=the_hsm,Sig=B_SIG,State=s1->s11")
    qutest.expect("%timestamp Trg-Done QS_RX_EVENT")

    qutest.dispatch("D_SIG")
    qutest.expect("%timestamp Disp===> Obj=the_hsm,Sig=D_SIG,State=s11")
    qutest.expect("===RTC===> St-Unhnd Obj=the_hsm,Sig=D_SIG,State=s11")
    qutest.expect("===RTC===> St-Exit  Obj=the_hsm,State=s11")
    qutest.expect("===RTC===> St-Exit  Obj=the_hsm,State=s1")
    qutest.expect("===RTC===> St-Init  Obj=the_hsm,State=s->s11")
    qutest.expect("===RTC===> St-Entry Obj=the_hsm,State=s1")
    qutest.expect("===RTC===> St-Entry Obj=the_hsm,State=s11")
    qutest.expect("%timestamp ===>Tran Obj=the_hsm,Sig=D_SIG,State=s1->s11")
    qutest.expect("%timestamp Trg-Done QS_RX_EVENT")

    qutest.dispatch("D_SIG")
    qutest.expect("%timestamp Disp===> Obj=the_hsm,Sig=D_SIG,State=s11")
    qutest.expect("===RTC===> St-Exit  Obj=the_hsm,State=s11")
    qutest.expect("===RTC===> St-Init  Obj=the_hsm,State=s1->s11")
    qutest.expect("===RTC===> St-Entry Obj=the_hsm,State=s11")
    qutest.expect("%timestamp ===>Tran Obj=the_hsm,Sig=D_SIG,State=s11->s11")
    qutest.expect("%timestamp Trg-Done QS_RX_EVENT")

    qutest.dispatch("E_SIG")
    qutest.expect("%timestamp Disp===> Obj=the_hsm,Sig=E_SIG,State=s11")
    qutest.expect("===RTC===> St-Exit  Obj=the_hsm,State=s11")
    qutest.expect("===RTC===> St-Exit  Obj=the_hsm,State=s1")
    qutest.expect("===RTC===> St-Entry Obj=the_hsm,State=s1")
    qutest.expect("===RTC===> St-Entry Obj=the_hsm,State=s11")
    qutest.expect("%timestamp ===>Tran Obj=the_hsm,Sig=E_SIG,State=s->s11")
    qutest.expect("%timestamp Trg-Done QS_RX_EVENT")

    qutest.dispatch("G_SIG")
    qutest.expect("%timestamp Disp===> Obj=the_hsm,Sig=G_SIG,State=s11")
    qutest.expect("===RTC===> St-Exit  Obj=the_hsm,State=s11")
    qutest.expect("===RTC===> St-Exit  Obj=the_hsm,State=s1")
    qutest.expect("===RTC===> St-Entry Obj=the_hsm,State=s2")
    qutest.expect("===RTC===> St-Entry Obj=the_hsm,State=s21")
    qutest.expect("===RTC===> St-Entry Obj=the_hsm,State=s211")
    qutest.expect("%timestamp ===>Tran Obj=the_hsm,Sig=G_SIG,State=s11->s211")
    qutest.expect("%timestamp Trg-Done QS_RX_EVENT")

    qutest.dispatch("H_SIG")
    qutest.expect("%timestamp Disp===> Obj=the_hsm,Sig=H_SIG,State=s211")
    qutest.expect("===RTC===> St-Exit  Obj=the_hsm,State=s211")
    qutest.expect("===RTC===> St-Exit  Obj=the_hsm,State=s21")
    qutest.expect("===RTC===> St-Exit  Obj=the_hsm,State=s2")
    qutest.expect("===RTC===> St-Init  Obj=the_hsm,State=s->s11")
    qutest.expect("===RTC===> St-Entry Obj=the_hsm,State=s1")
    qutest.expect("===RTC===> St-Entry Obj=the_hsm,State=s11")
    qutest.expect("%timestamp ===>Tran Obj=the_hsm,Sig=H_SIG,State=s211->s11")
    qutest.expect("%timestamp Trg-Done QS_RX_EVENT")

    qutest.dispatch("H_SIG")
    qutest.expect("%timestamp Disp===> Obj=the_hsm,Sig=H_SIG,State=s11")
    qutest.expect("===RTC===> St-Exit  Obj=the_hsm,State=s11")
    qutest.expect("===RTC===> St-Exit  Obj=the_hsm,State=s1")
    qutest.expect("===RTC===> St-Init  Obj=the_hsm,State=s->s11")
    qutest.expect("===RTC===> St-Entry Obj=the_hsm,State=s1")
    qutest.expect("===RTC===> St-Entry Obj=the_hsm,State=s11")
    qutest.expect("%timestamp ===>Tran Obj=the_hsm,Sig=H_SIG,State=s11->s11")
    qutest.expect("%timestamp Trg-Done QS_RX_EVENT")

    qutest.dispatch("C_SIG")
    qutest.expect("%timestamp Disp===> Obj=the_hsm,Sig=C_SIG,State=s11")
    qutest.expect("===RTC===> St-Exit  Obj=the_hsm,State=s11")
    qutest.expect("===RTC===> St-Exit  Obj=the_hsm,State=s1")
    qutest.expect("===RTC===> St-Entry Obj=the_hsm,State=s2")
    qutest.expect("===RTC===> St-Init  Obj=the_hsm,State=s2->s211")
    qutest.expect("===RTC===> St-Entry Obj=the_hsm,State=s21")
    qutest.expect("===RTC===> St-Entry Obj=the_hsm,State=s211")
    qutest.expect("%timestamp ===>Tran Obj=the_hsm,Sig=C_SIG,State=s1->s211")
    qutest.expect("%timestamp Trg-Done QS_RX_EVENT")

    qutest.dispatch("G_SIG")
    qutest.expect("%timestamp Disp===> Obj=the_hsm,Sig=G_SIG,State=s211")
    qutest.expect("===RTC===> St-Exit  Obj=the_hsm,State=s211")
    qutest.expect("===RTC===> St-Exit  Obj=the_hsm,State=s21")
    qutest.expect("===RTC===> St-Exit  Obj=the_hsm,State=s2")
    qutest.expect("===RTC===> St-Entry Obj=the_hsm,State=s1")
    qutest.expect("===RTC===> St-Init  Obj=the_hsm,State=s1->s11")
    qutest.expect("===RTC===> St-Entry Obj=the_hsm,State=s11")
    qutest.expect("%timestamp ===>Tran Obj=the_hsm,Sig=G_SIG,State=s21->s11")
    qutest.expect("%timestamp Trg-Done QS_RX_EVENT")

    qutest.dispatch("C_SIG")
    qutest.expect("%timestamp Disp===> Obj=the_hsm,Sig=C_SIG,State=s11")
    qutest.expect("===RTC===> St-Exit  Obj=the_hsm,State=s11")
    qutest.expect("===RTC===> St-Exit  Obj=the_hsm,State=s1")
    qutest.expect("===RTC===> St-Entry Obj=the_hsm,State=s2")
    qutest.expect("===RTC===> St-Init  Obj=the_hsm,State=s2->s211")
    qutest.expect("===RTC===> St-Entry Obj=the_hsm,State=s21")
    qutest.expect("===RTC===> St-Entry Obj=the_hsm,State=s211")
    qutest.expect("%timestamp ===>Tran Obj=the_hsm,Sig=C_SIG,State=s1->s211")
    qutest.expect("%timestamp Trg-Done QS_RX_EVENT")

    qutest.dispatch("C_SIG")
    qutest.expect("%timestamp Disp===> Obj=the_hsm,Sig=C_SIG,State=s211")
    qutest.expect("===RTC===> St-Exit  Obj=the_hsm,State=s211")
    qutest.expect("===RTC===> St-Exit  Obj=the_hsm,State=s21")
    qutest.expect("===RTC===> St-Exit  Obj=the_hsm,State=s2")
    qutest.expect("===RTC===> St-Entry Obj=the_hsm,State=s1")
    qutest.expect("===RTC===> St-Init  Obj=the_hsm,State=s1->s11")
    qutest.expect("===RTC===> St-Entry Obj=the_hsm,State=s11")
    qutest.expect("%timestamp ===>Tran Obj=the_hsm,Sig=C_SIG,State=s2->s11")
    qutest.expect("%timestamp Trg-Done QS_RX_EVENT")

# the end


if __name__ == "__main__":
    options = ['-x', '-v', '--tb=short']
    options.extend(sys.argv)
    pytest.main(options)
