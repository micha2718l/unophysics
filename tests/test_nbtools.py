from unophysics import nbtools

def test_pmath(capsys):
    nbtools.pmath(2)
    out, err = capsys.readouterr()
    assert out == '<IPython.core.display.Markdown object>\n', "Should be Markdown object"

def test_pmath_return(capsys):
    ret = nbtools.pmath(2, ret=True)
    assert ret == '$2$', 'Should be "$2$"'

def test_pmath_return_all_args(capsys):
    ret = nbtools.pmath(2, pre='Two: ', preM='t=', postM='a', post=' not three.', ret=True)
    assert ret == 'Two: $t=2a$ not three.', 'Should be "Two: $t=2a$ not three."'
