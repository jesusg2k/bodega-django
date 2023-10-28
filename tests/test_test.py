from unittest import TestCase


"""
Prueba de documentacion para tests
-----------------------------------------
eskgjlsmsñldmsñdlvmdslvmste es el modulo de test

"""

def func(x):
    """
    :param name: self - parametro recibido
    :param type: int
    :return: int
    """
    return x + 1




class Test(TestCase):
    def test_test_answer(self):
        assert func(3) == 4

    def test_test_answer(self):
        assert func(2) == 3
