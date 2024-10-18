# INTERVAL
from unittest.mock import MagicMock

from simplemonitor.mrl.elements import Interval, WindowInterval
from simplemonitor.mrl.functions import Polynomial
from simplemonitor.mrl.nodes import IntegralNode, UnaryNode, BinaryNode, ShiftNode


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


# SHIFT NODE
def test_shift_node_receive():
    mock_notifier = MagicMock()
    shift_node = ShiftNode(2.5)
    shift_node.to(mock_notifier)

    shift_node.receive(Interval(1, 2, Polynomial.linear(1, 1)))

    mock_notifier.assert_called_once_with(Interval(3.5, 4.5, Polynomial.linear(1, -1.5)))
