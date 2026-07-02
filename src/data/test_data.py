"""SwagLabs(saucedemo) 테스트에서 재사용하는 공용 데이터/상수 모음.

실제 saucedemo DOM 실측값(live_analysis.json)을 신뢰 소스로 사용한다.
비밀번호는 공개 데모 계정 값(secret_sauce)만 포함하며 로그에는 절대 남기지 않는다.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CustomerInfo:
    """체크아웃 배송정보 입력에 사용하는 고객 정보."""

    first_name: str
    last_name: str
    postal_code: str


# 체크아웃에 사용할 기본 고객 정보 (cypress testdata 이식)
CUSTOMER = CustomerInfo(first_name="Gildong", last_name="Hong", postal_code="12345")


@dataclass(frozen=True)
class UserAccount:
    """로그인 계정(아이디/비밀번호) 정보."""

    username: str
    password: str


# 공개 데모 공용 비밀번호
PASSWORD = "secret_sauce"

# 시나리오별 계정 (전부 동일 비밀번호 사용)
STANDARD_USER = UserAccount("standard_user", PASSWORD)
LOCKED_OUT_USER = UserAccount("locked_out_user", PASSWORD)
PROBLEM_USER = UserAccount("problem_user", PASSWORD)
PERF_GLITCH_USER = UserAccount("performance_glitch_user", PASSWORD)

# 상품 slug → 표시 이름 (실측 6종)
PRODUCTS: dict[str, str] = {
    "sauce-labs-backpack": "Sauce Labs Backpack",
    "sauce-labs-bike-light": "Sauce Labs Bike Light",
    "sauce-labs-bolt-t-shirt": "Sauce Labs Bolt T-Shirt",
    "sauce-labs-fleece-jacket": "Sauce Labs Fleece Jacket",
    "sauce-labs-onesie": "Sauce Labs Onesie",
    "test.allthethings()-t-shirt-(red)": "Test.allTheThings() T-Shirt (Red)",
}

# 로그인/체크아웃 에러 메시지 상수 (부분매칭 substring 값 — to_contain_text 로 검증)
ERR_LOCKED = "Sorry, this user has been locked out"
ERR_USERNAME_REQUIRED = "Username is required"
ERR_PASSWORD_REQUIRED = "Password is required"
ERR_CREDENTIALS_MISMATCH = "Username and password do not match"
