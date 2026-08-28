# 트러블슈팅

자주 겪는 문제와 해결 방법. (증상 → 원인 → 해결 순)

## 브라우저 관련

### `Executable doesn't exist at ...chromium...`

- **원인**: Playwright 브라우저 미설치, 또는 패키지 업그레이드 후 브라우저 버전 불일치
- **해결**: `python -m playwright install chromium`
- **예방**: `playwright` 버전을 올리면 항상 브라우저 재설치

### 설치 중 다운로드 실패 (사내망)

- **원인**: 프록시/방화벽이 `cdn.playwright.dev` 차단
- **해결**: `HTTPS_PROXY` 환경변수 설정 후 재시도, 또는 미러 사용
  (`PLAYWRIGHT_DOWNLOAD_HOST` 환경변수)

## import / 실행 관련

### `ModuleNotFoundError: No module named 'config'` (또는 'src')

- **원인**: 프로젝트 루트가 `sys.path` 에 없음 (pytest 를 다른 위치에서 실행)
- **해결**: 프로젝트 루트에서 실행한다. `pyproject.toml` 의 `[tool.pytest.ini_options] pythonpath = ["."]`
  가 루트를 import 경로에 추가하므로, 루트에서 `pytest` 를 실행하면 된다.

## 테스트 관련

### 테스트가 엉뚱한 사이트(base_url)로 접속한다

- **원인**: pytest-playwright 의 `browser_context_args` 는 session 스코프라 "첫 테스트"의 base_url 이
  세션 전체에 캐시된다.
- **해결**: 루트 `conftest.py` 의 `browser_context_args` 오버라이드가 매 테스트 `base_url` 을 명시적으로
  덮어쓰도록 되어 있다 — 이 오버라이드를 삭제하지 말 것.

### 로그인 테스트만 이미 로그인된 상태로 시작한다

- **원인**: 프로젝트 공통 `storage_state` 가 적용됨
- **해결**: 해당 테스트 파일에서 `sauce_storage_state` fixture 를 `None` 으로 오버라이드해 빈 세션으로 시작한다 —
  `tests/test_login.py` 참고

```python
@pytest.fixture
def sauce_storage_state() -> None:
    return None
```

### 어제까지 되던 테스트가 `.auth/sauce_demo.json` 에러로 실패

- **원인**: 저장된 세션 만료 또는 파일 손상
- **해결**: `.auth/` 폴더 삭제 후 재실행 — `sauce_storage_state` fixture 가 다시 로그인해서 저장한다

### 간헐적으로 실패하는(플레이키) 테스트 찾기

```bash
make repeat        # pytest --count=3 으로 3회 반복 실행 (pytest-repeat)
```

### 실패 원인을 모르겠을 때 — trace 보기

실패한 테스트는 trace 가 자동 저장된다 (`--tracing=retain-on-failure`).

```bash
playwright show-trace test-results/<테스트 폴더>/trace.zip
```

타임라인으로 각 액션 시점의 DOM/네트워크/콘솔을 되돌려 볼 수 있다. **가장 강력한 디버깅 수단.**

(실패 시 브라우저 콘솔 로그는 `capture_console` fixture 가 pytest 출력에도 남긴다.)

## Windows 관련

### 셸 스크립트 실행 시 `bad interpreter: /bin/bash^M`

- **원인**: CRLF 줄바꿈으로 저장된 `.sh` 파일
- **해결**: LF 로 변환 (VS Code 우하단 CRLF → LF 클릭이 가장 간단). 명령으로 할 때는 OS별 sed 문법이 다르다:
    - macOS(BSD sed): `sed -i '' 's/\r$//' <파일>` (`-i` 뒤에 빈 문자열 `''` 필수)
    - Linux(GNU sed): `sed -i 's/\r$//' <파일>`
- **예방**: `.gitattributes` 가 `*.sh`/`*.py`/`Makefile` 등을 LF 로 강제하고 있음 — 삭제하지 말 것

### 터미널에서 한글 로그가 깨진다

- **원인**: 콘솔 코드페이지가 UTF-8 이 아님
- **해결**: PowerShell 에서 `chcp 65001` 실행 또는 Windows Terminal 사용
