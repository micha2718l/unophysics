
import sympy
from IPython.display import Latex, Markdown, display

__all__ = ['pmath', 'nbprint']

def nbprint(string):
    display(Markdown(string))

lt = sympy.latex
sympy.init_printing()
def pmath(sym, ret=False):
    output = f'${lt(sym)}$'
    if ret:
        return output
    nbprint(output)
