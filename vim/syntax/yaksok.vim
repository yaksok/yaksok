" Vim syntax file
" Language: Yaksok
" Maintainer: Jaeseung Ha
" Latest Revision: 7 March 2015

if exists("b:current_syntax")
  finish
endif

syn keyword ysFun 약속 번역 
syn keyword ysStmt 만약 끝 이면 아니면
syn keyword ysBoolean 참 거짓
syn keyword ysLoopMada 마다 의 반복
syn match ysAssign "[:]"
syn match ysOperator "[\+\-\*/\~=]"
syn region ysLoop start=+반복+ end=+마다+ contains=ysLoopMada transparent
syn region ysString   start=+"+  skip=+\\\\\|\\"+  end=+"+
syn region  ysComment	start="#" skip="\\$" end="$" keepend
  syn match   ysNumber	"\<\%([1-9]\d*\|0\)\>"
  syn match   ysNumber
	\ "\<\d\+\.\%([eE][+-]\=\d\+\)\=[jJ]\=\%(\W\|$\)\@="
syn keyword ysShow 보여주기

"hi def link celTodo        Todo
hi def link ysComment       Comment
hi def link ysStmt          Keyword
hi def link ysLoop          Keyword
hi def link ysLoopMada      Keyword
hi def link ysFun           Keyword
hi def link ysAssign        Statement
hi def link ysString      String
hi def link ysNumber      Number
hi def link ysBoolean      Boolean
hi def link ysOperator      Operator
hi def link ysShow          Function
"hi def link ysConst       Constant
"hi def link celDesc        PreProc
