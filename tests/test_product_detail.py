"""상품 상세 테스트 — 저장된 로그인 세션으로 시작한다 (sauce_storage_state 참고)."""

from __future__ import annotations

import re

import pytest
from playwright.sync_api import Page, expect

from src.pages.inventory_page import InventoryPage
from src.pages.product_detail_page import ProductDetailPage


@pytest.fixture(autouse=True)
def _open_inventory(inventory_page: InventoryPage) -> None:
    # 저장된 로그인 세션으로 시작하므로 바로 상품 목록에 접근할 수 있다.
    inventory_page.goto()


@pytest.mark.e2e
def test_click_product_opens_detail(
    page: Page,
    inventory_page: InventoryPage,
    product_detail_page: ProductDetailPage,
) -> None:
    """상품명을 클릭하면 해당 상품 상세로 진입한다."""
    inventory_page.open_product("Sauce Labs Backpack")

    product_detail_page.expect_loaded()
    # 상세 URL 은 inventory-item.html (쿼리스트링 포함) 이어야 한다.
    expect(page).to_have_url(re.compile(r"inventory-item\.html"))
    # 상세 상품명이 클릭한 상품과 일치해야 한다.
    expect(product_detail_page.name).to_have_text("Sauce Labs Backpack")


@pytest.mark.e2e
def test_add_to_cart_from_detail(
    inventory_page: InventoryPage,
    product_detail_page: ProductDetailPage,
) -> None:
    """상세 화면에서 상품을 장바구니에 담을 수 있다."""
    inventory_page.open_product("Sauce Labs Backpack")
    product_detail_page.expect_loaded()

    product_detail_page.add_to_cart()
    # 담은 뒤에는 정적 Remove 버튼(data-test="remove")이 노출된다.
    expect(product_detail_page.remove_button).to_be_visible()


@pytest.mark.e2e
def test_back_to_products_from_detail(
    page: Page,
    inventory_page: InventoryPage,
    product_detail_page: ProductDetailPage,
) -> None:
    """상세에서 목록으로 돌아갈 수 있다."""
    inventory_page.open_product("Sauce Labs Backpack")
    product_detail_page.expect_loaded()

    product_detail_page.back_to_products()
    # 목록으로 복귀하면 inventory.html 로 이동하고 인벤토리가 로드되어야 한다.
    expect(page).to_have_url(re.compile(r"inventory\.html"))
    inventory_page.expect_loaded()
