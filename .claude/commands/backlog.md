# Backlog Command

Read plan.md and find the next unmarked test. Create a backlog item for it.

## Jira Issue Format

### 제목 형식
```
[type]:[편장열] [역할]로서, [기능 설명]하고 싶다 [백로그ID]
```
- type: feat(기능), fix(버그), refactor(리팩토링)
- 담당자: 편장열 (항상 포함)
- 역할: 관리자, 사용자, 시스템 등
- 백로그ID: plan.md에 있는 ID (예: QA-1, PROD-2)

예시: `feat:[편장열] 관리자로서, 수입검사관리 조회 시 상태값을 확인하고 싶다 [QA-4]`

### Description 형식
```
# Domain
• [도메인명] (품질관리, 생산관리, 영업관리 등)

# Purpose
• [역할]로서, [기능]을 하여 [목적]을 달성하고 싶다.
• [상세 설명 1]
• [상세 설명 2]

# Success Criteria
[ ] [완료 조건 1]
[ ] [완료 조건 2]

# Todo
[ ] [할 일 1]
[ ] [할 일 2]
```

## Instructions

1. Read plan.md to find the target backlog item
2. 백로그 정보 파악 (도메인, 기능, 완료조건 등)
3. 백로그 카드 마크다운 출력 (노션 붙여넣기용)
4. plan.md에 백로그 ID 기록
5. 완료 메시지 출력

## Jira CLI 명령어 안내

백로그 생성 후 Jira 이슈 등록이 필요하면 아래 명령어 사용:

```bash
# 이슈 생성
jira issue create -t Story -s "feat:[편장열] 제목 [백로그ID]" --priority Medium

# 담당자 할당
jira issue assign AFAR-xxx "편장열"

# 내용 추가 (대화형)
jira issue edit AFAR-xxx

# 내용 추가 (파일에서)
jira issue edit AFAR-xxx -b "$(cat description.txt)" --no-input

# 이슈 상세 보기
jira issue view AFAR-xxx
```

## 도메인 매핑

- QA: 품질관리 (Quality Management)
- PROD: 생산관리 (Production Management)
- SALES: 영업관리 (Sales Management)
- MAT: 구매/재고관리 (Material Management)
- PRINT: 인쇄위치관리 (Print Position Management)
- API: API 공통 (Common API)
- SETT: 정산관리 (Settlement Management)
- POP: 현장관리 (POP Management)
