# using py.test

from yaksok.yaksok import run_code
from yaksok.ast_tool import transform
import ast
import logging
logging.basicConfig(level=logging.DEBUG)

class TestASTTool:
    def test_nothing(self):
        tree = transform('a=3', {})
        env = {}
        exec(compile(tree, '<string>', 'exec'), env)
        assert env['a'] == 3

    def test_number(self):
        tree = transform('a=<:number:>', dict(number=ast.Num(3)))
        env = {}
        exec(compile(tree, '<string>', 'exec'), env)
        assert env['a'] == 3

def test_assign():
    env = run_code("a:3")
    assert env['a'] == 3

def test_define_function():
    run_code('''
약속 "안녕세계"
    "안녕세계" 보여주기
''')

#약속 무언가 "두번 보여주기"
    #무언가 보여주기
    #무언가 보여주기
