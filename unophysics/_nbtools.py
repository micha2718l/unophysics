
import sympy
from IPython.display import Latex, Markdown, display

__all__ = ['pmath', 'nbprint', 'setup_notebook']


def nbprint(string):
    display(Markdown(string))


lt = sympy.latex
sympy.init_printing()


def pmath(sym, ret=False, pre='', post='', preM='', postM=''):
    output = f'{pre}${preM}{lt(sym)}{postM}${post}'
    if ret:
        return output
    nbprint(output)


def setup_notebook():
    #global sp, np, pmath, nbprint, plt
    global sympy
    print(sympy.I)
    #from unophysics.nbtools import pmath, nbprint
    #import sympy
    #import numpy as np
    #import matplotlib.pyplot as plt
    print(dir())

# def reset_notebook_test1():
#    global sp, np, pmath, nbprint, norm, plt, ureg
#     %reset_selective -f "^((?!reset_notebook).)*$"
#     import pint
#     ureg = pint.UnitRegistry()
#     from unophysics.nbtools import pmath, nbprint
#     import sympy as sp
#     import numpy as np
#     from scipy.stats import norm
#     %matplotlib inline
#     import matplotlib.pyplot as plt
