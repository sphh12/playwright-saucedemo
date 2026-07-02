"""환경 정의 맵 — 대상 서비스 정보(URL/계정)를 한곳에서 관리한다.

- 기본 환경은 saucedemo(SwagLabs) 이며 .env 의 TEST_ENV 로 선택한다.
- 실계정/시크릿 값은 절대 코드에 하드코딩하지 말고 .env 로 주입한다. (.env 는 gitignore 대상)
  (단, saucedemo 는 공개 데모 계정이라 기본값 하드코딩을 허용한다.)
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

# .env 로드 — 이 모듈을 import 하는 곳(conftest/테스트) 어디서든 환경변수를 쓸 수 있게 여기서 로드한다.
load_dotenv(Path(__file__).resolve().parent.parent / ".env")


@dataclass(frozen=True)
class EnvConfig:
    """테스트 대상 환경 설정."""

    #: 테스트 대상 base URL
    base_url: str
    #: 로그인 계정 (필요한 환경에서만 정의)
    username: str | None = None
    password: str | None = None


# 환경 정의 맵 — 키를 TEST_ENV 로 선택한다.
ENVIRONMENTS: dict[str, EnvConfig] = {
    # 기본 환경 — SwagLabs 공개 데모 사이트 (공개 데모 계정이라 기본값 하드코딩 허용)
    "saucedemo": EnvConfig(
        base_url=os.environ.get("BASE_URL", "https://www.saucedemo.com"),
        username=os.environ.get("SAUCE_USERNAME", "standard_user"),
        password=os.environ.get("SAUCE_PASSWORD", "secret_sauce"),
    ),
    # 별칭 — 로컬에서도 동일한 공개 데모를 바라본다 (saucedemo 와 동일 설정)
    "local": EnvConfig(
        base_url=os.environ.get("BASE_URL", "https://www.saucedemo.com"),
        username=os.environ.get("SAUCE_USERNAME", "standard_user"),
        password=os.environ.get("SAUCE_PASSWORD", "secret_sauce"),
    ),
}

_env_name = os.environ.get("TEST_ENV", "saucedemo")
if _env_name not in ENVIRONMENTS:
    raise ValueError(f"알 수 없는 TEST_ENV: '{_env_name}' — 사용 가능한 환경: {', '.join(ENVIRONMENTS)}")

#: TEST_ENV 로 선택된 현재 환경 (기본: saucedemo)
current_env: EnvConfig = ENVIRONMENTS[_env_name]
