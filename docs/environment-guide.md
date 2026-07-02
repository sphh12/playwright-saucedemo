# 환경/시크릿 관리 가이드

## 구조

```
.env.example  ──복사──▶  .env (gitignore, 실값)
                           │ python-dotenv 로 로드
                           ▼
              config/environments.py (환경 정의 맵, 기본 saucedemo)
                           │ import
                           ▼
        conftest.py / 테스트 코드에서 사용
```

- **환경 정의는 코드에** (`config/environments.py` 의 `ENVIRONMENTS` 맵)
- **비밀값/선택값은 `.env` 에** (`os.environ.get("XXX", 기본값)` 으로 주입)

## 기본 환경 (saucedemo)

`TEST_ENV` 미설정 시 기본값은 `saucedemo` 이다. base_url/계정은 `.env` 로 덮어쓸 수 있다:

```python
ENVIRONMENTS: dict[str, EnvConfig] = {
    "saucedemo": EnvConfig(
        base_url=os.environ.get("BASE_URL", "https://www.saucedemo.com"),
        username=os.environ.get("SAUCE_USERNAME", "standard_user"),
        password=os.environ.get("SAUCE_PASSWORD", "secret_sauce"),
    ),
}
```

`.env` 에서 값 변경(선택):

```
TEST_ENV=saucedemo
SAUCE_USERNAME=standard_user
SAUCE_PASSWORD=****
```

실행하면 테스트가 `current_env` 로 해당 환경을 바라본다.
(런타임에 `--base-url` 로 넘기면 그 값이 우선한다 — `conftest.py` 의 `base_url` fixture 참고)

## 새 환경 추가하기

`config/environments.py` 에 항목을 추가한다:

```python
ENVIRONMENTS: dict[str, EnvConfig] = {
    "saucedemo": EnvConfig(base_url=os.environ.get("BASE_URL", "https://www.saucedemo.com"), ...),
    "staging": EnvConfig(
        base_url=os.environ.get("STAGING_URL", "https://staging.example.com"),
        username=os.environ.get("STAGING_USER"),      # 실값은 .env 에만
        password=os.environ.get("STAGING_PASSWORD"),
    ),
}
```

## 시크릿 규칙 (중요)

| 항목                 | 규칙                                          |
| -------------------- | --------------------------------------------- |
| `.env`               | gitignore — **절대 커밋 금지**                |
| `.auth/` (세션 파일) | gitignore — 로그인 토큰이 들어있음, 커밋 금지 |
| `.env.example`       | 커밋 O — 키 이름과 더미값만                   |
| 공개 데모 계정       | 코드 기본값 허용 (saucedemo 등 공개용만)      |

로그에도 비밀번호를 남기지 않는다 — `LoginPage.login()` 은 아이디만 출력한다.

## CI 에서의 시크릿

GitHub Actions 에서는 `.env` 파일 대신 **Repository Secrets** 를 사용한다:

```yaml
# .github/workflows/playwright.yml 의 테스트 스텝에 추가
- name: 테스트 실행
  run: python -m pytest
  env:
    TEST_ENV: staging
    STAGING_PASSWORD: ${{ secrets.STAGING_PASSWORD }}
```
