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

def test_pass():
    run_code('''
패스
만약 1 이면
    패스
''')

def test_define_function():
    run_code('''
약속 "안녕세계"
    "안녕세계" 보여주기
안녕세계
''')

def test_add_function():
    env = run_code('''
약속 가"와" 나 "더하기"
    가+나 보여주기
    결과: 가+나
2 와 3 더하기
2와 3 더하기
무언가:12와 27 더하기
뭔가:무언가 와 11 더하기
그것: 뭔가와 77 더하기
''')
    assert env['무언가'] == 12+27
    assert env['뭔가'] == 12+27+11
    assert env['그것'] == 12+27+11+77


def test_translate():
    env = run_code('''
번역(python) x "뒤에" y "추가" 
***
    x.append(y)
***

리스트: []
리스트 뒤에 5 추가
''')
    assert env['리스트'] == [5]
