# 실행 단축 명령 — JS 템플릿의 package.json scripts 대응.
# 사용법: make test / make test-smoke / make report ...
# (가상환경을 활성화한 상태에서 실행하거나, PY=.venv/bin/python 처럼 인터프리터를 지정)

PY ?= python

.PHONY: install browsers test test-smoke test-e2e test-headed test-debug \
        repeat report codegen format lint allure allure-open docker-test

install:            ## 의존성 설치 (개발 도구 포함)
	$(PY) -m pip install -e ".[dev]"

browsers:           ## Playwright 브라우저 설치 (최초 1회)
	$(PY) -m playwright install chromium

test:               ## 전체 테스트 (병렬)
	$(PY) -m pytest -n auto

test-smoke:         ## 스모크 마커만 실행
	$(PY) -m pytest -m smoke

test-e2e:           ## e2e 마커만 실행 (핵심 흐름 엔드투엔드)
	$(PY) -m pytest -m e2e

test-headed:        ## 브라우저 화면을 보면서 실행
	$(PY) -m pytest --headed

test-debug:         ## 단계별 디버그 (PWDEBUG 인스펙터)
	PWDEBUG=1 $(PY) -m pytest -s

repeat:             ## 3회 반복 실행 (플레이키/불안정 테스트 탐지 — pytest-repeat)
	$(PY) -m pytest --count=3

report:             ## 마지막 HTML 리포트 열기 (reports/report.html)
	$(PY) -c "import webbrowser, pathlib; webbrowser.open(pathlib.Path('reports/report.html').resolve().as_uri())"

codegen:            ## 코드 자동 생성기 (브라우저 조작 → 코드)
	$(PY) -m playwright codegen

format:             ## 코드 포맷 (ruff format)
	$(PY) -m ruff format .

lint:               ## 정적 검사 (ruff check)
	$(PY) -m ruff check .

allure:             ## Allure 결과 생성 후 리포트 생성 (ALLURE=true 로 테스트 실행 필요)
	allure generate allure-results --clean -o allure-report

allure-open:        ## Allure 리포트 열기
	allure open allure-report

docker-test:        ## Docker 컨테이너에서 전체 테스트
	docker compose run --rm test
