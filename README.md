# qp-plus
This project is a collection of open source extensions to the Quantum Leaps framework and tools.

The code in this project dependent upon existing code available from: https://www.state-machine.com.

## spy-py extension

Spy-py is a rewrite of the existing Tcl qspy and qutest scripts using Python. 

File | Descripton
---- | ----------
qspy.py | The Python implementation of the qspy.tcl.  
tests/config.py | File used to configure the running of the unit tests.
tests/test_qspy.py | qspy.py unit test
