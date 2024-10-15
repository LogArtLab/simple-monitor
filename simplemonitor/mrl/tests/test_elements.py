# INTERVAL TESTS
import pytest

from simplemonitor.mrl.elements import Interval, Integral, Memory, Min
from simplemonitor.mrl.functions import Polynomial
from simplemonitor.mrl.nodes import UnaryNode, BinaryNode, NaryNode
from simplemonitor.mrl.utility import mean_polynomial


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


def test_min_interval_left_constant():
    left = Interval(1, 2, Polynomial.constant(3))
    right = Interval(1, 2, Polynomial.constant(4))

    min_interval = left.min_interval(right)

    assert min_interval == [left, ]


def test_min_interval_right_constant():
    left = Interval(1, 2, Polynomial.constant(4))
    right = Interval(1, 2, Polynomial.constant(3))

    min_interval = left.min_interval(right)

    assert min_interval == [right, ]


def test_min_interval_right_linear():
    left = Interval(1, 2, Polynomial.linear(1, 0))
    right = Interval(1, 2, Polynomial.linear(-1, 3))

    min_interval = left.min_interval(right)

    assert min_interval == [Interval(1, 1.5, Polynomial.linear(1, 0)), Interval(1.5, 2, Polynomial.linear(-1, 3))]


def test_min_interval_same_interval():
    left = Interval(1, 2, Polynomial.linear(1, 0))
    right = Interval(1, 2, Polynomial.linear(1, 0))

    min_interval = left.min_interval(right)

    assert min_interval == [right, ]


def test_min_interval_polynomial_with_no_zeros():
    left = Interval(1, 2, Polynomial.full(1, 0, 0))
    right = Interval(1, 2, Polynomial.linear(1, -.1))

    min_interval = left.min_interval(right)

    assert min_interval == [right, ]


def test_min_interval_polynomial_with_zeros():
    left = Interval(0, 1, Polynomial.full(1, 0, 0))
    right = Interval(0, 1, Polynomial.linear(1, -.1))

    min_interval = left.min_interval(right)

    assert min_interval == [Interval(0.0, 0.1127016653792583, Polynomial.linear(1, -0.1)),
                            Interval(0.1127016653792583, 0.8872983346207417, Polynomial.full(1, 0, 0)),
                            Interval(0.8872983346207417, 1.0, Polynomial.linear(1, -0.1)),
                            ]


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


# TEST MIN
def test_move_with_constants():
    min_operator = Min()
    first_interval = Interval(1, 2, Polynomial.constant(4))
    second_interval = Interval(2, 3, Polynomial.constant(3))
    third_interval = Interval(3, 4, Polynomial.constant(2))
    min_operator.add(first_interval)
    min_operator.add(second_interval)

    minimum = min_operator.move(first_interval, third_interval)

    assert minimum == [Interval(1, 2, Polynomial.constant(2)), ]


def test_move_with_functions():
    min_operator = Min()
    first_interval = Interval(1, 2, Polynomial.linear(1, 1))
    second_interval = Interval(2, 3, Polynomial.constant(1.5))
    third_interval = Interval(3, 4, Polynomial.constant(1))
    fourth_interval = Interval(4, 5, Polynomial.constant(2))
    min_operator.add(first_interval)
    min_operator.add(second_interval)
    min_operator.add(third_interval)

    minimum = min_operator.move(first_interval, fourth_interval)

    assert minimum == [Interval(1, 2, Polynomial.constant(1)), ]


def test_move_with_functions_version():
    min_operator = Min()
    first_interval = Interval(1, 2, Polynomial.linear(1, 1))
    second_interval = Interval(2, 3, Polynomial.constant(1.5))
    third_interval = Interval(3, 4, Polynomial.constant(1))
    min_operator.add(first_interval)
    min_operator.add(second_interval)

    minimum = min_operator.move(first_interval, third_interval)

    assert minimum == [Interval(1, 2, Polynomial.constant(1)), ]


def test_move_with_functions_and_zeros():
    min_operator = Min()
    first_interval = Interval(1, 2, Polynomial.linear(1, 1))
    second_interval = Interval(2, 3, Polynomial.constant(2.7))
    third_interval = Interval(3, 4, Polynomial.constant(3))
    min_operator.add(first_interval)
    min_operator.add(second_interval)

    minimum = min_operator.move(first_interval, third_interval)

    assert minimum == [Interval(1, 1.7, Polynomial.linear(1, 1)), Interval(1.7, 2.0, Polynomial.constant(2.7))]
