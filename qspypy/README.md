
# The qspypy package 
The **qspypy** package is a rewrite of the existing Tcl qspy and qutest scripts 
using Python 3.6.  

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
behavior and other options can be customized via the standard _conftest.py_ 
pytest configuration script.

# Installation
Installation is through pip:

```pip3 install qspypy```


# Tcl Script Conversion
As of qspypy 1.1.0, a new system wide command line utility is provided called 
**qutest_convert**.  

This script can do _most_ of the conversion of a test script
from Tcl to Python for you (e.g. it doesn't convert Tcl binary format to Python 
struck.pack).  

Simply provide the list of Tcl test files to convert, for example:
```
qutest_convert test_table.tcl test_philo.tcl
```
In additon, this utility will create a default _conftest.py_.

# Test Creation and Test Fixtures
If you understand how the existing Tcl based qutest scripts are written,
it should not be too difficult for you to understand the qutest/pytest versions.

Each pytest test function can derive from one or more test fixtures.  These
test fixtures (defined in the qspypy.fixtures module) provide a context for  
tests and execute before (and optionally after with a _yield_) each test.  
Fixtures replace the standard xUnit setUp and tearDown methods.

Qspypy provides two basic test fixtures for you to use for your tests: 
**qutest** and **qutest_noreset**.  

Qutest and qutest_norest both provide the same per-test context,
but qutest_noreset does not reset the target.  Both of these contexts contain
the qutest_context methods that are identical (except for Coninue) to the 
qutest.tcl procedure names.

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


def on_reset(qutest):
    """ Common reset handler called by qutest after resetting target """

    qutest.expect_pause()
    qutest.glb_filter(FILTER.SM)
    qutest.loc_filter(QS_OBJ_KIND.SM_AO, 'AO_Philo<2>')
    qutest.Continue()  # note continue in lower case. is a reserved word in python
    qutest.expect("===RTC===> St-Init  Obj=AO_Philo<2>,State=QP::QHsm::top->thinking")
    qutest.expect("===RTC===> St-Entry Obj=AO_Philo<2>,State=thinking")
    qutest.expect("%timestamp Init===> Obj=AO_Philo<2>,State=thinking")
    qutest.glb_filter(FILTER.SM, FILTER.AO, FILTER.UA)
    qutest.current_obj(QS_OBJ_KIND.SM_AO, 'AO_Philo<2>')


def test_TIMEOUT_Philo_post(qutest):
    qutest.post('TIMEOUT_SIG')
    qutest.expect("%timestamp AO-Post  Sdr=QS_RX,Obj=AO_Philo<2>,Evt<Sig=TIMEOUT_SIG*")
    qutest.expect("%timestamp AO-GetL  Obj=AO_Philo<2>,Evt<Sig=TIMEOUT_SIG,*")
    qutest.expect("%timestamp Disp===> Obj=AO_Philo<2>,Sig=TIMEOUT_SIG,State=thinking")
    qutest.expect("===RTC===> St-Exit  Obj=AO_Philo<2>,State=thinking")
    qutest.expect("===RTC===> St-Entry Obj=AO_Philo<2>,State=hungry")
    qutest.expect("%timestamp ===>Tran Obj=AO_Philo<2>,Sig=TIMEOUT_SIG,State=thinking->hungry")
    qutest.expect("%timestamp Trg-Done QS_RX_EVENT")

def test_publish_EAT_2(qutest_noreset): 
    qutest = qutest_noreset # Rename for consistancy
    qutest.loc_filter(QS_OBJ_KIND.SM_AO, 'AO_Philo<2>')
    qutest.publish('EAT_SIG',  struct.pack('< B', 2)) # Send byte of value 2
    qutest.expect("%timestamp AO-Post  Sdr=QS_RX,Obj=AO_Philo<2>,Evt<Sig=EAT_SIG,*")
    qutest.expect("%timestamp Trg-Done QS_RX_EVENT")
    qutest.expect("%timestamp AO-GetL  Obj=AO_Philo<2>,Evt<Sig=EAT_SIG,*")
    qutest.expect("%timestamp Disp===> Obj=AO_Philo<2>,Sig=EAT_SIG,State=hungry")
    qutest.expect("%timestamp BSP_CALL BSP::random 123")
    qutest.expect("===RTC===> St-Entry Obj=AO_Philo<2>,State=eating")
    qutest.expect("%timestamp ===>Tran Obj=AO_Philo<2>,Sig=EAT_SIG,State=hungry->eating")
    qutest.expect("%timestamp Trg-Done QS_RX_EVENT")

