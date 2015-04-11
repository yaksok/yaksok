약속 프로그래밍 언어
====================

[약속 언어](http://yaksok.org)는 쉬운 한글 프로그래밍 언어로
누구나 쉽게 배울 수 있습니다.
약속은 배우고 쓰기 쉬운 교육용 언어이면서, 동시에
상용 소프트웨어, 웹 애플리케이션, 게임, 스마트폰 앱까지 전부 만들 수 있습니다.

약속을 이용해 비만도(BMI)를 계산하여 보여주는 예제 코드는 다음과 같습니다:

<pre>
<strong>약속</strong> &quot;키&quot; 키 &quot;몸무게&quot; 몸무게&quot;의 비만도&quot;
    <strong>결과</strong>: 몸무게 / 키 / 키

비만도: 키 1.77 몸무게 68의 비만도
비만도 보여주기
</pre>

좀더 자세한 소개는 [홈페이지](http://yaksok.org)를 참고해 주세요.

기능
----

- 자연스러운 한국어 표현으로 프로그래밍을 할 수 있습니다.
- 한국어 어순을 존중한 약속(함수) 정의 가능
- 앱이나 웹으로 [간단한 게임](http://yaksok.github.io/2048/)을 만들 수 있습니다. 

설치하기
--------

(윈도우용 설치 파일을 차후 제공할 예정입니다.)

현재는 약속을 사용하려면 python 3가 필요합니다.

다음을 실행하여 설치할 수 있습니다:

    git clone http://github.com/yaksok/yaksok
    cd yaksok
    python setup.py install
    
(시스템에 따라 python 대신 python3를 사용해야할 수도 있습니다.)

.yak 파일을 작성 후 아래와 같이 실행할 수 있습니다:

    yaksok 파일이름.yak

설치하지 않고 테스트만 할 수도 있습니다.

    python -m yaksok code_examples/hello.yak

약속 개발에 기여하기
--------------------

- 소스 코드: github.com/yaksok/yaksok
- 이슈 관리: github.com/yaksok/yaksok/issues

