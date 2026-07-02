# CLAUDE.md — 이 프로젝트에서의 AI 작업 규칙

## 프로젝트 개요

[saucedemo.com](https://www.saucedemo.com) (SwagLabs) 대상 Playwright + pytest E2E 테스트 자동화 프로젝트.
Cypress(JS) SwagLabs 시나리오를 Page Object Model 기반 Python 코드로 이식했다. 구조 설명은 `README.md` 참고.

## 작업 규칙

- 코드 주석과 문서는 **한국어**, 변수/함수/클래스명은 **영어**로 작성한다.
- 모든 `.py` 파일 상단에 `from __future__ import annotations` 를 둔다. 전면 타입힌트를 사용한다.
- 새 페이지 객체는 반드시 `src/pages/base_page.py` 의 `BasePage` 를 상속하고, `path` 와 `ready_locator()` 를 정의한다.
- 로케이터는 생성자에서 선언한다. testId 속성은 `data-test` (`get_by_test_id`) 이며, id 셀렉터만 있는 요소는 `page.locator("#...")` 를 쓴다.
- 테스트는 페이지 객체를 직접 생성하지 않고 `tests/conftest.py` 의 fixture 로 주입받는다.
- 고정 대기(`page.wait_for_timeout`) 금지 — 로케이터 자동 대기와 `expect(...)` / `page.wait_for_function` 을 사용한다.
- 시크릿/실계정은 코드에 하드코딩하지 않고 `.env` 로 주입한다. (`config/environments.py` 참고, saucedemo 공개 데모 계정만 예외)
- 디버깅용 `print("[ClassName] ...")` 는 의도적으로 포함하되, **비밀번호는 절대 로그에 남기지 않는다**.

## 검증 명령

| 명령                          | 용도                        |
| ----------------------------- | --------------------------- |
| `ruff check .`                | 정적 검사(린트)             |
| `ruff format --check .`       | 포맷 확인                   |
| `pytest tests`                | 전체 테스트 (실서비스 대상) |

코드 변경 후에는 최소한 `ruff check .` 와 관련 테스트를 실행해 확인한다.

## 푸시 전 필수 확인

`GIT_RULES.md` 의 민감정보 스캔 체크리스트를 수행한다. `.env`, `.auth/` 는 절대 커밋 금지.
