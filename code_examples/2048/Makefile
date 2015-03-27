all:game.py draw.py
game.py:게임.yak
	../../convert2py 게임.yak > game.py
draw.py:화면.yak
	../../convert2py 화면.yak > draw.py
run: all
	python3 main.py
