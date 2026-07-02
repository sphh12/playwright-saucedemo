"""버거 메뉴(사이드바) 테스트 — 저장된 로그인 세션으로 시작한다.

- 로그아웃 시 로그인 화면으로 복귀하는지 검증한다.
- 앱 상태 초기화(Reset App State) 시 장바구니 배지가 사라지는지 검증한다.
"""

from __future__ import annotations

import re

import pytest
from playwright.sync_api import expect

from src.pages.inventory_page import InventoryPage
from src.pages.login_page import LoginPage


@pytest.fixture(autouse=True)
def _open_inventory(inventory_page: InventoryPage) -> None:
    # 저장된 로그인 세션으로 시작하므로 바로 상품 목록에 접근할 수 있다.
    inventory_page.goto()


@pytest.mark.e2e
def test_logout_returns_to_login(inventory_page: InventoryPage, login_page: LoginPage) -> None:
    """로그아웃하면 로그인 화면으로 돌아간다."""
    inventory_page.logout()

    # URL 이 로그인 화면(루트 또는 index.html)으로 돌아왔는지 정규식으로 검증한다.
    expect(inventory_page.page).to_have_url(re.compile(r"saucedemo\.com/?(index\.html)?$"))
    # 로그인 버튼이 다시 보이면 로그인 화면으로 확실히 복귀한 것이다.
    expect(login_page.login_button).to_be_visible()


@pytest.mark.e2e
def test_reset_app_state_clears_badge(inventory_page: InventoryPage) -> None:
    """앱 상태 초기화를 하면 장바구니 배지가 사라진다."""
    # 담기 → 배지 1 확인 (add_item_to_cart 는 이름이 아니라 slug 를 받는다)
    inventory_page.add_item_to_cart("sauce-labs-backpack")
    inventory_page.expect_cart_badge_count(1)

    # 초기화 → 배지가 사라져 개수 0 이 되는지만 검증한다.
    # (주의: reset 후에도 담기 버튼 상태는 서비스 버그로 남을 수 있으므로 배지만 검증)
    inventory_page.reset_app_state()
    inventory_page.expect_cart_badge_count(0)
