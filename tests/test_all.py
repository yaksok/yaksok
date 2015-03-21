# using py.test

from yaksok.yaksok import run_code
from yaksok.ast_tool import transform
import ast
import os
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
    env = run_code("a:-3")
    assert env['a'] == -3

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
약속 "안녕 세계"
    "안녕 세계" 보여주기
안녕 세계
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


def test_import():
    print('''
약속 가 나 "더하기"
    결과: 가+나
약속 가 나 "빼기"
    가-나 보여주기
    결과: 가-나
''', file=open('더함.yak','w'))
    env = run_code('''
약속 나 가 "더하기"
    결과: (@더함 가 나 더하기)+4
삼: @더함 1 2 더하기
팔: 2 2 더하기
사: @더함 2 2 더하기
이: @더함 6 4 빼기
''')
    assert env['삼'] == 3
    assert env['사'] == 4
    assert env['팔'] == 8
    assert env['이'] == 2
    os.remove('더함.yak')


def test_postposition():
    env = run_code('''
약속 과일"을/를" "먹자"
    결과:과일 + " 씨앗"
사과:"사과"
감:"감"
먹은_사과:사과를 먹자
먹은_감:감을 먹자
''')
    assert env['먹은_사과'] == '사과 씨앗'
    assert env['먹은_감'] == '감 씨앗'


def test_space_in_promise_definition_with_postposition():
    env = run_code('''
약속 과일"을/를 먹자"
    결과:과일 + " 씨앗"
사과:"사과"
감:"감"
먹은_사과:사과를 먹자
먹은_감:감을 먹자
''')
    assert env['먹은_사과'] == '사과 씨앗'
    assert env['먹은_감'] == '감 씨앗'


def test_logic_op():
    env = run_code('''
a11:참 그리고 참
a10:참 그리고 거짓
a01:거짓 이고 참
a00:거짓 이고 거짓
o00:거짓 또는 거짓
o01:거짓 또는 참
o10:참 이거나 거짓
o11:참 이거나 참
''')
    assert env['a11'] == True
    assert env['a10'] == False
    assert env['a01'] == False
    assert env['a00'] == False
    assert env['o11'] == True
    assert env['o10'] == True
    assert env['o01'] == True
    assert env['o00'] == False

def test_inf_loop_continue_break():
    env = run_code('''
합:0
위치:0
반복
    위치:위치+1
    만약 위치 > 10 이면
        반복 그만
    만약 위치 % 2 = 1 이면
        반복 다시
    합:합+위치
''')
    assert env['합'] == 2+4+6+8+10
