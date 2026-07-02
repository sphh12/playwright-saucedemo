"""장바구니(Cart) 테스트 — 저장된 로그인 세션으로 시작한다 (sauce_storage_state 참고)."""

from __future__ import annotations

import re

import pytest
from playwright.sync_api import Page, expect

from src.data.test_data import PRODUCTS
from src.pages.cart_page import CartPage
from src.pages.checkout_info_page import CheckoutInfoPage
from src.pages.inventory_page import InventoryPage

# 실측 확인된 상품명 (live_analysis.json)
BACKPACK_NAME = PRODUCTS["sauce-labs-backpack"]
BIKE_LIGHT_NAME = PRODUCTS["sauce-labs-bike-light"]


@pytest.fixture(autouse=True)
def _open_inventory(inventory_page: InventoryPage) -> None:
    # 저장된 로그인 세션으로 시작하므로 바로 상품 목록에 접근할 수 있다.
    inventory_page.goto()


@pytest.mark.e2e
def test_added_items_appear_in_cart(inventory_page: InventoryPage, cart_page: CartPage) -> None:
    """담은 여러 상품이 장바구니에 표시된다."""
    inventory_page.add_item_to_cart("sauce-labs-backpack")
    inventory_page.add_item_to_cart("sauce-labs-bike-light")
    inventory_page.open_cart()

    cart_page.expect_loaded()
    # 카트에 2개 상품이 담겨 있어야 한다 (자동 폴링).
    expect(cart_page.items).to_have_count(2)
    # 담은 두 상품명이 각각 포함되어야 한다 (filter + count 로 web-first 검증).
    expect(cart_page.item_names.filter(has_text=BACKPACK_NAME)).to_have_count(1)
    expect(cart_page.item_names.filter(has_text=BIKE_LIGHT_NAME)).to_have_count(1)
    print(f"[test_cart] 장바구니 상품명: {cart_page.get_item_names()}")  # 디버깅용


@pytest.mark.e2e
def test_remove_item_reduces_count(inventory_page: InventoryPage, cart_page: CartPage) -> None:
    """장바구니에서 상품을 제거하면 개수가 줄어든다 (2 → 1)."""
    inventory_page.add_item_to_cart("sauce-labs-backpack")
    inventory_page.add_item_to_cart("sauce-labs-bike-light")
    inventory_page.open_cart()

    cart_page.expect_loaded()
    expect(cart_page.items).to_have_count(2)

    cart_page.remove_item("sauce-labs-backpack")
    expect(cart_page.items).to_have_count(1)
    print(f"[test_cart] 제거 후 장바구니 상품명: {cart_page.get_item_names()}")  # 디버깅용


@pytest.mark.e2e
def test_continue_shopping_returns_to_inventory(inventory_page: InventoryPage, cart_page: CartPage, page: Page) -> None:
    """쇼핑 계속하기를 누르면 인벤토리로 돌아간다."""
    inventory_page.add_item_to_cart("sauce-labs-backpack")
    inventory_page.open_cart()

    cart_page.expect_loaded()
    cart_page.continue_shopping()

    # 인벤토리로 복귀 — URL 및 상품 목록 로드 확인.
    expect(page).to_have_url(re.compile(r"inventory\.html"))
    inventory_page.expect_loaded()


@pytest.mark.e2e
def test_checkout_navigates_to_info(
    inventory_page: InventoryPage, cart_page: CartPage, checkout_info_page: CheckoutInfoPage, page: Page
) -> None:
    """체크아웃을 누르면 배송정보 입력 화면으로 진입한다."""
    inventory_page.add_item_to_cart("sauce-labs-backpack")
    inventory_page.open_cart()

    cart_page.expect_loaded()
    cart_page.checkout()

    # 체크아웃 1단계(배송정보)로 진입 — URL 및 입력 폼 로드 확인.
    expect(page).to_have_url(re.compile(r"checkout-step-one\.html"))
    checkout_info_page.expect_loaded()
