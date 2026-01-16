---
trigger: always_on
---

# Mandatory TDD Enforcement (Red-Green-Refactor)

## Test Process

**This project MUST follow strict Test-Driven Development practices:**

- **Always write tests FIRST** before writing production code
- Follow the Red-Green-Refactor cycle:
  1. **Red**: Write a test that fails (tests the desired behavior)
  2. **Green**: Write minimal production code to make the test pass
  3. **Refactor**: Improve code quality without changing behavior
- **End every task by running the test suite** and confirming all tests pass

## Test Structure
- Test files colocated with source: `src/game/Board.js` → `src/game/Board.test.js`
- Each test file covers one class/module

