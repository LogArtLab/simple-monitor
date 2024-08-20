import numpy as np
from antlr4 import InputStream, CommonTokenStream

from stl.Monitor import STLMonitorBuilder
from stl.RobSemantics import RobSemantics
from stl.STLLexer import STLLexer
from stl.STLParser import STLParser
from stl.TimeSeries import TimeSeries

# formula = '(G_[1,6] (Q>2)) | (!(F_[1,10](P<=4)))'
timeSeries = TimeSeries(['P', 'Q'],
                        np.array([0, 1, 2, 3, 4]),
                        np.array([[5, 67, -6, -1, -1],
                                  [3, 3, -3, -1, -1]]))

formula = '(G_[1,6] (Q>-20))'
monitor = STLMonitorBuilder(formula).build()
value = monitor.monitor(RobSemantics(timeSeries=timeSeries, currentState=0))
print(value)
print("DONE")
