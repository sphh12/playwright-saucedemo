"""체크아웃 테스트 — 저장된 로그인 세션으로 시작한다 (sauce_storage_state 참고).

- 필수 입력(이름/성/우편번호) 누락 시 에러 메시지(접두사 있음 → 부분매칭) 검증.
- 취소 시 장바구니 복귀 검증.
- 다중 상품 풀 체크아웃 완료(@e2e): 주문 확인 → 총액 일관성 → 주문 완료.
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


@pytest.fixture(autouse=True)
def _open_inventory(inventory_page: InventoryPage) -> None:
    # 저장된 로그인 세션으로 시작하므로 바로 상품 목록에 접근할 수 있다.
    inventory_page.goto()


def go_to_checkout_info(
    slug: str,
    inventory_page: InventoryPage,
    cart_page: CartPage,
    checkout_info_page: CheckoutInfoPage,
) -> None:
    """상품 담기 → 장바구니 → 체크아웃 → 배송정보 화면 진입까지의 공통 진입 흐름."""
    print(f"[test_checkout] go_to_checkout_info(slug={slug})")  # 디버깅용
    inventory_page.add_item_to_cart(slug)
    inventory_page.open_cart()
    cart_page.expect_loaded()
    cart_page.checkout()
    checkout_info_page.expect_loaded()


def test_empty_first_name_error(
    inventory_page: InventoryPage,
    cart_page: CartPage,
    checkout_info_page: CheckoutInfoPage,
) -> None:
    """이름을 비우면 이름 필수 에러가 표시된다 (부분매칭)."""
    go_to_checkout_info("sauce-labs-backpack", inventory_page, cart_page, checkout_info_page)
    checkout_info_page.fill_shipping_info("", "Hong", "12345")
    checkout_info_page.submit()
    # 실제 텍스트는 "Error: First Name is required" → 접두사 때문에 부분매칭 사용
    expect(checkout_info_page.error_message).to_contain_text("First Name is required")


def test_empty_last_name_error(
    inventory_page: InventoryPage,
    cart_page: CartPage,
    checkout_info_page: CheckoutInfoPage,
) -> None:
    """성을 비우면 성 필수 에러가 표시된다 (부분매칭)."""
    go_to_checkout_info("sauce-labs-backpack", inventory_page, cart_page, checkout_info_page)
    checkout_info_page.fill_shipping_info("Gildong", "", "12345")
    checkout_info_page.submit()
    expect(checkout_info_page.error_message).to_contain_text("Last Name is required")


def test_empty_postal_code_error(
    inventory_page: InventoryPage,
    cart_page: CartPage,
    checkout_info_page: CheckoutInfoPage,
) -> None:
    """우편번호를 비우면 우편번호 필수 에러가 표시된다 (부분매칭)."""
    go_to_checkout_info("sauce-labs-backpack", inventory_page, cart_page, checkout_info_page)
    checkout_info_page.fill_shipping_info("Gildong", "Hong", "")
    checkout_info_page.submit()
    expect(checkout_info_page.error_message).to_contain_text("Postal Code is required")


def test_cancel_returns_to_cart(
    page: Page,
    inventory_page: InventoryPage,
    cart_page: CartPage,
    checkout_info_page: CheckoutInfoPage,
) -> None:
    """취소를 누르면 장바구니로 돌아간다."""
    go_to_checkout_info("sauce-labs-backpack", inventory_page, cart_page, checkout_info_page)
    checkout_info_page.cancel()
    expect(page).to_have_url(re.compile(r"cart\.html"))
    cart_page.expect_loaded()


@pytest.mark.e2e
def test_multi_item_full_checkout_completes(
    page: Page,
    inventory_page: InventoryPage,
    cart_page: CartPage,
    checkout_info_page: CheckoutInfoPage,
    checkout_overview_page: CheckoutOverviewPage,
    checkout_complete_page: CheckoutCompletePage,
) -> None:
    """여러 상품을 담아 배송정보 입력 후 주문을 완료한다 (@e2e)."""
    # 1. 다중 상품 담기 → 장바구니 → 체크아웃
    inventory_page.add_item_to_cart("sauce-labs-backpack")
    inventory_page.add_item_to_cart("sauce-labs-bike-light")
    inventory_page.open_cart()
    cart_page.expect_loaded()
    cart_page.checkout()

    # 2. 배송 정보 입력 후 주문 확인 화면으로 진행
    checkout_info_page.expect_loaded()
    checkout_info_page.fill_customer_info(CUSTOMER)
    checkout_info_page.submit()

    # 3. 주문 확인: 상품 2개 + 총액 일관성(소계+세금=총액)
    checkout_overview_page.expect_loaded()
    expect(checkout_overview_page.items).to_have_count(2)
    checkout_overview_page.expect_totals_consistent()
    checkout_overview_page.finish()

    # 4. 주문 완료 화면 검증
    expect(page).to_have_url(re.compile(r"checkout-complete\.html"))
    checkout_complete_page.expect_order_complete()
