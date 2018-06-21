
# The qspypy package 
The **qspypy** package is a rewrite of the existing Tcl qspy and qutest scripts 
using Python.  

This package currently contains to modules: **qspy** and **qutest**.  

At some point in the future, the **qspyview** frontend maybe added as well.  
Since Python comes with Tk, the translation effort shouldn't be too great.

## The qspy module
The qspy module is the interface to the qspy backend application that ultimately 
interfaces with the target.  This module provides a series of message send and 
callback methods so that knowledge of communications is hidden from any of the
frontends that use it.

## The qutest module
The qutest module is designed to be run using the powerful
[pytest](https://pytest.org/) Python testing frame work.  

Pytest makes it easy to discover and run your **qutest** scripts, 
in addition to host of other features like jUnit XML output for Jenkins 
and hundreds of other plugins.

Finally, qutest provides the added feature of automatically starting qspy 
for you (assuming its on your path) at the start of every test session.  This 
behavior and other options can be changed via the standard _conftest.py_ pytest
configuration script.

# Installation
Installation is though pip:

```pip install qspypy```

# Test Creation
If you understand the how the existing Tcl based qutest scripts are written,
it should not be too difficult for you to understand the qutest/pytest versions.

Each pytest test function can derive from one or more test fixtures.  These
test fixtures provide a context for a test and execute before (and 
optionally after with a _yield_) each test.  This replaces the standard xUnit
setUp and tearDown methods.

Qutest provides two test fixtures for you to use for your tests, 
**qutest** and **qutest_noreset**.  As you can imagine, they both provide the
same functinality, but **qutest_norest** does not reset the target.

In addition to these, you can provide your own common test fixture, either in
conftest.py for global access or in each individual script.

# Example from qpcpp version 6.2.0
Here is a part of the dpp test_philo.py test script.  
The full example of this and the test_table.py is available on
[GitHub](https://github.com/LotusEngineering/qpboost/tree/master/qspypy/tests).

```
import pytest
import struct
from qspypy.qspy import FILTER, QS_OBJ_KIND
from qspypy.qutest import qutest, qutest_noreset, qutest_session


@pytest.fixture
def on_reset(qutest):
    qutest.expect_pause()
    qutest.Continue()  # note continue in lower case. is a reserved word in python
    qutest.glb_filter(FILTER.SM, FILTER.AO)
    qutest.loc_filter(QS_OBJ_KIND.AO, 'l_table')
    qutest.current_obj(QS_OBJ_KIND.SM_AO, 'l_table')

# tests...
def test_PAUSE_Table(qutest, on_reset):
    qutest.dispatch('PAUSE_SIG')
    qutest.expect("%timestamp Disp===> Obj=l_table,Sig=PAUSE_SIG,State=Table::serving")
    qutest.expect("===RTC===> St-Entry Obj=l_table,State=Table::paused")
    qutest.expect("%timestamp ===>Tran Obj=l_table,Sig=PAUSE_SIG,State=Table::serving->Table::paused")
    qutest.expect("%timestamp Trg-Done QS_RX_EVENT")

def test_SERVE_Table_1(qutest, on_reset):
    qutest.command(1)
    qutest.expect("%timestamp Disp===> Obj=l_table,Sig=SERVE_SIG,State=Table::serving")
    qutest.expect("%timestamp =>Ignore Obj=l_table,Sig=SERVE_SIG,State=Table::serving")
    qutest.expect("%timestamp Trg-Done QS_RX_COMMAND")

```

**NOTE** In order to send arbitrary binary packet data, Pythons **struct**
class can be used.  For example:

```
    qutest.dispatch('EAT_SIG', struct.pack('< B', 2))
```

# Configurion and Running Tests

## Configuring qutest and pytest
Before you can run your tests, you must configure pytest by creating a 
conftest.py file where your tests reside.  At a minimum this file needs to 
contain the com port that qspy uses to communicate with the target. Here's the
example from qspypy/tests:

```
#
# conftest.py pytest configuration file
#
import pytest
import qspypy.config as CONFIG

## Change this to be the port your target is connected to
CONFIG.QSPY_COM_PORT = 'COM3'
```
You can also change this file to run a local target if you are running one.

## Test execution
You can run pytest either from a Python script (see end of example scripts), or 
simple from the command line.  For example to run one test in verbose mode:
```
pytest -v test_philo.py
```
Procuces the following output:

```
pytest -v test_philo.py

============================= test session starts =============================
platform win32 -- Python 3.6.4, pytest-3.6.1, py-1.5.3, pluggy-0.6.0 -- C:\tools\Python\Python36\python.exe
cachedir: ..\.pytest_cache
rootdir: C:\dev\qpboost\qspypy, inifile:
collected 5 items

test_philo.py::test_TIMEOUT_Philo_post PASSED                            [ 20%]
test_philo.py::test_publish_EAT_2 PASSED                                 [ 40%]
test_philo.py::test_TIMEOUT_Philo_thinking_ASSERT PASSED                 [ 60%]
test_philo.py::test_TIMEOUT_Philo_eating_PUBLISH_from_AO PASSED          [ 80%]
test_philo.py::test_timeEvt_Philo_tick PASSED                            [100%]

========================== 5 passed in 2.67 seconds ===========================
```

# Source File Description
File | Descripton
---- | ----------
qspy.py | The Python implementation of the qspy.tcl qspy interface library
qutest.py | The Python implementaition of qutest.tcl
config.py | Configuration values used in qutest.tcl  
tests/config.py | File used to configure the running of the unit tests.
tests/test_qspy.py | qspy.py unit test, based on unittest on pytest
tests/test_philo.py | Example qspypy version of test_philo.tcl from qpcpp/examples/qutest/dpp
tests/test_table.py | Example qspypy version of test_table.tcl from qpcpp/examples/qutest/dpp
