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
