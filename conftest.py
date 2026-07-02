"""루트 conftest — 모든 테스트가 공유하는 fixture / 훅.

JS 템플릿(playwright.config.ts + src/fixtures/test.ts)의 다음을 pytest-playwright 로 옮긴 것:
- use.locale / timezoneId          → browser_context_args 오버라이드
- use.trace/screenshot/video       → pyproject.toml 의 addopts (--tracing/--screenshot/--video)
- expect.timeout                   → expect.set_options(timeout=...)
- reporter(html) / Allure(옵션)    → pytest-html(addopts) + ALLURE=true 시 allure-results 활성화
- src/fixtures/test.ts 의 consoleLogs auto fixture → capture_console autouse fixture
"""

from __future__ import annotations

import os

import pytest
from playwright.sync_api import Page, expect

from config.environments import current_env

# expect 단건 검증 최대 대기(=JS expect.timeout 10s). 구버전엔 set_options 가 없을 수 있어 방어적으로 처리.
try:
    expect.set_options(timeout=10_000)
except AttributeError:  # pragma: no cover - 구버전 playwright 호환
    pass


def pytest_configure(config: pytest.Config) -> None:
    """Allure 리포트는 옵션 — .env 의 ALLURE=true 로 켠다 (docs/allure-guide.md 참고).

    allure-pytest 플러그인은 --alluredir 값을 config.option.allure_report_dir 로 읽는다.
    """
    if os.environ.get("ALLURE") == "true" and config.pluginmanager.hasplugin("allure_pytest"):
        if not getattr(config.option, "allure_report_dir", None):
            config.option.allure_report_dir = "allure-results"


@pytest.fixture(scope="session")
def base_url(request: pytest.FixtureRequest) -> str:
    """pytest-playwright 가 컨텍스트 base_url 로 사용하는 값.

    --base-url 로 넘기면 그 값을, 아니면 config/environments.py 의 현재 환경 base_url 을 쓴다.
    (페이지 객체의 goto()가 상대 경로로 동작하도록 base_url 을 주입 — docs/pom-guide.md 참고)
    """
    return request.config.getoption("--base-url") or current_env.base_url


@pytest.fixture
def browser_context_args(browser_context_args: dict, base_url: str) -> dict:
    """모든 컨텍스트 공통 옵션 — 한국 서비스 테스트 기본값 (대상 서비스에 따라 조정/제거).

    base_url 을 여기서 노드별로 명시 설정하는 이유:
      pytest-playwright 의 browser_context_args 는 session 스코프라 "첫 테스트"의 base_url 이
      세션 전체에 캐시된다. 그대로 두면 (환경/디렉터리마다 base_url 이 다른) 테스트가
      엉뚱한 base_url 로 실행되므로, 함수 스코프인 이 오버라이드에서 매 테스트 base_url 을 덮어쓴다.
    """
    return {
        **browser_context_args,
        "base_url": base_url,
        "locale": "ko-KR",
        "timezone_id": "Asia/Seoul",
    }


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo):
    # 각 단계(setup/call/teardown) 결과를 item 에 저장 → fixture teardown 에서 성공/실패 판단에 쓴다.
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)


@pytest.fixture(autouse=True)
def capture_console(page: Page, request: pytest.FixtureRequest):
    """브라우저 콘솔/페이지 에러를 수집했다가 "테스트가 실패했을 때만" 리포트에 남긴다.

    autouse 라서 각 테스트에서 따로 호출할 필요가 없다. (JS 의 consoleLogs auto fixture 대응)
    → 실패 원인 분석 시 스크린샷/트레이스와 함께 콘솔 로그까지 한 번에 확인 가능.
    """
    logs: list[str] = []
    page.on("console", lambda msg: logs.append(f"[{msg.type}] {msg.text}"))
    page.on("pageerror", lambda err: logs.append(f"[pageerror] {err.message}"))

    yield

    # 예상과 다르게 끝났을 때(실패/에러)만 첨부
    rep_call = getattr(request.node, "rep_call", None)
    if rep_call is not None and rep_call.failed and logs:
        body = "\n".join(logs)
        print(f"\n[console-logs]\n{body}")  # 실패 시 캡처된 로그가 pytest 출력에 표시된다(디버깅용)
        if os.environ.get("ALLURE") == "true":
            try:  # allure 활성 시에만 리포트에 첨부
                import allure

                allure.attach(body, name="console-logs", attachment_type=allure.attachment_type.TEXT)
            except Exception:  # pragma: no cover - allure 미설치/미활성 시 무시
                pass
