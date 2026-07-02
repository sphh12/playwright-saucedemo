"""로그인 후 모든 페이지 상단에 공통으로 존재하는 헤더 영역.

- "페이지"가 아니라 여러 페이지가 공유하는 UI 조각이므로 상속 대신 컴포지션으로 사용한다.
  (페이지 객체가 멤버로 포함 — InventoryPage.header 참고)
"""

from __future__ import annotations

from playwright.sync_api import Page, expect


class HeaderComponent:
    """장바구니 아이콘과 버거 메뉴(사이드바) 조작을 담당하는 헤더 컴포넌트."""

    def __init__(self, page: Page) -> None:
        # 로케이터는 생성자에서 선언한다.
        self.page = page
        self.cart_link = page.get_by_test_id("shopping-cart-link")
        self.cart_badge = page.get_by_test_id("shopping-cart-badge")
        # 버거 버튼은 data-test 속성이 없어 id 셀렉터로 접근한다.
        self.burger_button = page.locator("#react-burger-menu-btn")
        self.logout_link = page.get_by_test_id("logout-sidebar-link")
        self.reset_link = page.get_by_test_id("reset-sidebar-link")
        self.all_items_link = page.get_by_test_id("inventory-sidebar-link")
        self.about_link = page.get_by_test_id("about-sidebar-link")

    def open_cart(self) -> None:
        """장바구니 페이지로 이동."""
        print("[HeaderComponent] 장바구니 아이콘 클릭")  # 디버깅용
        self.cart_link.click()

    def open_menu(self) -> None:
        """버거 메뉴(사이드바)를 연다. 사이드바 링크 가시성으로 열림을 판정한다."""
        print("[HeaderComponent] 버거 메뉴 열기")  # 디버깅용
        self.burger_button.click()
        # 고정 대기 대신 사이드바 링크가 보일 때까지 expect 폴링으로 대기한다.
        expect(self.logout_link).to_be_visible()

    def logout(self) -> None:
        """로그아웃(메뉴 열기 → Logout 클릭)."""
        print("[HeaderComponent] 로그아웃")  # 디버깅용
        self.open_menu()
        self.logout_link.click()

    def reset_app_state(self) -> None:
        """앱 상태 초기화(메뉴 열기 → Reset App State 클릭)."""
        print("[HeaderComponent] 앱 상태 초기화")  # 디버깅용
        self.open_menu()
        self.reset_link.click()

    def go_to_all_items(self) -> None:
        """전체 상품 목록으로 이동(메뉴 열기 → All Items 클릭)."""
        print("[HeaderComponent] 전체 상품 목록으로 이동")  # 디버깅용
        self.open_menu()
        self.all_items_link.click()

    def expect_cart_badge_count(self, count: int) -> None:
        """장바구니 배지 개수를 검증한다.

        count가 0이면 배지가 존재하지 않아야 하므로 개수 0으로 검증하고,
        그 외에는 배지 텍스트가 해당 숫자와 일치하는지 검증한다.
        """
        print(f"[HeaderComponent] 장바구니 배지 개수 검증 count={count}")  # 디버깅용
        if count == 0:
            expect(self.cart_badge).to_have_count(0)
        else:
            expect(self.cart_badge).to_have_text(str(count))
