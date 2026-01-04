# Agentic Workflows: Stilo

## CDD Modes (Gemini Conductor)
### Light
Use for small, low risk changes such as UI copy, minor bug fixes, or refactors without behavior change.
Artifacts: spec-light.md (implementation plan optional).

### Full
Use for changes that affect contracts, integrations, or system behavior.
Artifacts: spec-full.md + implementation_plan.md + approval.

## Mode Triggers
- Full if: API or JSON contract changes, new endpoints, external integrations, secrets or security, deploy or infra changes, data storage, or scope > 1 day or > 3 files.
- Light if: UI polish, small bug with clear cause, refactor without behavior change, local style fixes.
- When unsure, default to Full.

## Feature Implementation Flow (Full)
1. Spec: define requirements in a spec-full.md (see .context/specs/_templates).
2. Plan: create implementation_plan.md.
3. Approval: human review and approval of the plan.
4. Implement: code execution in small, verifiable chunks.
5. Verify: automated and manual verification.

## Lightweight Flow
1. Spec: capture intent in spec-light.md.
2. Implement: small, contained changes.
3. Verify: quick manual or targeted checks.

## Testing Strategy
- Backend: health checks and endpoint validation.
- Frontend: UI consistency and end-to-end integration tests.
- AI Logic: prompt evaluation and JSON contract validation.

## Environment Management
- Frontend uses import.meta.env.
- Backend uses python-dotenv.
- Production uses Secret Manager.
