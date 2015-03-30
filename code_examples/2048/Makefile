all:game.py draw.py
game.py:게임.yak
	../../convert2py 게임.yak > game.py
	../../convert2js 게임.yak > game.js
draw.py:화면.yak
	../../convert2py 화면.yak > draw.py
	../../convert2js 화면.yak > draw.js
run: all
	python3 main.py
