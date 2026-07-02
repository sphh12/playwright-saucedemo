"""스모크 테스트 — saucedemo 첫 진입이 정상 동작하는지 최소 검증.

이 파일은 로그인 이전의 진입 자체를 검증하므로, 프로젝트 저장 세션을 쓰지 않고
빈(fresh) 세션으로 시작한다. (conftest 의 sauce_storage_state 를 None 으로 오버라이드)
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from src.pages.login_page import LoginPage


@pytest.fixture
def sauce_storage_state() -> None:
    # 저장 세션 미사용: session fixture 를 None 으로 오버라이드 → browser_context_args 가 storage_state 제외
    return None


@pytest.mark.smoke
def test_saucedemo_loads(page: Page, login_page: LoginPage) -> None:
    """saucedemo 홈이 로드되면 타이틀이 "Swag Labs" 이고 로그인 버튼이 보인다 (@smoke)."""
    print("[test_smoke] saucedemo 홈 진입 검증 시작")  # 디버깅용
    page.goto("/")

    # 브라우저 탭 타이틀 확인 (실측: "Swag Labs")
    expect(page).to_have_title("Swag Labs")

    # 로그인 폼 진입 확인 — login-button 가시성으로 판정
    expect(login_page.login_button).to_be_visible()
