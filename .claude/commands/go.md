# Go - Execute Next TDD Cycle

Find the next test in plan.md and implement it following TDD.

## Workflow

1. **Read plan.md** - Find the next unmarked test (AFAR-xxx 이슈 키 확인)
2. **Red Phase** - Write a failing test
3. **Run tests** - Confirm it fails
4. **Green Phase** - Write minimum code to pass
5. **Run tests** - Confirm all pass
6. **Mark complete** - Update plan.md with [x]
7. **Consider refactoring** - If needed, enter refactor phase

## Rules

- ONE test at a time
- Minimum code to pass
- Run tests after each phase
- Mark progress in plan.md

## Jira CLI 명령어 안내

작업 시작/완료 시 Jira 상태 변경이 필요하면 아래 명령어 사용:

```bash
# 이슈를 "진행 중"으로 변경
jira issue move AFAR-xxx "진행 중"

# 이슈를 "완료"로 변경
jira issue move AFAR-xxx "완료"

# 이슈 상세 보기
jira issue view AFAR-xxx
```

## Output Format

After completing:
```
Completed: [test name]
Status: [Red -> Green -> Refactored (if applicable)]
Next: [next test in plan.md or "All tests complete"]
Jira: jira issue move AFAR-xxx "완료"
```
