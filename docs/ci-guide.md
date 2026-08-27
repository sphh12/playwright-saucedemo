# CI 가이드 (GitHub Actions)

`.github/workflows/playwright.yml` 이 push / PR / 수동 실행 / 매일 정기 실행 시 전체 테스트를 돌리고
HTML 리포트(`report.html`)와 실패 산출물(`test-results/`)을 아티팩트로 업로드한다.

## 실행 트리거 4가지

| 트리거              | 방식 | 코드 변경 | 용도                                        |
| ------------------- | ---- | --------- | ------------------------------------------- |
| `push`              | 자동 | 필요      | main/master 푸시 시 회귀 검증               |
| `pull_request`      | 자동 | 필요      | PR 머지 전 게이트                           |
| `workflow_dispatch` | 수동 | 불필요    | Actions 탭 "Run workflow" — 올라간 코드 재실행 |
| `schedule`          | 자동 | 불필요    | 야간 회귀 (매일 KST 03:05)                  |

수동 실행/재실행은 CLI 로도 가능하다:

```bash
gh workflow run playwright.yml     # 최신 main 코드로 새로 실행
gh run rerun <런ID>                # 그 런이 쓴 커밋으로 재실행 (플레이키 확인용)
gh run rerun <런ID> --failed       # 실패한 job 만 재실행
```

## 동작 흐름

1. push / PR / 수동 실행 / 스케줄 중 하나로 워크플로 시작
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

### 스케줄 실행 (설정 완료 — 매일 정기 회귀)

현재 워크플로에 아래와 같이 적용되어 있다:

```yaml
on:
  schedule:
    - cron: '5 18 * * *' # UTC 18:05 = KST 03:05 (UTC 날짜 +1일이 KST 날짜)
```

코드 변경이 없어도 매일 돌기 때문에 **대상 사이트(saucedemo)의 UI·셀렉터 변화**와
**플레이키 테스트**를 잡아낸다. 주기를 바꿀 때 알아둘 점:

- `cron` 은 **UTC 기준**이다. KST = UTC + 9 (한국은 서머타임이 없어 연중 동일). UTC 18:05 발동분은 **KST 날짜로 하루 뒤** 새벽이다.
- 정시(`:00`)는 GitHub 부하가 몰려 수 분~수십 분 지연될 수 있다 — 분 단위를 비정시로 두는 편이 낫다.
- **스케줄은 정시 보장이 아니다** — "이 시각 이후 여유될 때" 발동한다. 실측 지연: 평소 **+19분**,
  GitHub Actions 장애 시 **+203분**(2026-08-27, Critical 등급 장애). 지연이 심하면 실행이 아예 취소될 수도 있다.
  그래서 새벽(03:05)에 두어 **출근 전까지 6시간 버퍼**를 확보한다 — 3시간 지연돼도 06:30 이전에 끝난다.
- **기본 브랜치(main)** 의 워크플로 파일만 스케줄 실행된다. 브랜치에서 cron 을 바꿔도 머지 전에는 적용되지 않는다.
- 저장소가 **60일간 활동이 없으면** GitHub 이 스케줄 워크플로를 자동 비활성화한다(알림 메일 발송).
  이때는 Actions 탭에서 다시 활성화하면 된다.

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
