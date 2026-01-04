# Specs Index and Workflow

## Where to add specs
- Each change lives in its own folder under `.context/specs/`.
- Use date + slug: `YYYY-MM-DD-short-name`.

## Choose mode
- Light: UI polish, small bug fixes, refactors without behavior change.
- Full: contracts, integrations, security, deploy/infra, data storage, or scope > 1 day or > 3 files.

## Templates
- Light: `_templates/spec-light.md`
- Full: `_templates/spec-full.md` + `_templates/implementation_plan.md`

## Flow
- Light: spec -> implement -> quick verify
- Full: spec -> plan -> approval -> implement -> verify

## Scaffold script
- `powershell -ExecutionPolicy Bypass -File .context/specs/new-spec.ps1 -Slug your-feature -Mode light|full`
- Default mode is `full`.
- Output: `.context/specs/YYYY-MM-DD-your-feature/` with `spec.md` (and `implementation_plan.md` for full).

## Naming examples
- `2026-01-03-ui-copy-fix`
- `2026-01-05-whatsapp-webhook-hardening`
