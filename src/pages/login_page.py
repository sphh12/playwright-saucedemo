"""saucedemo.com 로그인 페이지.

- saucedemo 는 data-test 속성을 제공하므로 get_by_test_id() 를 우선 사용한다.
  (tests/conftest.py 에서 test_id_attribute 를 'data-test' 로 지정해 둠)
- 성공/에러/URL 검증은 테스트 쪽에서 expect 폴링으로 수행한다.
"""

from __future__ import annotations

from playwright.sync_api import Locator, Page

from src.pages.base_page import BasePage


class LoginPage(BasePage):
    #: base_url 기준 로그인 페이지 경로 (루트)
    path = "/"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        # 로케이터는 생성자에서 선언 (data-test 속성 기반)
        self.username_input: Locator = page.get_by_test_id("username")
        self.password_input: Locator = page.get_by_test_id("password")
        self.login_button: Locator = page.get_by_test_id("login-button")
        self.error_message: Locator = page.get_by_test_id("error")

    def ready_locator(self) -> Locator:
        """로그인 버튼 가시성으로 페이지 준비 상태를 판단한다."""
        return self.login_button

    def login(self, username: str, password: str) -> None:
        """로그인 시도 — 필수입력 케이스 지원을 위해 빈 문자열 fill 을 허용한다.

        성공/실패 검증은 테스트 쪽에서 expect 로 수행한다.
        """
        print(f"[LoginPage] login as: {username}")  # 비밀번호는 로그에 남기지 않는다
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.login_button.click()
