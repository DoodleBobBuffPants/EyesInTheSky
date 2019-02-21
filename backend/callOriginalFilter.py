# function to check the original filter function for comparison
# simple test to call CarFilter.m from Python

import matlab.engine
eng = matlab.engine.start_matlab()
cf = eng.CarFilter(nargout=0) # number of args returned from matlab
a = eng.run(cf)
