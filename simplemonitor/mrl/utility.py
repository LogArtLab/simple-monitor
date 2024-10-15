from typing import List

from simplemonitor.mrl.elements import Interval
from simplemonitor.mrl.functions import Polynomial


def mean_polynomial(interval: List[Interval]):
    result = interval[0]
    n = len(interval)
    for i in range(1, n):
        result = result + interval[i]
    rf = result.function
    return Interval(result.start, result.end, Polynomial(rf.a / n, rf.b / n, rf.c / n))
