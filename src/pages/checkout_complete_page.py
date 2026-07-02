"""saucedemo.com 체크아웃 완료 페이지 (/checkout-complete.html).

주문 확정 후 표시되는 최종 화면으로, 완료 헤더/문구와 홈으로 돌아가기 버튼을 담당한다.
"""

from __future__ import annotations

from playwright.sync_api import Locator, Page, expect

from src.pages.base_page import BasePage


class CheckoutCompletePage(BasePage):
    path = "/checkout-complete.html"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        # 로케이터 선언 (testId = data-test)
        self.complete_header = page.get_by_test_id("complete-header")
        self.complete_text = page.get_by_test_id("complete-text")
        self.back_home_button = page.get_by_test_id("back-to-products")

    def ready_locator(self) -> Locator:
        """페이지 로드 판단 대표 요소 — 주문 완료 헤더."""
        return self.complete_header

    def expect_order_complete(self) -> None:
        """주문 완료 메시지 검증 (자동 폴링)."""
        print("[CheckoutCompletePage] 주문 완료 확인")  # 디버깅용
        expect(self.complete_header).to_have_text("Thank you for your order!")

    def back_home(self) -> None:
        """홈(상품 목록)으로 돌아가기."""
        print("[CheckoutCompletePage] 홈으로 돌아가기")  # 디버깅용
        self.back_home_button.click()