```

**NOTE** In order to send arbitrary binary packet data, Python's 
[struct](https://docs.python.org/3/library/struct.html) class can be used.  

For example:
```
    qutest.dispatch('EAT_SIG', struct.pack('< B', 2))
```

# Configurion and Running Tests
In order to run a python qutest script, you need to provide a standard pytest 
_conftest.py_ configuration file.  This file needs no modifications to use the 
new qutest command line tool.

The file must contain the following at a minimum:

```
#
# pytest configuration file
#

# Load common fixtures used throughout testing
from qspypy.fixtures import session, reset, module, qutest, qutest_noreset 
```
Alternatively, this file can be modified to change the behavior of qutest by 
modifying its configuration.  

For example, to have the qspy backend start automatically, add the following:
```
# Load default configuration so we can change it before running
import qspypy.config as CONFIG

# Automatically start/stop qspy for the session
CONFIG.AUTOSTART_QSPY = True

## NOTE: You must change this to be the port your target is connected to
CONFIG.QSPY_COM_PORT = 'COM3'

```

## Test execution
The qspypy package creates a system wide executable **qutest** that provides
the identical interface at the existing qutest.tcl script.

For example, to run all of the dpp mingw example test scripts you would enter
the following terminal command in  /examples/qutest/dpp: 

```
qutest *.py mingw/test_dpp.exe

```

Which produces the following output:

```
============================= test session starts =============================
platform win32 -- Python 3.6.4, pytest-3.6.1, py-1.5.3, pluggy-0.6.0 -- c:\tools\python\python36\python.exe
cachedir: .pytest_cache
rootdir: C:\tools\qp\qpcpp_6.3.2\examples\qutest\dpp, inifile:
collected 8 items

test_philo.py::test_TIMEOUT_Philo_post PASSED                            [ 12%]
test_philo.py::test_publish_EAT_2 PASSED                                 [ 25%]
test_philo.py::test_TIMEOUT_Philo_thinking_ASSERT PASSED                 [ 37%]
test_philo.py::test_TIMEOUT_Philo_eating_PUBLISH_from_AO PASSED          [ 50%]
test_philo.py::test_timeEvt_Philo_tick PASSED                            [ 62%]
test_table.py::test_PAUSE_Table PASSED                                   [ 75%]
test_table.py::test_SERVE_Table_1 PASSED                                 [ 87%]
test_table.py::test_SERVE_Table_2 PASSED                                 [100%]

========================== 8 passed in 10.13 seconds ==========================
```



# Known Issues
- Support for config.AUTOSTART_QSPY mac not tested
- Potential issue with dropped characters on linux

# Release Notes
## 1.1.0
- Added missing qutest: fill, peek, poke
- Added command line tool **qutestpy** which is interface compatible with existing
qutest.tcl script.
- Added command line tool **qutestpy_convert** to convert tcl scripts to python.
- Fixed bug with missing setup and teardown calls.
- Qutest will no longer show a console for local targets, this can be changed by
setting LOCAL_TARGET_USES_CONSOLE to True.
- Added new configuration QSPY_LOCAL_UDP_PORT to specify local UDP port.
- Simplifed test fixtures to just require qutest or qutest_noreset.
- Added reset, setup and teardown callbacks via registration in module fixture.
- No longer kills local_target process but relies on reset message only.
- Added remaining test examples


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
qutest_convert.py | Command line tool for file Tcl to Python conversion
tests | Directory containing Python versions of test scripts
