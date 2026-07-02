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
