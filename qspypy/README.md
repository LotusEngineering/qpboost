
# qspypy

**qspypy** is a rewrite of the existing Tcl qspy and qutest scripts using Python. 

File | Descripton
---- | ----------
qspy.py | The Python implementation of the qspy.tcl qspy interface library
qutest.py | The Python implementaition of qutest.tcl
config.py | Configuration values used in qutest.tcl  
tests/config.py | File used to configure the running of the unit tests.
tests/test_qspy.py | qspy.py unit test
tests/test_philo.py | qspypy version of test_philo.tcl from qpcpp/examples/qutest/dpp
tests/test_table.py | qspypy version of test_table.tcl from qpcpp/examples/qutest/dpp
