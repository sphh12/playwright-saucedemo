"""로그인 테스트 — "로그인 자체"를 검증하므로 저장 세션을 쓰지 않고 빈 상태로 시작한다.

cypress saucedemo/login.cy.js 전 케이스를 이식했다.
에러 메시지에는 "Epic sadface:" 접두사가 붙으므로 반드시 부분매칭(to_contain_text)으로 검증한다.
"""

from __future__ import annotations

import re

import pytest
from playwright.sync_api import Page, expect

from src.data.test_data import (
    ERR_CREDENTIALS_MISMATCH,
    ERR_LOCKED,
    ERR_PASSWORD_REQUIRED,
    ERR_USERNAME_REQUIRED,
    LOCKED_OUT_USER,
    PASSWORD,
    STANDARD_USER,
)
from src.pages.login_page import LoginPage


@pytest.fixture
def sauce_storage_state() -> None:
    # 이 파일은 로그인 흐름을 검증하므로, 프로젝트 저장 세션을 쓰지 않고 빈 상태(fresh)로 시작한다.
    # (conftest 의 session fixture 를 None 으로 오버라이드 → browser_context_args 가 storage_state 제외)
    return None


@pytest.fixture(autouse=True)
def _open_login(login_page: LoginPage) -> None:
    # 각 테스트 전에 로그인 페이지로 이동 (cypress beforeEach / LoginPage.open() 대응)
    login_page.goto()


@pytest.mark.e2e
def test_standard_user_login_success(login_page: LoginPage, page: Page) -> None:
    """standard_user 로 정상 로그인하면 인벤토리로 진입한다."""
    login_page.login(STANDARD_USER.username, STANDARD_USER.password)
    # 로그인 성공 = 상품 목록(inventory.html) 도착
    expect(page).to_have_url(re.compile(r"inventory\.html"))


@pytest.mark.e2e
def test_locked_out_user_shows_error(login_page: LoginPage) -> None:
    """잠긴 계정(locked_out_user)으로 로그인하면 차단 에러가 표시된다."""
    login_page.login(LOCKED_OUT_USER.username, LOCKED_OUT_USER.password)
    # 접두사("Epic sadface: ")가 있으므로 부분매칭으로 검증
    expect(login_page.error_message).to_contain_text(ERR_LOCKED)


@pytest.mark.e2e
def test_empty_username_shows_error(login_page: LoginPage) -> None:
    """아이디를 비우고 로그인하면 아이디 필수 에러가 표시된다."""
    login_page.login("", PASSWORD)
    expect(login_page.error_message).to_contain_text(ERR_USERNAME_REQUIRED)


@pytest.mark.e2e
def test_empty_password_shows_error(login_page: LoginPage) -> None:
    """비밀번호를 비우고 로그인하면 비밀번호 필수 에러가 표시된다."""
    login_page.login(STANDARD_USER.username, "")
    expect(login_page.error_message).to_contain_text(ERR_PASSWORD_REQUIRED)


@pytest.mark.e2e
def test_wrong_password_shows_error(login_page: LoginPage) -> None:
    """잘못된 비밀번호로 로그인하면 불일치 에러가 표시된다."""
    login_page.login(STANDARD_USER.username, "wrong_password")
    expect(login_page.error_message).to_contain_text(ERR_CREDENTIALS_MISMATCH)
