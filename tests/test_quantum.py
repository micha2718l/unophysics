from unophysics import quantum
import sympy as sp
import pytest

class TestPhi:
    x = sp.symbols('x')

    def test_phi_n1(self):
        phi_1 = sp.sqrt(2) * sp.sin(sp.pi * self.x)
        phi = quantum.phi(n=1, x=self.x)
        assert phi == phi_1, "Should be sqrt(2)*sin(pi*x)"

    def test_phi_n1(self):
        phi_2 = sp.sqrt(2) * sp.sin(2 * sp.pi * self.x)
        phi = quantum.phi(n=2, x=self.x)
        assert phi == phi_2, "Should be sqrt(2)*sin(2*pi*x)"

    def test_phi_n1_a5(self):
        phi_2 = sp.sqrt(10) * sp.sin(sp.pi * self.x /5) / 5
        phi = quantum.phi(n=1, a=5, x=self.x)
        assert phi == phi_2, "Should be sqrt(2)*sin(2*pi*x)"

    def test_phi_non_integer(self):
        with pytest.raises(ValueError) as e:
            assert quantum.phi(n=1.3)

        assert str(e.value) == "n must be integer."
