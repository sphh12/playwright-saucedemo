"""saucedemo.com 장바구니 페이지."""

from __future__ import annotations

from playwright.sync_api import Locator, Page

from src.pages.base_page import BasePage


class CartPage(BasePage):
    #: base_url 기준 장바구니 경로
    path = "/cart.html"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        # 로케이터 선언 (data-test 기반)
        self.cart_list = page.get_by_test_id("cart-list")
        self.items = page.get_by_test_id("inventory-item")
        self.item_names = page.get_by_test_id("inventory-item-name")
        self.checkout_button = page.get_by_test_id("checkout")
        self.continue_shopping_button = page.get_by_test_id("continue-shopping")

    def ready_locator(self) -> Locator:
        """장바구니 로드 완료 판단 요소 — 체크아웃 버튼."""
        return self.checkout_button

    def remove_item(self, slug: str) -> CartPage:
        """장바구니에서 특정 상품 제거."""
        print(f"[CartPage] 상품 제거: {slug}")  # 디버깅용
        self.page.get_by_test_id(f"remove-{slug}").click()
        return self

    def get_item_names(self) -> list[str]:
        """장바구니에 담긴 상품명 목록 반환(공백 제거)."""
        return [name.strip() for name in self.item_names.all_inner_texts()]

    def continue_shopping(self) -> None:
        """쇼핑 계속하기 — 인벤토리로 복귀."""
        print("[CartPage] 쇼핑 계속하기")  # 디버깅용
        self.continue_shopping_button.click()

    def checkout(self) -> None:
        """결제(체크아웃) 시작."""
        print("[CartPage] 체크아웃 시작")  # 디버깅용
        self.checkout_button.click()
