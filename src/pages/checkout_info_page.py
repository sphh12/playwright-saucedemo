"""saucedemo.com 체크아웃 1단계 페이지 (배송 정보 입력).

- 고객 정보를 입력하고 다음 단계(주문 확인)로 진행하거나 취소한다.
- 필수 입력 검증 케이스를 위해 빈 문자열 입력도 허용한다.
"""

from __future__ import annotations

from playwright.sync_api import Locator, Page

from src.data.test_data import CustomerInfo
from src.pages.base_page import BasePage


class CheckoutInfoPage(BasePage):
    path = "/checkout-step-one.html"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.first_name_input = page.get_by_test_id("firstName")
        self.last_name_input = page.get_by_test_id("lastName")
        self.postal_code_input = page.get_by_test_id("postalCode")
        self.continue_button = page.get_by_test_id("continue")
        self.cancel_button = page.get_by_test_id("cancel")
        self.error_message = page.get_by_test_id("error")

    def ready_locator(self) -> Locator:
        return self.first_name_input

    def fill_customer_info(self, customer: CustomerInfo) -> CheckoutInfoPage:
        """고객 정보(dataclass)를 세 필드에 입력. (빈 문자열 허용)"""
        print(f"[CheckoutInfoPage] 배송 정보 입력: {customer.last_name}{customer.first_name}")  # 디버깅용
        return self.fill_shipping_info(customer.first_name, customer.last_name, customer.postal_code)

    def fill_shipping_info(self, first_name: str, last_name: str, postal_code: str) -> CheckoutInfoPage:
        """개별 필드 값으로 배송 정보를 입력. (필수 입력 케이스용, 빈 문자열 허용)"""
        print(f"[CheckoutInfoPage] 배송 정보 입력(개별 필드): {last_name}{first_name}")  # 디버깅용
        self.first_name_input.fill(first_name)
        self.last_name_input.fill(last_name)
        self.postal_code_input.fill(postal_code)
        return self

    def submit(self) -> None:
        """다음 단계(주문 확인)로 진행."""
        print("[CheckoutInfoPage] submit(continue) 클릭")  # 디버깅용
        self.continue_button.click()

    def cancel(self) -> None:
        """취소하고 장바구니로 돌아감."""
        print("[CheckoutInfoPage] cancel 클릭")  # 디버깅용
        self.cancel_button.click()
