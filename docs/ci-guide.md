# CI 가이드 (GitHub Actions)

`.github/workflows/playwright.yml` 이 push / PR / 수동 실행 시 전체 테스트를 돌리고
HTML 리포트(`report.html`)와 실패 산출물(`test-results/`)을 아티팩트로 업로드한다.

## 동작 흐름

1. `main`/`master` 로 push 또는 PR → 워크플로 자동 시작 (Actions 탭에서 수동 실행도 가능)
2. Python 3.12 설치 → `pip install -e .` → `python -m playwright install --with-deps chromium`
3. `python -m pytest --reruns 2` 실행 — CI 에서는 실패 시 2회 재시도 (플레이키 완화)
4. 성공/실패와 무관하게 `report.html` + `test-results/` 를 아티팩트로 업로드 (보관 30일)

## 리포트 확인 방법

GitHub → Actions 탭 → 해당 실행 → Artifacts → `playwright-report` 다운로드 → 압축 해제 후:

- `report.html` : 브라우저로 열면 전체 결과 요약
- `test-results/<테스트>/trace.zip` : 실패한 테스트의 trace →
  ```bash
  playwright show-trace <경로>/trace.zip
  ```
  타임라인 단위로 각 액션 시점의 DOM/네트워크/콘솔을 되돌려 볼 수 있다. **가장 강력한 디버깅 수단.**

## 자주 쓰는 확장

### 멀티 브라우저 매트릭스

```yaml
strategy:
  matrix:
    browser: [chromium, firefox, webkit]
steps:
  - run: python -m playwright install --with-deps ${{ matrix.browser }}
  - run: python -m pytest --browser ${{ matrix.browser }}
```

(pytest-playwright 는 `--browser` 옵션으로 브라우저를 선택한다. 여러 번 주면 모두 실행된다.)

### 스케줄 실행 (매일 새벽 정기 회귀)

```yaml
on:
  schedule:
    - cron: '0 22 * * *' # UTC 22:00 = KST 07:00
```

### 시크릿 주입

민감값은 저장소 Settings → Secrets and variables → Actions 에 등록 후:

```yaml
- run: python -m pytest
  env:
    STAGING_PASSWORD: ${{ secrets.STAGING_PASSWORD }}
```

## GitLab 등 다른 CI 를 쓰는 경우

핵심 커맨드는 동일하다: `pip install -e .` → `python -m playwright install --with-deps chromium` → `python -m pytest`.
Docker 실행 환경이라면 `mcr.microsoft.com/playwright/python:v<버전>-noble` 이미지를 쓰면 브라우저 설치가 생략된다.
