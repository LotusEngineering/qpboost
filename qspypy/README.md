
# The qspypy package 
The **qspypy** package is a rewrite of the existing Tcl qspy and qutest scripts 
using Python 3.  

This package currently contains two main modules: **qspy** and **qutest**.  

At some point in the future, the **qspyview** front end may be added as well.  
Since Python comes with Tk, the translation effort shouldn't be too great.

## The qspy module
The qspy module is the interface to the qspy back end application that ultimately 
interfaces with the target.  This module provides a series of message send and 
callback methods so that knowledge of communications is hidden from qutest.  

## The qutest module
The qutest module is designed to be run using the powerful
[pytest](https://pytest.org/) Python testing framework.  

Pytest makes it easy to discover and run your qutest scripts, 
in addition to a host of other features like jUnit XML output for Jenkins 
and hundreds of other plugins.

Finally, qutest provides the added feature of automatically starting qspy 
for you (assuming it's on your path) at the start of every test session.  This 
behavior and other options can be changed via the standard _conftest.py_ pytest
configuration script.

# Installation
Installation is through pip:

```pip3 install qspypy```

# Test Creation and Test Fixtures
If you understand how the existing Tcl based qutest scripts are written,
it should not be too difficult for you to understand the qutest/pytest versions.

Each pytest test function can derive from one or more test fixtures.  These
test fixtures (defined in the qspypy.fixtures module) provide a context for  
tests and execute before (and optionally after with a _yield_) each test.  
Fixtures replace the standard xUnit setUp and tearDown methods.


Qspypy provides three test fixtures for you to use for your tests: 
**qutest_session**, **qutest** and **qutest_noreset**.  Qutest_session is used
to create the the context for the complete session.

Qutest and qutest_norest both provide the same per-test context,
but qutest_noreset does not reset the target.  Both of these contexts contain
the qutest_context methods that are almost identical to the qutest.tcl procedure
names.

In addition to these, you can provide your own common test fixture, either in
_conftest.py_ for global access or in each individual script.

## Example from qpcpp version 6.3.2
Here is a part of the dpp _test_philo.py_ test script.  
The full example of this and the _test_table.py_ is available on
[GitHub](https://github.com/LotusEngineering/qpboost/tree/master/qspypy/tests).

```
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
    qutest.expect("%timestamp Disp===> Obj=AO_Table,Sig=PAUSE_SIG,State=serving")
    qutest.expect("%timestamp BSP_CALL BSP::displayPaused 1")
    qutest.expect("===RTC===> St-Entry Obj=AO_Table,State=paused")
    qutest.expect("%timestamp ===>Tran Obj=AO_Table,Sig=PAUSE_SIG,State=serving->paused")
    qutest.expect("%timestamp Trg-Done QS_RX_EVENT")

def test_SERVE_Table_1(qutest, on_reset):
    qutest.command(1)
    qutest.expect("%timestamp Disp===> Obj=AO_Table,Sig=SERVE_SIG,State=serving")
    qutest.expect("%timestamp =>Ignore Obj=AO_Table,Sig=SERVE_SIG,State=serving")
    qutest.expect("%timestamp Trg-Done QS_RX_COMMAND")

```

**NOTE** In order to send arbitrary binary packet data, Python's 
[struct](https://docs.python.org/3/library/struct.html) class can be used.  

For example:
```
    qutest.dispatch('EAT_SIG', struct.pack('< B', 2))
```

# Configurion and Running Tests

## Configuring qutest and pytest
Before you can run your tests, you must configure pytest by creating a 
_conftest.py_ file in the folder where your tests reside.  At a minimum, this 
file needs to include the qspypy fixtures.  You can also configure qutest
by importing qspy.config and modifying the default values.

Here's the example from qspypy/tests on GitHub:
```
# Load common fixtures used throughout testing
from qspypy.fixtures import qutest_session, qutest, qutest_noreset

# Load default configuration so we can change it before running
import qspypy.config as CONFIG

# Automatically start/stop qspy for the session
CONFIG.AUTOSTART_QSPY = True

## NOTE: You must change this to be the port your target is connected to
CONFIG.QSPY_COM_PORT = 'COM3'
```
You can also change this file to run a local target if you are running one.

## Test execution
You can run pytest either from a Python script (see end of example scripts), or 
simply from the command line.  For example to run one test in verbose mode:
```
pytest -v test_philo.py
```


Produces the following output:
```
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


To have pytest discover and run all of your tests, in verbose mode 
(stopping at the first failure), use the following:
```
pytest -x -v
```


You can run the above command from any directory in or above your scripts 
as pytest will recurse into folders and run any tests it finds.

# Known Issues
- Support for config.AUTOSTART_QSPY mac not tested
- Potential issue with dropped characters on linux

# Release Notes
## 1.1.0
- Added command line tool **qutest** which is interface compatible with existing
qutest.tcl script.
- Qutest will no longer show a console for local targets, this can be changed by
setting LOCAL_TARGET_USES_CONSOLE to True.
- Added new configuration QSPY_LOCAL_UDP_PORT to specify local UDP port.
- Simplifed test fixtures to just require qutest or qutest_noreset.
- Added reset callback via registration in module fixture.
- No longer kills local_target process but relies on reset message only.
- Added another test example: test_blinky.py


## 1.0.1
- Fixed crash on linux
- Added config.AUTOSTART_QSPY support for linux via gnome-terminal
- Now defaults to config.AUTOSTART_QSPY to False 

## 1.0.0
- Initial release to PyPi

# Source File Description
File | Descripton
---- | ----------
config.py | Configuration values used in qutest.py  
fixtures.py | pytest fixtures to used in the user's conftest.py
qspy.py | The Python implementation of the qspy.tcl qspy interface library
qutest.py | The Python implementaition of qutest.tcl
tests/conftest.py | File used to configure the running of the unit tests.
tests/test_philo.py | Example qspypy version of test_philo.tcl from qpcpp/examples/qutest/dpp
tests/test_table.py | Example qspypy version of test_table.tcl from qpcpp/examples/qutest/dpp
