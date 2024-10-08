# INTERVAL
import pytest

from simplemonitor.mrl.functions import Polynomial
from simplemonitor.mrl.mrl import Interval, Integral, IntegralNode, WindowInterval, UnaryNode, BinaryNode, Memory, \
    mean_polynomial, NaryNode


# INTERVAL TESTS

def test_integrate_constant():
    interval = Interval(0, 1, Polynomial.constant(2))

    integrate = interval.integrate()

    assert integrate == 2


def test_integrate_linear():
    interval = Interval(1, 2, Polynomial.linear(1, 1))

    integrate = interval.integrate()

    assert integrate == 5 / 2


def test_integrate_full():
    interval = Interval(1, 2, Polynomial.full(1, 1, 1))
    with pytest.raises(Exception):
        interval.integrate()


def test_apply_operator():
    operator = lambda p: p + Polynomial.constant(1)
    interval = Interval(1, 2, Polynomial.constant(3))

    actual_interval = interval.apply_operator(operator)

    expected_interval = Interval(1, 2, Polynomial.constant(4))
    assert expected_interval == actual_interval


def test_apply_binary_operator():
    operator = lambda p1, p2: p1 + p2
    interval1 = Interval(1, 2, Polynomial.constant(3))
    interval2 = Interval(1, 2, Polynomial.constant(3))

    actual_interval = interval1.apply_binary_operator(operator, interval2)

    expected_interval = Interval(1, 2, Polynomial.constant(6))
    assert expected_interval == actual_interval


# INTEGRAL TESTS
def test_move_with_constant():
    integral = Integral()
    i1 = Interval(0, 1, Polynomial.constant(1))
    i2 = Interval(1, 2, Polynomial.constant(2))
    i3 = Interval(2, 3, Polynomial.constant(3))
    i4 = Interval(3, 4, Polynomial.constant(4))
    integral.add(i1)
    integral.add(i2)
    integral.add(i3)

    result = integral.move(i1, i4)

    assert result == (Interval(0, 1, Polynomial.linear(3, 6)),)


def test_move_with_linear():
    integral = Integral()
    i1 = Interval(0, 1, Polynomial.linear(1, 0))
    i2 = Interval(1, 2, Polynomial.constant(2))
    i3 = Interval(2, 3, Polynomial.constant(3))
    i4 = Interval(3, 4, Polynomial.linear(-1, 3))
    integral.add(i1)
    integral.add(i2)
    integral.add(i3)

    result = integral.move(i1, i4)

    assert result == (Interval(0, 1, Polynomial.full(-1, 0, 5.5)),)


def test_move_with_linear_and_zeros():
    integral = Integral()
    i1 = Interval(0, 1, Polynomial.linear(10, 0))
    i2 = Interval(1, 2, Polynomial.constant(2))
    i3 = Interval(2, 3, Polynomial.constant(3))
    i4 = Interval(3, 4, Polynomial.linear(-1, 8))
    integral.add(i1)
    integral.add(i2)
    integral.add(i3)

    result = integral.move(i1, i4)

    assert result[0] == Interval(0, 5 / 11, Polynomial.full(-5.5, 5, 10))
    assert result[1] == Interval(5 / 11, 1, Polynomial.full(-5.5, 5, 10))


# INTEGRALNODE TESTS

def test_receive():
    node = IntegralNode(WindowInterval(2))
    signal = []
    node.to(signal.append)
    node.receive(Interval(0, 1, Polynomial.linear(10, 0)))
    node.receive(Interval(1, 2, Polynomial.constant(2)))
    node.receive(Interval(2, 3, Polynomial.constant(3)))
    node.receive(Interval(3, 4, Polynomial.linear(-1, 8)))

    print()


# UNARYNODE TESTS

def test_unary_node_receive():
    actual_signal = []
    operator = lambda p: p + Polynomial.constant(2)
    node = UnaryNode(operator)
    node.to(actual_signal.append)

    node.receive(Interval(1, 4, Polynomial.linear(1, 3)))

    expected_signal = [Interval(1, 4, Polynomial.linear(1, 5))]
    assert expected_signal == actual_signal


# BINARY TESTS
def test_binary_node_receive():
    actual_signal = []
    operator = lambda p1, p2: p1 + p2
    node = BinaryNode(operator)
    node.to(actual_signal.append)

    node.receive_right(Interval(1, 4, Polynomial.linear(1, 3)))
    node.receive_right(Interval(4, 6, Polynomial.constant(2)))
    node.receive_left(Interval(1, 5, Polynomial.linear(1, 3)))
    node.receive_left(Interval(5, 10, Polynomial.linear(1, 3)))

    expected_signal = [Interval(1, 4, Polynomial.linear(2, 6)), Interval(4, 5, Polynomial.linear(1, 5)),
                       Interval(5, 6, Polynomial.linear(1, 5))]
    assert expected_signal == actual_signal


# MEMORY TESTS
def test_memory_receive():
    memory = Memory()
    operator = lambda p: p + Polynomial.constant(2)
    memory.add_unary_node("X", "Y", UnaryNode(operator))
    memory.add_binary_node("Y", "Z", "R", BinaryNode(lambda p1, p2: p1 + p2))

    memory.receive("X", Interval(1, 2, Polynomial.constant(2)))
    memory.receive("Z", Interval(1, 8, Polynomial.linear(1, 1)))

    assert Interval(1, 2, Polynomial.constant(4)) == memory.get_value("Y")
    assert Interval(1, 2, Polynomial.linear(1, 5)) == memory.get_value("R")


def test_memory_receive_with_nary_node():
    memory = Memory()
    memory.add_nary_node(["Y", "X", "Z"], "R", NaryNode(mean_polynomial))

    memory.receive("X", Interval(1, 2, Polynomial.constant(2)))
    memory.receive("Y", Interval(1, 8, Polynomial.linear(2, 1)))
    memory.receive("Z", Interval(1, 1.5, Polynomial.linear(1, 3)))

    assert Interval(1, 1.5, Polynomial.linear(1, 2)) == memory.get_value("R")


# function
def test_mean_polynomial():
    intervals = [Interval(1, 2, Polynomial.constant(1)),
                 Interval(1, 2, Polynomial.constant(2))]

    mean = mean_polynomial(intervals)

    assert mean == Interval(1, 2, Polynomial.constant(1.5))
