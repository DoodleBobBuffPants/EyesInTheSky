# simple test to call CarFilter.m from Python
import matlab.engine
eng = matlab.engine.start_matlab()
eng.CarFilter(nargout=0) # number of args returned from matlab