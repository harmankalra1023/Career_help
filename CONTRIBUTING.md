# Contributing to Digital Career Twin (DCT)

Thank you for your interest in contributing! Digital Career Twin is an open-source, evidence-based career intelligence platform.

## Development Workflow

1. Fork and clone the repository.
2. Ensure you have Python 3.11+ and Node.js 18+ (or Docker).
3. Copy environment configuration:
   ```bash
   cp .env.example .env
   ```
4. Run setup and development servers:
   ```bash
   make dev
   ```
   Or run components individually:
   - Backend: `cd apps/api && uvicorn app.main:app --reload`
   - Frontend: `cd apps/web && pnpm dev`

## Coding Standards

- **Python**: Follow PEP 8, formatted with `ruff`, typed with `mypy --strict` on core modules.
- **TypeScript**: Strict mode enabled, formatted with Prettier and linted with ESLint.
- **Git Commits**: Follow [Conventional Commits](https://www.conventionalcommits.org/) (e.g. `feat:`, `fix:`, `docs:`, `test:`).
- **Branching**: Trunk-based development with short-lived feature branches (`feat/feature-name`, `fix/issue-description`).
- **Tests**: Every new feature or bug fix must include automated tests (unit/integration).

## Architecture Boundaries

- Routers call Services. Services call DB/Models or pure domain libraries.
- Services never import Routers.
- The scoring, matching, and simulator engines are **pure functions** (no direct I/O) to ensure deterministic testability.
- All contributions must adhere to privacy, fairness, and consent requirements outlined in `docs/prd.md`.

## Submitting a Pull Request

1. Create a descriptive PR title following conventional commit guidelines.
2. Link relevant issues or tasks from `docs/work-plan.md`.
3. Verify all checks pass:
   ```bash
   make test
   make lint
   ```
4. A maintainer will review your pull request.
