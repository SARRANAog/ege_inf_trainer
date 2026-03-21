# EGE Informatics Trainer — PRD / Working Notes

## Current stack
- **Backend:** FastAPI + MongoDB (motor)
- **Frontend:** React 18 + React Router + plain CSS
- **Code editor:** Monaco Editor
- **Execution/checking:** Python subprocess + AST checks

## Current status after cleanup
- project stays on the current stack
- local development is the primary target
- environment files are normalized for localhost
- legacy Tailwind/PostCSS layer was removed because the UI uses regular CSS
- runtime content now includes all connected exercise packs

## Product modules already in place
1. onboarding + profile
2. theory for tasks 1–27 (short/full)
3. practice with closed and code tasks
4. roadmap
5. weekly review
6. mock exam
7. progress analytics

## Known next-stage work
- content QA for exercises/explanations
- richer filtering and autosave in practice
- stronger smoke/integration tests
- README/runtime docs improvement as project evolves
