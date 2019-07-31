import sympy as sp

__all__ = ["H", "E", "P", "phi"]


def H(psi_in, v_in, mass, var):
    hbar= sp.symbols('hbar', real=True)
    return -(1 *hbar**2) / (2 * mass) * sp.diff(psi_in, var, 2) + v_in * psi_in

def E(phi_in, v_in, mass, var, low, high):
    return sp.integrate(phi_in * H(phi_in, v_in, mass, var),
                           (var, low, high))

def P(phi_in, psi_in, var, low, high):
    return (sp.Abs(sp.integrate(phi_in * psi_in, (var, low, high)))**2)/sp.integrate(psi_in * psi_in, (var, low, high))

def phi(n, a=1, x=None):
    if not x:
        x = sp.symbols('x')
    return (sp.sqrt(2)/sp.sqrt(a))*sp.sin((n * sp.pi * x) / a)
