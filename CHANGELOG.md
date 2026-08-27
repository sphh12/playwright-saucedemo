# Changelog

프로젝트의 주요 변경 이력을 이 파일 하나에서 관리한다.

- 형식: [Keep a Changelog](https://keepachangelog.com/ko/1.1.0/) 기반 — **최신 항목이 위**(역순), 항목 분류는 `### Added` / `### Changed` / `### Fixed`.
- 할 일은 `## [Unreleased]` 에서 관리한다 (구 `Todo.md` 통합).
- 오래된 이력(3~6개월 경과)은 `archive/CHANGELOG-<범위>.md` 로 분리한다 — 현재 아카이브 없음.

## [Unreleased]

구 `Todo.md` "다음 추천 작업" 중 현재도 유효한 항목 (우선순위순):

- [ ] **CI 시크릿/브라우저 매트릭스**: GitHub Actions에 chromium 외 firefox/webkit 매트릭스 확장, 필요 시 계정 시크릿 주입.
- [ ] **Allure 리포트 파이프라인**: `ALLURE=true`로 실행 후 `allure serve`/CI 아티팩트 연동 확인.
- [ ] **추가 시나리오**: problem_user / performance_glitch_user 계정 케이스, 상세 페이지 상품별(6종) 파라미터라이즈, 결제 실패/경계값 확장.
- [ ] **병렬 실행 튜닝**: `pytest -n auto`(xdist) 동작/세션 storage_state 상호작용 점검.
- [ ] **CI 액션 버전 업**: `actions/checkout@v4`·`setup-python@v5`·`upload-artifact@v4` 가 Node.js 20 deprecated 경고를 낸다(현재는 Node 24 로 강제 실행되어 동작에는 문제 없음). v5 계열로 올려 경고 제거.

## 2026-08-27

### Changed
- **야간 회귀 실행 시각 변경**: `cron '40 21 * * *'`(KST 06:40) → `'5 18 * * *'`(UTC 18:05 = KST 03:05). 스케줄은 정시 보장이 아니라 "이 시각 이후 여유될 때" 발동하는데, 2026-08-27 GitHub Actions Critical 장애로 **+203분 지연**되어 KST 10:02에 실행됐다(평소 +19분). 새벽으로 옮겨 출근 전까지 약 6시간 버퍼를 확보 — 3시간 지연돼도 06:30 이전 완료. `docs/ci-guide.md` 에 실측 지연 데이터와 UTC/KST 날짜 차이 주의 반영.
- **CI 워크플로 표시 이름 변경**: `Playwright Tests` → `Playwright - SaucedLabs`. Actions 탭 사이드바와 이후 런에 반영된다. 과거 런은 내부 기록(`run.name`)에 실행 시점 이름을 그대로 유지하지만, 스케줄 런의 목록 제목은 워크플로의 **현재** 이름으로 표시되므로 지난 야간 회귀도 새 이름으로 보인다(실측 확인).

## 2026-08-24

### Fixed
- **CI 워크플로우 YAML 문법 오류 수정**: `playwright.yml` 31행 step 이름의 `(CI: 실패 시 2회 재시도)` 안에 있는 콜론+공백을 YAML 파서가 "키: 값" 구분자로 오인해, 2026-07-02 최초 푸시부터 모든 CI 런이 job 생성 없이 0초 startup failure 였다. 이름 전체를 따옴표로 감싸 해결(`Invalid workflow file ...#L31` 어노테이션 근거). 재발 방지로 `GIT_RULES.md` §10 커밋 전 검증에 워크플로우 YAML 파싱 명령 추가, 이를 위해 `pyyaml` 을 dev 의존성에 추가.

### Added
- **CI 야간 회귀(schedule) 트리거 추가**: 매일 `cron: '40 21 * * *'`(UTC 21:40 = KST 06:40) 자동 실행. 코드 변경이 없어도 돌기 때문에 대상 사이트(saucedemo) UI·셀렉터 변화와 플레이키 테스트를 감지한다. 정시 대신 40분으로 둔 이유는 GitHub 정시 부하로 인한 지연 회피. `docs/ci-guide.md` 에 트리거 4종(push/PR/수동/스케줄) 표와 `gh workflow run`·`gh run rerun` 사용법, 스케줄 제약(UTC 기준·기본 브랜치 한정·60일 무활동 시 자동 비활성화) 정리.
- **README 서두에 테스트 대상 사이트 소개 추가**: SwagLabs(saucedemo.com)가 무엇인지(Sauce Labs 공개 데모 쇼핑몰, 핵심 플로우, 동작이 다른 데모 계정들) 프로젝트 소개 앞에 명시.

### Changed
- **환경 세팅 가이드 통합**: README 빠른 시작 + `docs/environment-guide.md` + `.env.example` 사용법에 흩어져 있던 세팅 설명을 `docs/setup-guide.md` 하나로 통합(`git mv`로 이력 보존). 사전 요구사항·설치 5단계·설치 검증·Docker 대체 경로 추가, 기존 환경/시크릿 관리 내용은 §5~§7로 편입. README 빠른 시작은 요약본으로 유지하고 통합 가이드 포인터 추가, 문서 인덱스 갱신.
- **변경 이력 문서 개편**: `change_notes.md` + `Todo.md` → `CHANGELOG.md`(Keep a Changelog 형식) 단일 파일 통합. 미완료 할 일은 `[Unreleased]`로 큐레이션 — 이미 완료된 "git 초기화 & 원격 푸시" 항목은 제외. 구 `Todo.md` 원본은 하단 부록 A에 무손실 보존.

## 2026-07-02

### 프로젝트 신규 생성 — playwright_swagLabs_py
- `playwright_template_py`(템플릿) 구조/컨벤션을 계승하고, `cypress_swagLabs`의 SwagLabs(saucedemo) 시나리오 전체를 Playwright + pytest(Python)로 이식.
- **실제 브라우저 라이브 분석**: Playwright로 saucedemo.com 전 플로우(로그인→인벤토리→상세→카트→체크아웃 3단계→완료)를 주행하여 모든 `data-test` 셀렉터·상품 6종·정렬옵션·에러 텍스트·금액 계산을 실측 검증 후 코드 작성.
- **POM 구성**(1급 승격):
  - `src/pages/`: base_page, login, inventory, product_detail, cart, checkout_info, checkout_overview, checkout_complete
  - `src/components/`: header_component (버거메뉴/로그아웃/리셋/카트배지)
  - `src/data/test_data.py`: 고객정보/계정/상품/에러 상수
- **테스트 28종**: login(5) / inventory(7) / cart(4) / checkout(5) / menu(2) / product_detail(3) / purchase(1) / smoke(1)
- **인프라**: pyproject(ruff/pytest/markers), 루트 conftest(ko-KR·Asia/Seoul·콘솔캡처·Allure), tests/conftest(data-test testId·storage_state 로그인 1회·페이지 fixture), Dockerfile/docker-compose, GitHub Actions, docs/, .env.example.
- **검증**: `.venv` 생성 → `pip install -e '.[dev]'` → `ruff` 통과 → 실제 saucedemo 대상 **pytest 28 passed, 0 failed (22s)**.

### 규칙 준수
- 주석/docstring 한국어, 식별자 영어. 고정대기 금지(로케이터 자동대기 + `expect` 폴링, 가격정렬은 `wait_for_function`). 에러 검증은 접두사 고려해 `to_contain_text` 부분매칭. 비밀번호 로깅 금지.

---

## 부록 A — 구 `Todo.md` 원본 (2026-08-24 통합 시점, 무손실 보존)

# 할 일 (Todo)

## 진행 중
- (없음)

## 완료
- [x] 템플릿 클론/분석 + cypress 시나리오 분석
- [x] 실제 saucedemo 브라우저 라이브 분석
- [x] POM 페이지/컴포넌트 8종 작성
- [x] 테스트 28종 작성 + 실제 실행 통과(28 passed)

## 다음 추천 작업 (우선순위순)
1. **git 초기화 & 원격 푸시**: `git init` → github.com/sphh12/playwright_swagLabs_py 레포 생성/연결 → 최초 커밋/푸시 (GIT_RULES.md 참고).
2. **CI 시크릿/브라우저 매트릭스**: GitHub Actions에 chromium 외 firefox/webkit 매트릭스 확장, 필요 시 계정 시크릿 주입.
3. **Allure 리포트 파이프라인**: `ALLURE=true`로 실행 후 `allure serve`/CI 아티팩트 연동 확인.
4. **추가 시나리오**: problem_user / performance_glitch_user 계정 케이스, 상세 페이지 상품별(6종) 파라미터라이즈, 결제 실패/경계값 확장.
5. **병렬 실행 튜닝**: `pytest -n auto`(xdist) 동작/세션 storage_state 상호작용 점검.
