---
trigger: always_on
---

# Mandatory Development Process

## Development occurs in phases and child tasks
**Example**
- [] Phase 2.0 Core Game Logic
  - [] 2.0.1 Create test files (RED phase): `src/game/Tetromino.test.js`, `src/game/Board.test.js`, `src/game/scoring.test.js` with describe blocks and stub tests
  - [] 2.1 Create `src/game/constants.js` with BOARD_WIDTH (10), BOARD_HEIGHT (20), CELL_SIZE (30), DROP_INTERVAL (1000ms)
  - [] 2.2 Define all 7 tetromino shapes as 4×4 matrices in constants.js (I, O, T, S, Z, J, L) 

**MANDATORY TDD Workflow for every task:**
1. **Write test(s) FIRST** that describe the desired behavior
2. Run the test - verify test fails (RED)
3. Write minimal production code to pass tests (GREEN)
4. Refactor if needed while keeping tests passing (REFACTOR)
5. Run the test again - confirm all tests pass

**Use Docker for isolation **

**Development best practices:**
- Implement phase by phase - complete all child tasks within a phase to complete it
- **Test BEFORE production code** - Non-negotiable
- Commit after each completed phase with descriptive messages (follow git-standards.md)
- **ALWAYS run unit test suite before committing** - tests must all pass

### Phase Completion Checklist

**At the end of EVERY phase, perform these cleanup steps:**

1. **Remove temporary files:**
   - Delete any temp files (auto-ignored by .gitignore)
   - Remove test scaffolding, mock data, or debug code
   - Clean up commented-out code blocks
   - Remove statements used for debugging

2. **Clean up Docker resources:**
   - Check for stopped containers
   - Remove stopped containers (if needed)
   - Check Docker images

3. **Verify code quality:**
   - Ensure all unit tests pass
   - Verify coverage meets phase requirements
   - Check for unused imports or variables
   - Ensure no temporary or experimental code remains

4. **Git commit:**
   - follow git-standards.md

5. **Documentation:**
   - Update inline comments if complex logic was added
   - Update README.md if user-facing changes were made
   - Mark completed tasks
   - Mark the phase complete if all tasks are complete

**This checklist is MANDATORY at the end of each phase to maintain a clean, professional codebase.**
