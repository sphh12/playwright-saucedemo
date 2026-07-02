# 변경 이력 (change_notes)

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
