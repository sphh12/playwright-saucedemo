"""모든 페이지 객체의 공통 부모 클래스 (Template Method 패턴).

각 페이지는 두 가지만 정의하면 된다:
  1. path            — base_url 기준 상대 경로 (클래스 속성)
  2. ready_locator() — "이 페이지가 준비됐다"고 판단할 대표 요소

Playwright 는 클릭/입력 시 자동 대기(auto-wait)가 내장되어 있어서
Cypress 처럼 wait 헬퍼를 두껍게 만들 필요가 없다. 공통화는 최소한으로 유지한다.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from playwright.sync_api import Locator, Page, expect


class BasePage(ABC):
    #: base_url 기준 상대 경로 (예: '/inventory.html') — 각 페이지에서 재정의한다.
    path: str = ""

    def __init__(self, page: Page) -> None:
        self.page = page

    @abstractmethod
    def ready_locator(self) -> Locator:
        """페이지 로드 완료를 판단할 대표 로케이터 — 각 페이지에서 구현."""
        raise NotImplementedError

    def goto(self) -> BasePage:
        """페이지로 이동하고 준비될 때까지 대기."""
        print(f"[{type(self).__name__}] goto: {self.path}")  # 디버깅용
        self.page.goto(self.path)
        self.expect_loaded()
        return self

    def expect_loaded(self) -> BasePage:
        """현재 페이지가 준비 상태인지 검증 (UI 흐름으로 도착했을 때도 사용)."""
        expect(self.ready_locator(), f"{type(self).__name__} 로드 확인").to_be_visible()
        return self
