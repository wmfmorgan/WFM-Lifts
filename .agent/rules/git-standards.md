---
trigger: always_on
---

# Git Policy (Mandatory)

## Git Workflow


- Keep commits focused and descriptive

## Mandatory Git and .gitignore requirements:**

### Git Commit & Workflow standards
   
- Stage all changes: `git add .`
- Main branch: stable, working code
- Feature branches for new capabilities: `feature/ghost-piece`, `feature/scoring`
- **Branch Naming**: `feature/`, `fix/`, `refactor/`, `test/`

- Commit format - <type>: <description>
- description: phase-specific message (example: phase 1 core game logic with tetromino, board, and scoring tests) 
- type: 
  - `feat:` New features
  - `fix:` Bug fixes
  - `refactor:` Code restructuring
  - `test:` Testing related changes
  - `docs:` Documentation updates
  - `chore:` Maintenance tasks
- Verify commit with `git log --oneline`


### .gitignore Standards
- **Before ANY commits and before ANY dependencies are added**, create and propose `.gitignore` for approval
- **.gitignore MUST be committed FIRST** (as the first commit after repo initialization)
- **No production code commits until `.gitignore` is in place**
- Proposed `.gitignore` content (for user approval before implementation):
  ```
  # Dependencies
  node_modules/
  package-lock.json

  # Build outputs
  dist/
  build/

  # IDE & Editor
  .vscode/
  .idea/
  *.swp
  *.swo
  *~
  .DS_Store

  # Environment
  .env
  .env.local
  .env.*.local

  # Logs
  *.log
  npm-debug.log*
  yarn-debug.log*

  # Testing
  coverage/
  .nyc_output/

  # Temporary files
  tmpclaude-*
  ```