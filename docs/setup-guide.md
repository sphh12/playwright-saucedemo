# 환경 세팅 가이드 (통합)

프로젝트를 처음 받은 사람이 **클론 → 설치 → 검증 → 환경/시크릿 설정**까지 끝내는 데 필요한 모든 절차를 이 문서 하나로 관리한다.
(README의 "빠른 시작"은 이 문서의 요약본이다. 구 `environment-guide.md`의 환경/시크릿 관리 내용은 §5~§7로 통합됐다.)

## 1. 사전 요구사항

| 항목        | 버전/조건            | 확인 명령            |
| ----------- | -------------------- | -------------------- |
| Python      | 3.9 이상             | `python --version`   |
| git         | 최신 권장            | `git --version`      |
| make (선택) | 단축 명령용          | `make --version`     |
| Docker (선택) | 컨테이너 실행 시   | `docker --version`   |
| Allure CLI (선택) | Allure 리포트 시 | `allure --version` |

> **Windows 에서 make**: 기본 설치되지 않는다. `make` 없이도 README 실행 명령표의 "실제 명령"(`pytest -n auto` 등)을
> 그대로 쓰면 되므로 설치는 필수가 아니다. 설치하더라도 `make test-debug` 는 `PWDEBUG=1 python -m pytest -s` 처럼
> POSIX 환경변수 접두어 문법을 쓰기 때문에 Windows(cmd 셸) 에서는 동작하지 않는다 —
> 이때는 `$env:PWDEBUG=1; pytest -s` 로 직접 실행한다.

## 2. 설치 절차 (5단계)

```bash
# 0. 클론
git clone https://github.com/sphh12/playwright-saucedemo.git
cd playwright-saucedemo

# 1. 가상환경 생성 + 활성화
python -m venv .venv
source .venv/bin/activate          # macOS/Linux
# .venv\Scripts\Activate.ps1       # Windows PowerShell

# 2. 의존성 설치 (개발 도구 ruff 포함)
pip install -e ".[dev]"            # = make install

# 3. 브라우저 바이너리 설치 (최초 1회 — playwright 패키지와 별개로 필요)
playwright install chromium        # = make browsers

# 4. 환경 파일 생성 — 선택 (기본값만으로도 동작함, §5 참고)
cp .env.example .env               # Windows: Copy-Item .env.example .env
```

> 3단계가 필요한 이유: playwright 패키지는 제어 라이브러리일 뿐이고 실제 브라우저는 별도 다운로드다.
> (Cypress는 브라우저가 번들이지만 Playwright는 이 단계가 분리되어 있다.)

## 3. 설치 검증

설치가 끝나면 아래 2가지로 정상 동작을 확인한다.

```bash
# (1) 브라우저 구동 확인
python -c "from playwright.sync_api import sync_playwright; p = sync_playwright().start(); b = p.chromium.launch(); print('chromium OK:', b.version); b.close(); p.stop()"

# (2) 스모크 테스트 — 실제 saucedemo.com 대상, 수 초 내 통과해야 정상
pytest -m smoke
```

둘 다 통과하면 세팅 완료. 실패하면 `docs/troubleshooting.md`를 먼저 확인한다.

## 4. Docker로 대체하기 (로컬 세팅 생략)

로컬에 Python/브라우저를 설치하지 않고 컨테이너에서 바로 실행할 수 있다:

```bash
make docker-test        # = docker compose run --rm test
```

상세는 `docs/docker-guide.md` 참고. (Dockerfile의 playwright 이미지 태그는 `pyproject.toml`의 playwright 버전과 반드시 일치시킨다.)

## 5. 환경/시크릿 구조

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

### 기본 환경 (saucedemo)

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

### 새 환경 추가하기

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

## 6. 시크릿 규칙 (중요)

| 항목                 | 규칙                                          |
| -------------------- | --------------------------------------------- |
| `.env`               | gitignore — **절대 커밋 금지**                |
| `.auth/` (세션 파일) | gitignore — 로그인 토큰이 들어있음, 커밋 금지 |
| `.env.example`       | 커밋 O — 키 이름과 더미값만                   |
| 공개 데모 계정       | 코드 기본값 허용 (saucedemo 등 공개용만)      |

로그에도 비밀번호를 남기지 않는다 — `LoginPage.login()` 은 아이디만 출력한다.

`.env` 의 키 구조를 바꾸면 `.env.example` 도 같은 구조로 갱신한다 (`GIT_RULES.md` §7).

## 7. CI 에서의 시크릿

GitHub Actions 에서는 `.env` 파일 대신 **Repository Secrets** 를 사용한다:

```yaml
# .github/workflows/playwright.yml 의 테스트 스텝에 추가
- name: 테스트 실행
  run: python -m pytest
  env:
    TEST_ENV: staging
    STAGING_PASSWORD: ${{ secrets.STAGING_PASSWORD }}
```
