"""상품 목록(Inventory) 테스트 — 저장된 로그인 세션으로 시작한다."""

from __future__ import annotations

import pytest
from playwright.sync_api import expect

from src.pages.inventory_page import InventoryPage

# 실측(live_analysis.json)으로 확정된 담기 대상 상품 slug
BACKPACK = "sauce-labs-backpack"
BIKE_LIGHT = "sauce-labs-bike-light"


@pytest.fixture(autouse=True)
def _open_inventory(inventory_page: InventoryPage) -> None:
    # 저장된 로그인 세션으로 시작하므로 바로 상품 목록에 접근할 수 있다.
    inventory_page.goto()


@pytest.mark.smoke
def test_six_products_visible(inventory_page: InventoryPage) -> None:
    """상품이 6개 노출된다 (@smoke)."""
    expect(inventory_page.items).to_have_count(6)


@pytest.mark.e2e
def test_sort_name_az(inventory_page: InventoryPage) -> None:
    """이름 오름차순(A to Z)으로 정렬된다."""
    # 정렬 전에 상품 6개가 렌더된 상태를 먼저 보장 (빈 배열 오탐 방지)
    expect(inventory_page.items).to_have_count(6)
    inventory_page.sort_by("az")

    # 현재 이름을 읽어 오름차순 정렬 기대값을 계산한다.
    expected_names = sorted(inventory_page.get_item_names())
    print(f"[test_inventory] az 정렬 기대값: {expected_names}")  # 디버깅용
    expect(inventory_page.item_names).to_have_text(expected_names)


@pytest.mark.e2e
def test_sort_name_za(inventory_page: InventoryPage) -> None:
    """이름 내림차순(Z to A)으로 정렬된다."""
    expect(inventory_page.items).to_have_count(6)
    inventory_page.sort_by("za")

    expected_names = sorted(inventory_page.get_item_names(), reverse=True)
    print(f"[test_inventory] za 정렬 기대값: {expected_names}")  # 디버깅용
    expect(inventory_page.item_names).to_have_text(expected_names)


@pytest.mark.e2e
def test_sort_price_low_high(inventory_page: InventoryPage) -> None:
    """가격 오름차순(low to high)으로 정렬된다."""
    # 정렬 전에 상품 6개가 렌더된 상태를 먼저 보장 (빈 배열 오탐 방지)
    expect(inventory_page.items).to_have_count(6)
    inventory_page.sort_by("lohi")

    # get_prices()(all_text_contents)는 자동 대기가 없어 재렌더 전 값을 읽는 레이스가 있으므로,
    # 브라우저 안에서 "오름차순이 될 때까지" 재시도하도록 wait_for_function 으로 폴링한다.
    # length === 6 조건은 빈 배열 오탐(vacuous truth)을 막는다.
    inventory_page.page.wait_for_function(
        """() => {
            const prices = [...document.querySelectorAll('[data-test="inventory-item-price"]')]
                .map(el => parseFloat(el.textContent.replace('$', '')));
            return prices.length === 6 && prices.every((v, i, a) => i === 0 || a[i - 1] <= v);
        }"""
    )

    prices = inventory_page.get_prices()
    print(f"[test_inventory] lohi 정렬 후 가격: {prices}")  # 디버깅용
    assert prices == sorted(prices)


@pytest.mark.e2e
def test_sort_price_high_low(inventory_page: InventoryPage) -> None:
    """가격 내림차순(high to low)으로 정렬된다."""
    expect(inventory_page.items).to_have_count(6)
    inventory_page.sort_by("hilo")

    # 내림차순이 될 때까지 브라우저 안에서 폴링 (scrape-then-assert 레이스 방지)
    inventory_page.page.wait_for_function(
        """() => {
            const prices = [...document.querySelectorAll('[data-test="inventory-item-price"]')]
                .map(el => parseFloat(el.textContent.replace('$', '')));
            return prices.length === 6 && prices.every((v, i, a) => i === 0 || a[i - 1] >= v);
        }"""
    )

    prices = inventory_page.get_prices()
    print(f"[test_inventory] hilo 정렬 후 가격: {prices}")  # 디버깅용
    assert prices == sorted(prices, reverse=True)


@pytest.mark.e2e
def test_add_items_increases_badge(inventory_page: InventoryPage) -> None:
    """여러 상품을 담으면 카트 배지 수량이 증가한다."""
    inventory_page.add_item_to_cart(BACKPACK)
    inventory_page.add_item_to_cart(BIKE_LIGHT)
    inventory_page.expect_cart_badge_count(2)


@pytest.mark.e2e
def test_remove_item_decreases_badge(inventory_page: InventoryPage) -> None:
    """담은 상품을 인벤토리에서 제거하면 배지 수량이 감소한다."""
    inventory_page.add_item_to_cart(BACKPACK)
    inventory_page.add_item_to_cart(BIKE_LIGHT)
    inventory_page.expect_cart_badge_count(2)

    inventory_page.remove_item_from_cart(BACKPACK)
    inventory_page.expect_cart_badge_count(1)
