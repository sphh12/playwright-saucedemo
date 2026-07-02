# Allure 리포트 가이드 (옵션)

기본 리포트는 pytest-html 의 `report.html` + 실패 시 저장되는 Playwright trace 이며 대부분의 경우 그것으로 충분하다.
팀 대시보드 등 Allure 생태계가 필요할 때만 아래처럼 켠다.

## 사용법

1. `.env` 파일에 아래 한 줄을 추가한다 (셸 명령이 아니라 `.env` 파일 내용이다):

   ```
   ALLURE=true
   ```

2. 테스트 실행 후 리포트를 생성/열람한다:

   ```bash
   pytest                 # allure-results/ 생성 (ALLURE=true 일 때만)
   make allure            # allure generate — allure-report/ 생성
   make allure-open       # 브라우저로 열기
   ```

`allure-pytest` 는 의존성에 포함되어 있어 파이썬 측 별도 설치는 필요 없다.
단, 리포트 생성용 **Allure CLI** 는 별도 설치가 필요하다 (Java 필요):

```bash
# macOS
brew install allure
# 또는 https://github.com/allure-framework/allure2/releases 에서 내려받아 PATH 등록
```

## 동작 방식

`conftest.py` 의 `pytest_configure` 가 `ALLURE=true` 일 때만 `--alluredir=allure-results` 를 활성화한다:

```python
def pytest_configure(config):
    if os.environ.get("ALLURE") == "true" and config.pluginmanager.hasplugin("allure_pytest"):
        if not getattr(config.option, "allure_report_dir", None):
            config.option.allure_report_dir = "allure-results"
```

실패한 테스트의 콘솔 로그는 `capture_console` fixture 가 Allure 첨부로도 남긴다. (`conftest.py` 참고)

## report.html 과의 선택 기준

| 상황                           | 추천                            |
| ------------------------------ | ------------------------------- |
| 로컬 디버깅, 실패 원인 분석    | trace (`playwright show-trace`) |
| 단건 결과 요약/CI 아티팩트     | pytest-html `report.html` (가벼움) |
| 팀 공유용 이력/트렌드 대시보드 | Allure                          |
