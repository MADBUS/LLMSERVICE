# Commit - Create a Git Commit

Create a commit following TDD commit discipline.

## Prerequisites
- ALL tests must be passing
- ALL compiler/linter warnings resolved

## Commit Types

### Behavioral Commit (feat/fix)
For changes that add or modify functionality:
```
feat:[편장열] [description of new behavior] [JIRA-ID]
fix:[편장열] [description of bug fix] [JIRA-ID]
```

### Structural Commit (refactor/style)
For changes that don't alter behavior:
```
refactor:[편장열] [description of structural change] [JIRA-ID]
style:[편장열] [formatting, naming changes] [JIRA-ID]
```

## Commit Message Format
```
[type]:[편장열] [short description] [백로그ID] AFAR-xxx

[optional body with more details]

Co-Authored-By: Claude <noreply@anthropic.com>
```

예시:
```
feat:[편장열] 부적합관리 업체명(부서명) 필드 추가 [QA-3] AFAR-105
```

- `[QA-3]` - plan.md 백로그 번호
- `AFAR-105` - Jira 이슈 키 (GitHub 연동용)

## Instructions

1. Run all tests - confirm passing
2. Check for warnings - resolve any issues
3. plan.md에서 현재 작업 중인 백로그 ID 및 AFAR-xxx 확인
4. Stage changes with `git add`
5. Create commit with Jira ID included
6. Keep commits small and focused

## Jira CLI 명령어 안내

커밋 완료 후 Jira 상태 변경이 필요하면 아래 명령어 사용:

```bash
# 이슈를 "완료"로 변경
jira issue move AFAR-xxx "완료"

# 이슈에 코멘트 추가
jira issue comment add AFAR-xxx "커밋 완료: [커밋 메시지]"
```

## Checklist
- [ ] All tests passing
- [ ] No warnings
- [ ] Commit type matches change type (behavioral vs structural)
- [ ] Jira ID included in commit message
- [ ] Message is clear and concise
