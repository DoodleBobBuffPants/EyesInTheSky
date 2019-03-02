# function to check the original filter function for comparison
# simple test to call CarFilter.m from Python
# run from this folder

import matlab.engine

# noinspection PyUnresolvedReferences
eng = matlab.engine.start_matlab()
eng.CarFilter(nargout=0)  # number of args returned from matlab
