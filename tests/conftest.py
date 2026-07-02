"""tests 공통 conftest — data-test 속성 지정 + 로그인 세션 재사용 + 페이지 객체 fixture 주입.

템플릿 examples/sauce_demo/conftest.py 패턴을 tests/ 상위로 승격한 것:
- _set_test_id_attribute : get_by_test_id() 가 data-test 속성을 읽도록 전역 설정 (teardown 복원)
- sauce_storage_state    : standard_user 로 1회 로그인 → 세션을 파일로 저장 후 경로 반환
- browser_context_args   : 루트 override 를 상속하고 저장 세션(storage_state) 주입
- 페이지 객체 fixture    : 테스트 파라미터로 필요한 페이지 객체만 지연 생성
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from pathlib import Path

import pytest
from playwright.sync_api import Browser, Page, Playwright, expect

from src.data.test_data import STANDARD_USER
from src.pages.cart_page import CartPage
from src.pages.checkout_complete_page import CheckoutCompletePage
from src.pages.checkout_info_page import CheckoutInfoPage
from src.pages.checkout_overview_page import CheckoutOverviewPage
from src.pages.inventory_page import InventoryPage
from src.pages.login_page import LoginPage
from src.pages.product_detail_page import ProductDetailPage

# 로그인 세션 저장 위치 (.auth/ 는 gitignore 대상 — 세션 파일은 절대 커밋 금지)
AUTH_FILE = Path(".auth/sauce_demo.json")


@pytest.fixture(scope="session", autouse=True)
def _set_test_id_attribute(playwright: Playwright) -> Iterator[None]:
    # saucedemo 는 data-test 속성을 제공 → get_by_test_id() 가 data-test 를 읽도록 지정한다.
    # (Python 은 전역 설정이라 teardown 에서 기본값 data-testid 로 복원)
    playwright.selectors.set_test_id_attribute("data-test")
    yield
    playwright.selectors.set_test_id_attribute("data-testid")


@pytest.fixture(scope="session")
def sauce_storage_state(browser: Browser, base_url: str, _set_test_id_attribute: None) -> str | None:
    """로그인 1회 → 세션을 파일로 저장하고 경로를 반환한다.

    이후 모든 테스트는 저장된 세션(storage_state)으로 시작하므로 로그인을 반복하지 않는다.
    (로그인 자체를 검증하는 test_login.py 는 이 fixture 를 None 으로 오버라이드해 빈 세션으로 시작)
    """
    AUTH_FILE.parent.mkdir(parents=True, exist_ok=True)
    context = browser.new_context(base_url=base_url)
    page = context.new_page()

    login_page = LoginPage(page)
    login_page.goto()
    login_page.login(STANDARD_USER.username, STANDARD_USER.password)

    # 로그인 성공 = 상품 목록 페이지 도착 (고정 대기 없이 URL 폴링)
    expect(page).to_have_url(re.compile(r"inventory\.html"))

    context.storage_state(path=str(AUTH_FILE))
    context.close()
    print(f"[sauce_storage_state] 로그인 세션 저장 완료 → {AUTH_FILE}")  # 디버깅용
    return str(AUTH_FILE)


@pytest.fixture
def browser_context_args(browser_context_args: dict, sauce_storage_state: str | None) -> dict:
    # 매 테스트 로그인 반복 대신 저장된 세션으로 시작. (base_url/locale/timezone 은 루트 conftest 에서 상속)
    args = dict(browser_context_args)
    if sauce_storage_state:
        args["storage_state"] = sauce_storage_state
    return args


# ── 페이지 객체 fixture 주입 ──
# 테스트 파라미터에 적으면 필요한 페이지 객체만 생성된다. (지연 생성 + page 자동 연결)
@pytest.fixture
def login_page(page: Page) -> LoginPage:
    return LoginPage(page)


@pytest.fixture
def inventory_page(page: Page) -> InventoryPage:
    return InventoryPage(page)


@pytest.fixture
def product_detail_page(page: Page) -> ProductDetailPage:
    return ProductDetailPage(page)


@pytest.fixture
def cart_page(page: Page) -> CartPage:
    return CartPage(page)


@pytest.fixture
def checkout_info_page(page: Page) -> CheckoutInfoPage:
    return CheckoutInfoPage(page)


@pytest.fixture
def checkout_overview_page(page: Page) -> CheckoutOverviewPage:
    return CheckoutOverviewPage(page)


@pytest.fixture
def checkout_complete_page(page: Page) -> CheckoutCompletePage:
    return CheckoutCompletePage(page)
