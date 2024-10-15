# function
from simplemonitor.mrl.elements import Interval
from simplemonitor.mrl.functions import Polynomial
from simplemonitor.mrl.utility import mean_polynomial


def test_mean_polynomial():
    intervals = [Interval(1, 2, Polynomial.constant(1)),
                 Interval(1, 2, Polynomial.constant(2))]

    mean = mean_polynomial(intervals)

    assert mean == Interval(1, 2, Polynomial.constant(1.5))
