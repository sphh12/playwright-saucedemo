# Docker 실행 가이드

로컬 환경(Python/브라우저 설치)과 무관하게 동일한 리눅스 컨테이너에서 테스트를 실행한다.

## 기본 사용법

```bash
# 전체 테스트 (이미지가 없으면 최초 1회 자동 빌드)
docker compose run --rm test

# 특정 파일만
docker compose run --rm test pytest tests/test_login.py

# 마커 필터
docker compose run --rm test pytest -m smoke
```

> ⚠️ 코드/의존성을 변경한 뒤에는 이미지가 **자동으로 다시 빌드되지 않는다**. `--build` 를 붙여야 한다:
>
> ```bash
> docker compose run --rm --build test
> ```

리포트는 볼륨 마운트되어 있어 실행 후 호스트의 `reports/report.html` / `test-results/` 에서 바로 확인할 수 있다.

## 주의사항

### 이미지 버전 = 패키지 버전

`Dockerfile` 의 이미지 태그는 `pyproject.toml` 의 `playwright` 버전과 **반드시 일치**해야 한다.

```dockerfile
FROM mcr.microsoft.com/playwright/python:v1.61.0-noble   # ← playwright==1.61.0 과 일치
```

버전이 어긋나면 "browser is not found" 류의 에러가 난다. Playwright 업그레이드 시 함께 수정할 것.

(공식 Python 이미지에는 브라우저가 미리 설치되어 있어 컨테이너 안에서 `playwright install` 이 불필요하다.)

### 타임존

`docker-compose.yml` 은 `TZ=Asia/Seoul` 로 컨테이너 시간대를 한국으로 맞춘다 (테스트 컨텍스트 locale/timezone 과 일관).

### Windows 줄바꿈 (CRLF)

컨테이너는 리눅스이므로 셸 스크립트가 CRLF 면 `bad interpreter` 에러가 난다.

`.gitattributes` 가 `*.sh`, `*.py`, `Dockerfile`, `Makefile`, `*.yml` 을 LF 로 강제하고 있으니 유지할 것.

### 사내 프록시/인증서 환경

`pip install` 이 컨테이너 안에서 실패하면 Dockerfile 에 프록시/인덱스 설정을 추가해야 할 수 있다:

```dockerfile
RUN pip config set global.proxy http://proxy.example.com:8080
# 또는: RUN pip install --index-url https://내부미러/simple -e .
```
