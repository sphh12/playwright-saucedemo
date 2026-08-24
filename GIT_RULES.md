# Git 규칙 (Git Rules)

코드를 Git 저장소에 커밋/푸시할 때 준수해야 할 규칙. (cypress_swagLabs / playwright_template 의 규칙과 동일한 정책을 이 프로젝트 맥락으로 옮긴 것)

원격 저장소: `origin = github.com/sphh12/playwright_swagLabs_py`

## 1. 커밋 메시지 컨벤션

Conventional Commits 형식 + 한국어 설명을 사용한다.

```
<type>: <변경 내용 요약>

(필요 시 본문에 상세 설명)
```

| type       | 용도                            |
| ---------- | ------------------------------- |
| `feat`     | 새 테스트/페이지 객체/기능 추가 |
| `fix`      | 테스트/코드 버그 수정           |
| `refactor` | 동작 변화 없는 구조 개선        |
| `docs`     | 문서만 변경                     |
| `chore`    | 설정, 의존성, 기타 잡무         |

예: `feat: 체크아웃 필수입력 검증 시나리오 추가`

## 2. 커밋/푸시 전 'claude' 흔적 제거 (필수)

포트폴리오/공개 저장소를 염두에 두고, 커밋 메시지와 코드 주석에서 **AI 작성자 흔적**을 제거한다.
제거 대상: `Co-Authored-By: Claude ...`, `Generated with Claude Code`, `🤖` 등 자동 삽입 태그.

Windows(PowerShell):

```powershell
git diff --cached | Select-String -Pattern 'Co-Authored-By: Claude|Generated with Claude|🤖'
git log -1 --format=%B | Select-String -Pattern 'Claude'
```

macOS/Linux(bash):

```bash
git diff --cached | grep -iE 'co-authored-by: claude|generated with claude|🤖'
git log -1 --format=%B | grep -i claude
```

> **예외 — 유지 대상**: 기능 코드의 `claude`(API 모델명, CLI 명령 등)와 프로젝트 문서 `CLAUDE.md`,
> `.claude/` 설정은 정당한 파일이므로 제거하지 않는다. (위 검색의 false positive)

## 3. 푸시 전 민감정보 스캔 (필수)

푸시 전에 아래를 반드시 확인한다. **한 번이라도 커밋된 시크릿은 히스토리에 영구 기록된다.**

Windows(PowerShell) — 회사 기본 환경:

```powershell
# 추적 중인 파일에 시크릿/로컬 설정 파일이 섞여 있는지 확인 (.env.example 은 정상이므로 제외)
git ls-files | Select-String -Pattern '\.env($|\.)|\.auth/|settings\.local\.json' | Where-Object { $_ -notmatch '\.env\.example' }

# 스테이징된 변경에 비밀번호/토큰 흔적이 있는지 확인
git diff --cached | Select-String -Pattern 'password|secret|token|apikey'
```

macOS/Linux(bash) — 집 환경:

```bash
git ls-files | grep -E "\.env($|\.)|\.auth/|settings\.local\.json" | grep -v '\.env\.example'
git diff --cached | grep -iE "password|secret|token|apikey"
```

체크리스트:

- [ ] `.env`(및 `.env.local`, `.env.staging` 등 변형), `.auth/` 가 커밋 목록에 없는가?
- [ ] `.claude/settings.local.json`(개인 로컬 설정)이 커밋 목록에 없는가?
- [ ] 실계정 아이디/비밀번호가 코드에 하드코딩되어 있지 않은가? (공개 데모 계정 saucedemo 는 예외)
- [ ] 스크린샷/트레이스 등 산출물(`test-results/`, `report.html`)이 커밋되지 않았는가?
- [ ] 가상환경(`.venv/`)/캐시(`__pycache__/`)가 커밋되지 않았는가?

## 4. .gitignore 필수 항목

이 프로젝트의 `.gitignore` 는 아래를 반드시 포함한다 (삭제하지 말 것):

```gitignore
# 가상환경 / 파이썬 캐시
.venv/
__pycache__/
*.py[cod]
.pytest_cache/
.ruff_cache/

# 테스트 산출물
test-results/
reports/
allure-results/
allure-report/

# 시크릿/세션 — 절대 커밋 금지
.env
.env.*
!.env.example
.auth/

# 로컬 전용 설정
.claude/settings.local.json
```

> 웹(Playwright)에서 상응하는 민감/대용량 항목은 `.auth/`(세션 storage_state)와 리포트 산출물이다.

## 5. 저장소 유형별 정책

