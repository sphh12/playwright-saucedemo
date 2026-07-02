"""saucedemo.com 상품 목록(Inventory) 페이지."""

from __future__ import annotations

from typing import Literal

from playwright.sync_api import Locator, Page

from src.components.header_component import HeaderComponent
from src.pages.base_page import BasePage

#: 정렬 옵션 값 (saucedemo select 의 value)
SortOption = Literal["az", "za", "lohi", "hilo"]


class InventoryPage(BasePage):
    """상품 목록 페이지 객체 — 공통 헤더는 컴포지션으로 포함한다."""

    path = "/inventory.html"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.header = HeaderComponent(page)  # 공통 헤더 — 컴포지션으로 포함
        self.inventory_list = page.get_by_test_id("inventory-list")
        self.items = page.get_by_test_id("inventory-item")
        self.item_names = page.get_by_test_id("inventory-item-name")
        self.item_prices = page.get_by_test_id("inventory-item-price")
        self.sort_select = page.get_by_test_id("product-sort-container")

    def ready_locator(self) -> Locator:
        """상품 목록 컨테이너 가시성으로 페이지 준비 판정."""
        return self.inventory_list

    def add_item_to_cart(self, slug: str) -> InventoryPage:
        """slug 로 특정 상품을 장바구니에 담기."""
        print(f"[InventoryPage] 장바구니 담기: {slug}")  # 디버깅용
        self.page.get_by_test_id(f"add-to-cart-{slug}").click()
        return self

    def remove_item_from_cart(self, slug: str) -> InventoryPage:
        """slug 로 특정 상품을 장바구니에서 제거."""
        print(f"[InventoryPage] 장바구니 제거: {slug}")  # 디버깅용
        self.page.get_by_test_id(f"remove-{slug}").click()
        return self

    def sort_by(self, option: SortOption) -> InventoryPage:
        """정렬 변경 (az: 이름순, za: 이름역순, lohi: 가격낮은순, hilo: 가격높은순)."""
        print(f"[InventoryPage] 정렬 변경: {option}")  # 디버깅용
        self.sort_select.select_option(option)
        return self

    def get_item_names(self) -> list[str]:
        """화면에 표시된 상품명 목록을 반환 (좌우 공백 제거)."""
        return [name.strip() for name in self.item_names.all_inner_texts()]

    def get_prices(self) -> list[float]:
        """화면에 표시된 가격을 숫자 배열로 반환 (예: '$29.99' → 29.99)."""
        texts = self.item_prices.all_text_contents()
        return [float(t.replace("$", "")) for t in texts]

    def open_product(self, name: str) -> None:
        """상품명으로 카드를 찾아 상세 페이지로 진입."""
        print(f"[InventoryPage] 상품 상세 열기: {name}")  # 디버깅용
        self.item_names.filter(has_text=name).first.click()

    def open_cart(self) -> None:
        """헤더에 위임하여 장바구니 열기."""
        self.header.open_cart()

    def expect_cart_badge_count(self, count: int) -> None:
        """헤더에 위임하여 장바구니 배지 개수 검증."""
        self.header.expect_cart_badge_count(count)

    def logout(self) -> None:
        """헤더에 위임하여 로그아웃."""
        self.header.logout()

    def reset_app_state(self) -> None:
        """헤더에 위임하여 앱 상태 초기화."""
        self.header.reset_app_state()
