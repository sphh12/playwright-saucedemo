# POM 설계 가이드

이 프로젝트의 Page Object Model 구조와, Cypress/JS 방식과의 차이를 설명한다.

## 구조: 3개 층

```
BasePage (src/pages/base_page.py)     ← 공통 계약: path + ready_locator + goto/expect_loaded
   ↑ 상속
구체 페이지 (LoginPage, InventoryPage …)  ← 로케이터 + 사용자 행동 메서드
   +  컴포지션
컴포넌트 (HeaderComponent …)          ← 여러 페이지가 공유하는 UI 조각
```

### BasePage 계약 (Template Method 패턴)

각 페이지는 두 가지만 정의한다:

```python
class LoginPage(BasePage):
    path = "/"                       # ① base_url 기준 상대 경로 (클래스 속성)

    def ready_locator(self) -> Locator:  # ② "로드 완료" 판단 기준 요소
        return self.login_button
```

이것만으로 `goto()`(이동+대기), `expect_loaded()`(로드 검증)를 물려받는다.

UI 흐름으로 페이지에 도착했을 때는 `goto()` 대신 `expect_loaded()` 로 도착만 검증한다.

### 페이지 vs 컴포넌트

- **페이지**: URL 이 있는 화면. `BasePage` 상속.
- **컴포넌트**: URL 이 없는 공유 UI 조각(헤더, 버거메뉴, 장바구니 배지 등). 상속하지 않고
  페이지가 멤버로 **포함(컴포지션)** 한다. → `src/components/header_component.py` 참고

## 싱글턴이 아니라 fixture 주입 (Cypress 경험자용)

Cypress 는 전역 `cy` 하나로 동작하므로 페이지 객체를 싱글턴으로 export 하는 것이 자연스럽다.

Playwright/pytest 는 테스트마다 **독립된 `page` 인스턴스**가 주입되므로(병렬 실행·격리),
페이지 객체도 `page` 를 받아 매 테스트 새로 만들어야 한다. fixture 가 그 생성을 자동화한다:

```python
# tests/conftest.py — conftest 에 fixture 를 등록해 두면
@pytest.fixture
def login_page(page: Page) -> LoginPage:
    return LoginPage(page)

# 테스트 — 파라미터에 적기만 하면 주입된다 (안 쓰면 생성도 안 됨)
def test_login(login_page: LoginPage) -> None: ...
```

| 항목             | Cypress/JS 방식                    | 이 프로젝트 (Playwright + pytest)                |
| ---------------- | ---------------------------------- | ------------------------------------------------ |
| 페이지 객체 획득 | `export default new LoginPage()`   | conftest fixture 주입 (`@pytest.fixture`)        |
| 대기 전략        | 커스텀 재시도 게이트               | 로케이터 자동 대기 + `expect` (내장)             |
| 공통 로그인      | `cy.login()` 커스텀 커맨드         | `sauce_storage_state` + `storage_state` (1회)    |
| 상태 저장 금지   | 인스턴스에 상태 저장 금지          | 동일 — 로케이터는 상태가 아닌 선언이라 안전함    |

## 로케이터 우선순위 (권장)

1. `get_by_role` — 접근성 기반, 가장 견고 (예: `get_by_role("button", name="Add to cart")`)
2. `get_by_test_id` — 서비스가 테스트 속성을 제공할 때 (SwagLabs 는 `data-test`)
3. `get_by_text` / `get_by_placeholder` — 보조 수단
4. CSS/XPath — 최후의 수단 (구조 변경에 취약, 예: `#react-burger-menu-btn`)

> saucedemo 는 `data-test` 속성을 쓰므로 `tests/conftest.py` 의 autouse fixture 에서
> `playwright.selectors.set_test_id_attribute("data-test")` 로 지정해 `get_by_test_id` 를 그대로 쓸 수 있게 했다.
> (Python 은 이 설정이 **전역**이라, conftest 에서 세션 종료 시 기본값 `data-testid` 로 복원한다.)

## 고정 대기 금지

`page.wait_for_timeout()`(무조건 N초 대기) 은 쓰지 않는다. 로케이터 자동 대기와 `expect(...)` 폴링을 사용한다.

DOM 을 직접 긁어 비교(scrape-then-assert)해야 하면, 재렌더 레이스를 막기 위해
`page.wait_for_function(...)`(조건이 참이 될 때까지 브라우저 안에서 폴링)을 쓴다.

→ `tests/test_inventory.py` 의 가격 정렬 테스트 참고.

## 새 페이지 추가 절차

1. `src/pages/` 아래에 `xxx_page.py` 생성 — `BasePage` 상속
2. 로케이터는 생성자에서 선언, 행동은 메서드로 (검증 로직은 가급적 테스트 쪽에)
3. `tests/conftest.py` 에 페이지 객체 fixture 를 등록한다.
   (루트 `conftest.py` 의 공통 fixture 는 자동 상속된다.)
4. 테스트에서 파라미터로 받아 사용
