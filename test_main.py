import main

def test_doctest():
    print('Testing docstring')

    import doctest
    doctest.testmod(main, raise_on_error=True, verbose=True, report=True)