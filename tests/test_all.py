# using py.test

from yaksok.yaksok import run_code

def test_assign():
    env = run_code("a:3")
    assert env['a'] == 3
