"""기본 구매 해피패스 E2E — 담기부터 주문 완료까지 페이지 객체들을 이어 검증한다.

- 저장된 로그인 세션(sauce_storage_state)으로 시작하며 autouse 로 상품 목록을 연다.
- 원본 Cypress purchase.basic.cy.js 시나리오를 이식.
"""

from __future__ import annotations

import re

import pytest
from playwright.sync_api import Page, expect

from src.data.test_data import CUSTOMER
from src.pages.cart_page import CartPage
from src.pages.checkout_complete_page import CheckoutCompletePage
from src.pages.checkout_info_page import CheckoutInfoPage
from src.pages.checkout_overview_page import CheckoutOverviewPage
from src.pages.inventory_page import InventoryPage

# 대상 상품 (slug/name) — Cypress 원본과 동일
PRODUCT_SLUG = "sauce-labs-backpack"
PRODUCT_NAME = "Sauce Labs Backpack"


@pytest.fixture(autouse=True)
def _open_inventory(inventory_page: InventoryPage) -> None:
    # 저장된 로그인 세션으로 시작하므로 바로 상품 목록에 접근할 수 있다.
    inventory_page.goto()


@pytest.mark.e2e
def test_basic_purchase_happy_path(
    page: Page,
    inventory_page: InventoryPage,
    cart_page: CartPage,
    checkout_info_page: CheckoutInfoPage,
    checkout_overview_page: CheckoutOverviewPage,
    checkout_complete_page: CheckoutCompletePage,
) -> None:
    """상품 담기 → 배송정보 입력 → 주문 완료 (@e2e)."""
    # 1. 상품 목록에서 담기 → 배지 1
    inventory_page.add_item_to_cart(PRODUCT_SLUG)
    inventory_page.expect_cart_badge_count(1)

    # 2. 장바구니 진입: 이름 포함 + 개수 1
    inventory_page.open_cart()
    cart_page.expect_loaded()
    expect(cart_page.items).to_have_count(1)
    expect(cart_page.item_names).to_contain_text([PRODUCT_NAME])

    # 3. 체크아웃 → 배송 정보 입력 → 다음 단계
    cart_page.checkout()
    checkout_info_page.expect_loaded()
    checkout_info_page.fill_customer_info(CUSTOMER)
    checkout_info_page.submit()

    # 4. 주문 확인(overview): 이름 포함 + 총액 일관성
    checkout_overview_page.expect_loaded()
    expect(page).to_have_url(re.compile("checkout-step-two.html"))
    expect(checkout_overview_page.item_names).to_contain_text([PRODUCT_NAME])
    checkout_overview_page.expect_totals_consistent()

    # 5. 주문 완료 확인
    checkout_overview_page.finish()
    checkout_complete_page.expect_loaded()
    expect(page).to_have_url(re.compile("checkout-complete.html"))
    checkout_complete_page.expect_order_complete()
