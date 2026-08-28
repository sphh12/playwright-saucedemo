# Playwright SwagLabs (Python)

## 테스트 대상 사이트 — SwagLabs (saucedemo.com)

[SwagLabs](https://www.saucedemo.com)는 [Sauce Labs](https://saucelabs.com)가 **UI 테스트 자동화 연습용으로 공개 운영하는 데모 쇼핑몰**이다.
로그인 → 상품 목록(정렬·장바구니 담기) → 상품 상세 → 장바구니 → 3단계 체크아웃이라는 전자상거래 핵심 플로우를 갖추고 있으며,
`standard_user`(정상) 외에 `locked_out_user`(계정 잠김), `problem_user`(의도된 UI 결함), `performance_glitch_user`(의도된 지연) 등
**서로 다르게 동작하는 공개 데모 계정**을 제공해 정상/예외 시나리오를 모두 검증 연습할 수 있다. 계정 정보는 로그인 페이지에 공개돼 있다.

## 프로젝트 소개

SwagLabs 를 대상으로 한 Playwright + pytest E2E 테스트 자동화 프로젝트.
Cypress(JS) 로 작성돼 있던 SwagLabs 시나리오를 Page Object Model 기반 Python 코드로 이식했다.

- 로그인 / 인벤토리(정렬·담기) / 상품 상세 / 장바구니 / 체크아웃 / 메뉴 / 구매 풀플로우 시나리오
- 대상 서비스 정보는 `config/environments.py` + `.env` 로 주입 (기본 환경 `saucedemo`)
- GitHub Actions CI + Docker 실행 지원

## 기술 스택

| 구분        | 내용                                                     |
| ----------- | -------------------------------------------------------- |
| 테스트 러너 | pytest + pytest-playwright (Python)                      |
| 패턴        | Page Object Model (클래스 상속 + 컴포넌트 컴포지션)      |
| 설정 주입   | python-dotenv (`.env`) + `config/environments.py`        |
| 리포트      | pytest-html(`report.html`) + trace / Allure(옵션)        |
| CI          | GitHub Actions (`.github/workflows/playwright.yml`)      |
| 컨테이너    | Docker + docker-compose                                  |
| 코드 품질   | ruff (format + lint)                                     |

## 빠른 시작

> 아래는 최소 절차 요약이다. **사전 요구사항·설치 검증·환경/시크릿 관리·Docker 대체 경로**까지 포함한
> 전체 세팅 절차는 통합 가이드 **[`docs/setup-guide.md`](docs/setup-guide.md)** 를 따른다.

```bash
# 1. 가상환경 생성 + 활성화 (Python 3.9+)
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 2. 의존성 설치 (개발 도구 포함)
pip install -e ".[dev]"

# 3. 브라우저 설치 (최초 1회)
playwright install chromium

# 4. 환경 파일 생성 — 필요한 값만 주석 해제 (기본값만으로도 동작함)
#    Windows: Copy-Item .env.example .env
cp .env.example .env

# 5. 테스트 실행 (saucedemo.com 대상)
pytest
```

### `.example` 파일 규칙

| 커밋되는 파일  | 복사해서 만들 파일 | 필수 여부                       |
| -------------- | ------------------ | ------------------------------- |
| `.env.example` | `.env`             | 선택 (기본값으로도 동작함)      |

⚠️ 실계정/시크릿은 `.env` 에만 넣는다. `.env`, `.auth/` 는 gitignore 대상이며 **절대 커밋 금지**.
(saucedemo 는 공개 데모 계정이라 코드 기본값을 허용한다.)

## 실행 명령어

`make <타깃>` 단축 명령을 제공한다 (내부적으로는 아래 `pytest`/`ruff` 명령을 실행).

| make 타깃            | 실제 명령                          | 설명                                          |
| -------------------- | ---------------------------------- | --------------------------------------------- |
| `make test`          | `pytest -n auto`                   | 전체 테스트 (병렬)                            |
| `make test-smoke`    | `pytest -m smoke`                  | 스모크 마커만 실행                            |
| `make test-e2e`      | `pytest -m e2e`                    | e2e 마커만 실행 (핵심 흐름)                   |
| `make test-headed`   | `pytest --headed`                  | 브라우저 화면을 보면서 실행                   |
| `make test-debug`    | `PWDEBUG=1 pytest -s`              | 인스펙터 디버그 모드                          |
| `make repeat`        | `pytest --count=3`                 | 3회 반복 (플레이키 탐지 — pytest-repeat)      |
| `make report`        | `reports/report.html` 열기         | 마지막 HTML 리포트                            |
| `make codegen`       | `playwright codegen`               | 코드 자동 생성기 (브라우저 조작 → 코드)       |
| `make format`        | `ruff format .`                    | 코드 포맷                                     |
| `make lint`          | `ruff check .`                     | 정적 검사                                     |
| `make docker-test`   | `docker compose run --rm test`     | Docker 컨테이너에서 전체 테스트               |
| `make allure`        | `allure generate ...`              | Allure 리포트 생성 (옵션 — `docs/allure-guide.md`) |

> `make` 없이 직접 실행할 때는 위 "실제 명령" 열을 그대로 쓰면 된다. (가상환경 활성화 상태 기준)

## 프로젝트 구조

```
playwright-saucedemo/
├── pyproject.toml              # 의존성 + pytest 설정(마커/addopts) + ruff 설정
├── Makefile                    # 실행 단축 명령
├── conftest.py                 # 루트: base_url/공통 컨텍스트 옵션 + 실패 시 콘솔 로그 첨부 + Allure 토글
├── config/
│   └── environments.py         # 환경 정의 맵 — TEST_ENV/.env 로 대상 환경 선택 (기본 saucedemo)
├── src/
│   ├── pages/                  # base_page + login/inventory/product_detail/cart/checkout 페이지 객체
│   ├── components/             # header_component (버거메뉴·장바구니 등 공유 UI)
│   └── data/                   # test_data — 계정/상품/에러 메시지 등 테스트 데이터 단일 관리
├── tests/
│   ├── conftest.py             # 페이지 객체 fixture + 로그인 세션 재사용 + data-test 속성
│   └── test_*.py               # login/inventory/product_detail/cart/checkout/menu/purchase/smoke
├── docs/                       # 상세 가이드 문서 (아래 인덱스)
├── .github/workflows/          # CI (push/PR 시 자동 실행 + 리포트 아티팩트)
├── Dockerfile / docker-compose.yml / .dockerignore
├── CLAUDE.md / GIT_RULES.md    # AI 작업 규칙 / git 규칙
├── .editorconfig / .gitattributes
└── .env.example                # 환경 변수 템플릿
```

## 핵심 설계 요약

- **BasePage 계약**: 각 페이지는 `path`(상대 경로)와 `ready_locator()`(로드 판단 기준)만 정의하면
  `goto()` / `expect_loaded()` 를 물려받는다. Playwright 자동 대기 덕분에 wait 헬퍼는 최소화했다.
- **fixture 주입 POM**: 싱글턴 export 대신, 페이지 객체를 conftest fixture 로 주입한다.
  테스트 함수 파라미터에 적기만 하면 생성/연결이 자동으로 된다. → `docs/pom-guide.md`
- **인증 1회 + 세션 재사용**: `sauce_storage_state` fixture 가 로그인 후 `storage_state` 를 저장하고,
  이후 모든 테스트는 로그인 없이 시작한다 (로그인 테스트만 개별 해제).
- **실패 시에만 산출물 저장**: trace / screenshot / video / 콘솔 로그 모두 실패한 테스트에만 남는다.

## 문서

| 문서                        | 내용                                         |
| --------------------------- | -------------------------------------------- |
| `docs/pom-guide.md`         | POM 설계 가이드 (Cypress/JS 방식과의 차이 포함) |
| `docs/setup-guide.md`       | 환경 세팅 통합 가이드 (설치·검증·환경/시크릿 관리) |
| `docs/ci-guide.md`          | GitHub Actions CI 가이드 및 확장 방법        |
| `docs/docker-guide.md`      | Docker 실행 가이드                           |
| `docs/allure-guide.md`      | Allure 리포트 사용법 (옵션)                  |
| `docs/troubleshooting.md`   | 자주 겪는 문제 해결                          |
