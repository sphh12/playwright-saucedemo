"""체크아웃 2단계 — 주문 요약 페이지 객체 (saucedemo /checkout-step-two.html).

소계/세금/총액 라벨을 파싱해 금액 일관성을 검증하는 헬퍼를 제공한다.
"""

from __future__ import annotations

import re

from playwright.sync_api import Locator, Page

from src.pages.base_page import BasePage

#: 라벨 텍스트에서 "$00.00" 형태의 금액을 파싱하는 정규식
_AMOUNT_PATTERN = re.compile(r"\$([0-9]+\.[0-9]{2})")


class CheckoutOverviewPage(BasePage):
    #: base_url 기준 상대 경로
    path: str = "/checkout-step-two.html"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        # 로케이터 선언 (testId = data-test 속성)
        self.items: Locator = page.get_by_test_id("inventory-item")
        self.item_names: Locator = page.get_by_test_id("inventory-item-name")
        self.subtotal_label: Locator = page.get_by_test_id("subtotal-label")
        self.tax_label: Locator = page.get_by_test_id("tax-label")
        self.total_label: Locator = page.get_by_test_id("total-label")
        self.finish_button: Locator = page.get_by_test_id("finish")
        self.cancel_button: Locator = page.get_by_test_id("cancel")

    def ready_locator(self) -> Locator:
        """페이지 로드 완료를 판단할 대표 로케이터."""
        return self.finish_button

    def get_item_names(self) -> list[str]:
        """주문 요약에 포함된 상품명 목록 반환 (공백 제거)."""
        names = [name.strip() for name in self.item_names.all_inner_texts()]
        print(f"[CheckoutOverviewPage] get_item_names: {names}")  # 디버깅용
        return names

    def expect_totals_consistent(self) -> None:
        """합계 금액 일관성 검증 (소계 + 세금 = 총액).

        각 라벨 텍스트에서 금액을 정규식으로 파싱하고,
        부동소수 오차를 감안해 1센트 미만 차이는 허용한다.
        """

        def parse_amount(locator: Locator, label: str) -> float:
            """라벨 로케이터의 텍스트에서 "$00.00" 금액을 파싱."""
            text = locator.inner_text()
            match = _AMOUNT_PATTERN.search(text)
            assert match is not None, f"{label} 금액 파싱 실패: {text!r}"
            return float(match.group(1))

        subtotal = parse_amount(self.subtotal_label, "소계")
        tax = parse_amount(self.tax_label, "세금")
        total = parse_amount(self.total_label, "총액")
        print(f"[CheckoutOverviewPage] totals subtotal={subtotal} tax={tax} total={total}")  # 디버깅용
        assert abs(subtotal + tax - total) < 0.01, f"소계+세금 != 총액: {subtotal} + {tax} != {total}"

    def finish(self) -> None:
        """주문 확정."""
        print("[CheckoutOverviewPage] finish: 주문 확정 클릭")  # 디버깅용
        self.finish_button.click()
