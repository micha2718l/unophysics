from unophysics import quantum
import sympy as sp
import pytest

x = sp.symbols('x')

class TestPhi:

    def test_phi_n1(self):
        phi_1 = sp.sqrt(2) * sp.sin(sp.pi * x)
        phi = quantum.phi(n=1, x=x)
        assert phi == phi_1, "Should be sqrt(2)*sin(pi*x)"

    def test_phi_n2(self):
        phi_2 = sp.sqrt(2) * sp.sin(2 * sp.pi * x)
        phi = quantum.phi(n=2, x=x)
        assert phi == phi_2, "Should be sqrt(2)*sin(2*pi*x)"

    def test_phi_n1_a5(self):
        phi_2 = sp.sqrt(10) * sp.sin(sp.pi * x /5) / 5
        phi = quantum.phi(n=1, a=5, x=x)
        assert phi == phi_2, "Should be sqrt(2)*sin(2*pi*x)"

    def test_phi_non_integer(self):
        with pytest.raises(ValueError) as e:
            assert quantum.phi(n=1.3)

        assert str(e.value) == "n must be integer."

    def test_phi_no_args(self):
        phi = sp.sqrt(2) * sp.sin(sp.pi * x)
        phi_no_args = quantum.phi()
        assert phi == phi_no_args, "Should be sqrt(2)*sin(pi*x)"
