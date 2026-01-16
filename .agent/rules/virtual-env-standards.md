---
trigger: always_on
---

# Mandatory Virtual Environment Policy (Mandatory Isolation)
**ALL development, dependency management, and execution MUST occur in isolated virtual environments:**

- **Docker is the method** for this project
- Create a `Dockerfile`
- Build image
- Run container
- All CI/CD pipelines and deployments must use Docker containers
- Never run `npm install` or development commands directly on host machine
- Local development without Docker is acceptable only if explicitly documented and agreed to