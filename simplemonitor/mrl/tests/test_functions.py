# CONSTANT FUNCTION

from simplemonitor.mrl.functions import Polynomial


# POLYNOMIAL
def test_polynomial_evaluation():
    f = Polynomial.full(1, 1, 1)

    evaluation = f(2)

    assert evaluation == 7


def test_polynomial_addition():
    f1 = Polynomial.full(1, 1, 1)
    f2 = Polynomial.full(1, 3, 2)

    add = f1 + f2

    assert add == Polynomial(2, 4, 3)


def test_polynomial_addition_with_number():
    f = Polynomial.full(1, 1, 1)

    add = f + 2

    assert add == Polynomial(1, 1, 3)


def test_polynomial_subtraction():
    f1 = Polynomial.full(1, 1, 1)
    f2 = Polynomial.full(1, 3, 2)

    minus = f1 - f2

    assert minus == Polynomial.linear(-2, -1)


def test_polynomial_subtraction_with_number():
    f1 = Polynomial.full(1, 1, 1)

    minus = f1 - 2

    assert minus == Polynomial.full(1, 1, -1)


def test_polynomial_zeros_for_constant_polynomial():
    function = Polynomial.constant(1)

    zeros = function.zeros()

    assert zeros == list()


def test_polynomial_zeros_for_linear_polynomial():
    function = Polynomial.linear(2, 3)

    zeros = function.zeros()

    assert zeros == [-3 / 2]


def test_polynomial_zeros_for_full_polynomial_with_no_zeros():
    function = Polynomial.full(1, 0, 1)

    zeros = function.zeros()

    assert zeros == list()


def test_polynomial_zeros_for_full_polynomial_with_two_coincident_zero():
    function = Polynomial.full(1, -2, 1)

    zeros = function.zeros()

    assert zeros == [1.0, ]


def test_polynomial_zeros_for_full_polynomial_with_two_zero():
    function = Polynomial.full(1, 0, -1)

    zeros = function.zeros()

    assert zeros == [-1.0, 1.0]


def test_polynomial_zeros_preserves_natural_ordering():
    f1 = Polynomial.full(1, 0, -1)
    f2 = Polynomial.full(-1, 0, 1)

    zeros_of_f1 = f1.zeros()
    zeros_of_f2 = f2.zeros()

    assert zeros_of_f1 == [-1.0, 1.0]
    assert zeros_of_f2 == [-1.0, 1.0]


# UNDEFINED
def test_undefined_evaluation():
    f = Polynomial.undefined()

    evaluation = f(2)

    assert evaluation is None


def test_undefined_addition():
    f1 = Polynomial.undefined()
    f2 = Polynomial.full(1, 3, 2)

    add = f1 + f2

    assert add == Polynomial.undefined()


def test_undefined_subtraction():
    f1 = Polynomial.undefined()
    f2 = Polynomial.full(1, 3, 2)

    add = f1 + f2

    assert add == Polynomial.undefined()