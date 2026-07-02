# Playwright 공식 Python 이미지 — 태그 버전을 pyproject.toml 의 playwright 버전과 반드시 맞출 것
FROM mcr.microsoft.com/playwright/python:v1.61.0-noble

WORKDIR /app

# 의존성 먼저 복사/설치 (Docker 레이어 캐시 활용)
COPY pyproject.toml ./
RUN pip install --no-cache-dir -e .

COPY . .

CMD ["pytest"]