| 항목            | Private 저장소 | Public 저장소 |
| --------------- | -------------- | ------------- |
| 민감정보 스캔   | 권장           | **필수**      |
| 시크릿 하드코딩 | 지양           | **금지**      |
| `.example` 파일 | 권장           | **필수**      |

> "커밋은 `.env.example` 만, 실값은 `.env`" 원칙을 기본으로 한다.

## 6. 저장소 공개상태 자동 판별 & 푸시 게이트

푸시 전에 현재 저장소가 Public 인지 자동으로 판별하고, Public 이면 스캔 게이트를 반드시 통과시킨다.

```bash
# true = Private / false = Public
gh repo view --json isPrivate --jq '.isPrivate'
```

- **Private**: §3 스캔 권장 후 푸시
- **Public**: §2(claude 흔적 제거) + §3(민감정보 스캔)을 **모두 통과한 뒤에만** 푸시

## 7. `.example` 파일 동기화

`.env` 등 실제 설정 파일의 **구조가 바뀌면 대응하는 `.example` 파일도 함께 갱신**한다.

- 키를 추가/삭제/이름변경하면 `.env` 와 `.env.example` 양쪽에 동일하게 반영한다.
- `.example` 에는 **실값이 아니라 플레이스홀더/더미값**만 넣는다 (예: `SAUCE_PASSWORD=<YOUR_PASSWORD>`).
- 목적: 신규 클론 사용자가 `.env.example` 만 보고도 필요한 모든 키를 알 수 있게 해 온보딩이 깨지지 않게 한다.

체크리스트: `.env` 를 수정했다면 → `.env.example` 도 같은 키 구조인지 확인했는가?

## 8. 브랜치/푸시 정책

- 기본 브랜치에 직접 커밋하지 않고, 작업 브랜치 → PR(또는 머지) 흐름을 권장
- 여러 원격 저장소를 쓰는 경우, 별도 언급이 없으면 설정된 모든 원격에 푸시 (기본: `origin`)
- 강제 푸시(`--force`)는 개인 작업 브랜치에서만

## 9. 긴급 조치 — 민감정보를 실수로 커밋했을 때

시크릿이 커밋되면 파일을 지우는 것만으로는 부족하다. **히스토리에 남고, 노출된 값은 이미 유효하지 않다고 간주**해야 한다.

```bash
# 1. 추적에서 제거 + gitignore 등록 후 새 커밋
git rm --cached <파일>
echo "<파일>" >> .gitignore
git commit -m "chore: 시크릿 파일 추적 제거"

# 2. 히스토리에서 완전 삭제 (권장: git filter-repo, 또는 BFG)
git filter-repo --path <파일> --invert-paths
#   또는: bfg --delete-files <파일>

# 3. 원격 강제 푸시 (협업 중이면 팀원 재동기화 필요)
git push origin --force --all

# 4. 노출된 시크릿 즉시 무효화/재발급 (가장 중요 — 위 조치와 별개로 반드시)
#    - 계정 비밀번호 변경
#    - API 키/토큰 재발급
#    - .auth 세션(storage_state) 폐기 후 재로그인
```

> `filter-repo`/`BFG` 는 히스토리를 재작성하므로, 협업 저장소에서는 팀원에게 반드시 공지한다.

## 10. 커밋 전 파일 무결성 검증

VS Code 의 format-on-save + Windows CRLF 조합에서 **파일 끝이 잘리거나 훼손되는 사고**를 방지한다.

Windows(PowerShell):

```powershell
# 구문/정적 검증 — 실패하면 커밋 금지
ruff check .
# 설정 파일 유효성 (pyproject.toml 파싱)
python -c "import tomllib; tomllib.load(open('pyproject.toml','rb'))"
# CI 워크플로우 YAML 유효성 — 깨진 워크플로우는 푸시 후 0초 실패로만 드러난다
#   PyYAML 이 필요하다 (dev 의존성에 포함 — `pip install -e ".[dev]"` 로 설치)
python -c "import yaml, io; yaml.safe_load(io.open('.github/workflows/playwright.yml', encoding='utf-8'))"
# 변경 규모 확인 (파일이 통째로 줄었는지)
git diff --cached --stat
```

macOS/Linux(bash):

```bash
ruff check .
python -c "import tomllib; tomllib.load(open('pyproject.toml','rb'))"
python -m compileall -q config src tests conftest.py   # 문법 오류 조기 발견
git diff --cached --stat
```

검증 실패(구문 에러, 예상치 못한 대량 삭제) 시에는 커밋하지 말고 원인을 먼저 확인한다.
