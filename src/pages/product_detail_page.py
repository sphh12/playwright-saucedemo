"""saucedemo.com 상품 상세(Product Detail) 페이지."""

from __future__ import annotations

from playwright.sync_api import Locator, Page

from src.pages.base_page import BasePage


class ProductDetailPage(BasePage):
    #: base_url 기준 상대 경로 — 상세는 쿼리스트링(?id=)이 붙지만 경로는 동일하다.
    path = "/inventory-item.html"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        # 상세 화면 로케이터 선언 (data-test 속성 기반)
        self.name = page.get_by_test_id("inventory-item-name")
        self.desc = page.get_by_test_id("inventory-item-desc")
        self.price = page.get_by_test_id("inventory-item-price")
        # 주의: 상세의 담기/제거 버튼은 목록과 달리 정적 셀렉터(add-to-cart / remove)다.
        self.add_button = page.get_by_test_id("add-to-cart")
        self.remove_button = page.get_by_test_id("remove")
        self.back_button = page.get_by_test_id("back-to-products")

    def ready_locator(self) -> Locator:
        # 상세 상품명이 보이면 페이지 준비 완료로 판단
        return self.name

    def add_to_cart(self) -> ProductDetailPage:
        """상세 화면에서 장바구니에 담기."""
        print("[ProductDetailPage] 장바구니 담기")  # 디버깅용
        self.add_button.click()
        return self

    def back_to_products(self) -> None:
        """상품 목록으로 복귀."""
        print("[ProductDetailPage] 상품 목록으로 복귀")  # 디버깅용
        self.back_button.click()
