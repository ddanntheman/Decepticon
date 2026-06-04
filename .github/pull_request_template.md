## Summary

<!--
One paragraph: what observable behavior changes (or "no-op refactor;
behavior preserved"), and why. Avoid restating the diff in prose.
-->

## Changes

<!-- Bullet list of key changes. -->

-

## Intent

- **Issue / ADR this satisfies:** <!-- #123, docs/adr/NNNN-*.md, or "release-blocker" -->
- **Anti-goal** (one thing this PR could have done but deliberately does not):

## Blast radius

Tick the row that best matches this change. The
[CODEOWNERS](../.github/CODEOWNERS) file is the ground truth — this
field is a fast self-classification, not a substitute. See
[docs/adr/0002-pr-tiering-and-blast-radius.md](../docs/adr/0002-pr-tiering-and-blast-radius.md).

- [ ] **Tier-auto** — tests, internal refactors, non-policy docs, lockfile-only dep bumps.
- [ ] **Tier-delegate** — agent prompts, skill bodies, middleware internals, web/CLI features.
- [ ] **Tier-owner** — anything CODEOWNERS-gated (CI/workflows, package manifests, install script, compose / Dockerfiles, plugin contracts, `.semgrep/**`, `SECURITY.md`, `docs/security/**`, `docs/COWORK.md`, `docs/adr/**`, `CONTRIBUTING_AGENT.md`).
  - If ticked, paste a **Why this needs an owner change** paragraph below:

<!-- Why this needs an owner change: ... -->

## Testing

<!-- How were these changes tested? Paste the last ~20 lines of output
where relevant; CI artifact links are also fine. Do not tick a box you
did not actually run. -->

- [ ] `make quality` passes (Python + CLI + Web)
- [ ] `make smoke` succeeds (clean local build + OSS-style up + health checks)
- [ ] `pytest tests/` passes (run this if you touched `docker-compose.yml` or `tests/`)
- [ ] Manual testing (describe):

## AI-assisted contribution attestation

If any material part of this PR was produced with the help of an AI
coding agent, you confirm — by opening this PR — that you followed
[CONTRIBUTING_AGENT.md](../CONTRIBUTING_AGENT.md):

- You read the diff in full and can defend every line.
- You actually ran the verification you ticked above.
- You did not bundle unrelated work.
- You did not weaken offensive-security guard rails (RoE, SafeCommand,
  EngagementContext, OPSEC skills, semgrep rules, compose isolation,
  capability/PID/memory limits) without a linked ADR.

No checkbox is required. The charter applies whether or not you
disclose tool use; this section exists so the expectation is visible at
the point of contribution.

## Related Issues

<!-- Link related issues: Fixes #123, Closes #456 -->
