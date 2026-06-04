# Charter for AI-Assisted Contributions

> If you used an AI agent (Claude, Codex, Copilot, Cursor, Gemini, an
> in-house tool — anything that drafts code or prose) to produce any
> material part of a contribution to Decepticon, this document is the
> contract you are operating under. It supplements [CONTRIBUTING.md](CONTRIBUTING.md),
> [docs/COWORK.md](docs/COWORK.md), and [SECURITY.md](SECURITY.md); it
> does **not** replace them.

Decepticon is an offensive security platform whose own offensive agents
operate under explicit Rules of Engagement. The contribution stream that
*builds* the platform deserves the same discipline. Without it, the
volume that AI assistance enables silently lowers the quality bar — and
on a tool of this class, that is the problem the project exists to
solve, in miniature.

The rules below are not aspirational. They are conditions of merge.

---

## 1. The hard rules

These are non-negotiable. A PR that violates any of them will be closed
without review, regardless of how green CI is.

1. **You commit under your own identity.** No `Co-Authored-By: Claude`,
   `Co-Authored-By: Copilot`, or any other AI co-author trailer. (Already
   enforced socially per [docs/COWORK.md §4.5](docs/COWORK.md); restated
   here so the rule is also visible from the AI-contributor entry point.)
   You used a tool. You are still the author and the reviewer-of-record.
2. **You read the diff in full before opening the PR.** Every line. If
   you have not read it, you cannot defend it, and you should not be
   asking a maintainer to.
3. **You ran the verification you are claiming.** The Testing checklist
   in the PR template is a statement of fact, not an aspiration. If you
   ticked `make quality passes`, you ran it and it passed on the exact
   tree you are pushing. False attestations are a trust violation and
   are treated as such.
4. **You do not bundle unrelated work.** "While I was in there" changes
   go in a separate PR. AI assistants love to drive-by-refactor; you are
   the gate that says no. See [docs/COWORK.md §4.5](docs/COWORK.md) on
   mega-PRs.
5. **You do not weaken the offensive-security guard rails by accident.**
   Specifically:
   - You did not remove or soften wording in `packages/decepticon/decepticon/skills/shared/opsec/**`,
     RoE enforcement, `SafeCommand`, `EngagementContext`, or any
     `decepticon-no-*` Semgrep rule under `.semgrep/` without an
     accompanying ADR and an explicit threat-model paragraph in the
     PR body.
   - You did not add a tool to a skill's `allowed-tools:` frontmatter
     without naming, in the PR body, what capability that opens to
     every agent that loads the skill.
   - You did not relax `cap_drop` / `no-new-privileges` / `mem_limit`
     / `pids_limit` / network membership in `docker-compose.yml`
     without an ADR.

If any of the above hits, stop. Open an issue or draft ADR first.

---

## 2. The self-review checklist

Run these on yourself, in order, before requesting human review. They
mirror the questions a maintainer will ask; doing them yourself is the
cheapest way to land your PR.

### 2.1 Intent

- [ ] **The PR references an issue, ADR, or release-blocker.** Title
      alone is not enough — the body links the thing this change is
      meant to satisfy. Speculative refactors land as draft PRs against
      an ADR, not as merge-ready PRs against `main`.
- [ ] **You can name, in one sentence, the change in observable
      behavior** (or the explicit "this is a no-op refactor; behavior is
      preserved" claim).
- [ ] **You can name the anti-goal**: one thing this PR could plausibly
      have done but deliberately does not. ("Did not also fix the
      adjacent bug." "Did not change the public type.") If you cannot
      name an anti-goal, your PR is probably too broad.

### 2.2 Scope and shape

- [ ] Every changed file traces directly to the stated intent. If a
      file is in the diff that does not, remove it.
- [ ] You have not renamed symbols, reordered imports, reflowed strings,
      or normalized whitespace outside the files your change required.
- [ ] Diff is the minimum that achieves the goal. If the AI produced
      200 lines and 50 would do it, you rewrote it down to 50 before
      pushing.
- [ ] No `TODO`, `FIXME`, stub, mock, or `raise NotImplementedError`
      shipped as part of a delivered feature. Unfinished work is closed
      out, deferred to a tracked issue, or kept on the branch.

### 2.3 Blast-radius classification

Tick the row that best matches your change. The CODEOWNERS file is the
ground truth — this is a fast self-check, not a substitute.

- [ ] **Tier-auto** — tests, internal refactors with no public-API
      change, docs that are not policy docs, dependency bumps in
      `uv.lock` / lockfiles only. Self-merge on green CI is the
      expected path.
- [ ] **Tier-delegate** — agent prompts, skill bodies, middleware
      internals, web/CLI features. Expect review from a maintainer or a
      delegated reviewer; CI green is necessary but not sufficient.
- [ ] **Tier-owner (CODEOWNERS-gated)** — `.github/workflows/**`,
      `pyproject.toml` / `uv.lock` / `package*.json` / `go.{mod,sum}`,
      plugin contracts under `packages/decepticon-core/.../contracts/**`,
      `scripts/install.sh`, `docker-compose.yml`,
      `containers/*.Dockerfile`, `.semgrep/**`, `SECURITY.md`,
      `docs/security/**`, `docs/COWORK.md`, `docs/adr/**`,
      `CONTRIBUTING_AGENT.md`. **You will wait for owner review.** Do
      not ping for a faster turnaround; the owner gate exists because
      these surfaces have outsized blast radius.

If you ticked Tier-owner, also confirm:

- [ ] The PR body has a section titled **Why this needs an owner
      change**, naming the surface and the specific invariant being
      touched. Generic "improving X" descriptions are not enough.

### 2.4 Verification

- [ ] You actually ran the Testing checklist in the PR template. Paste
      the relevant output (last ~20 lines of `make quality`) in the PR
      body or as a CI artifact link. If you cannot run a command
      locally, say so explicitly; do not tick the box.
- [ ] If you added or modified a test, you saw it fail without your
      change and pass with it. (For bug fixes, the failing-then-passing
      test sequence should be visible in the commit history of the PR
      branch — do not squash it away locally.)
- [ ] If you touched `docker-compose.yml`, you ran
      `pytest tests/test_compose_network_isolation.py` locally (or the
      whole `tests/` suite). The isolation invariants are not negotiable.
- [ ] If you touched any agent prompt under `packages/decepticon/decepticon/agents/**/prompts/`,
      you read the diff yourself and confirmed that no DO/DON'T item
      from [tradecraft & OPSEC](https://docs.decepticon.red/en/concepts/tradecraft)
      was weakened. (Prompts are not covered by Python tests; the
      review is on you.)

### 2.5 Honesty

- [ ] You marked claims about external behavior as `[INFERENCE]` (or
      equivalent) when you have not directly observed them.
- [ ] You did not paper over a failing check by retrying CI, skipping a
      test, removing a Semgrep rule, or moving code into an excluded
      path. If a guard rail fires, that is a signal — fix the underlying
      issue or open a separate PR that explicitly relaxes the rule with
      a justification a maintainer can approve.

---

## 3. Patterns AI assistants get wrong here

Symptoms a maintainer will catch if you do not. Save the round-trip by
catching them yourself first.

| Pattern | Why it bites Decepticon |
|---|---|
| Adding a `try/except Exception: pass` to "make a test pass" | Hides real failures in sandbox / network / LLM call paths where flakes are signal. |
| Inserting `if not …: return None` defaults instead of raising | RoE / OPPLAN code that silently returns `None` produces ghost objectives downstream. Fail loud. |
| "Helpfully" widening a function's signature with a new optional kwarg | Public-API surface change; needs a CODEOWNERS review on plugin contracts. |
| Replacing `assert` with `if ... raise ...` *everywhere* | Already covered by `decepticon-no-assert-in-prod` for the right paths. Do not bulk-rewrite. |
| Adding a new dependency to fix a small thing | Supply-chain change. Justify in the PR body or remove the dep and inline the small thing. |
| Generating a long Mermaid diagram or architecture doc as part of a code PR | Land docs separately. Mixed PRs make review pathological. |
| Reformatting unrelated files because the formatter "thought they were dirty" | Revert. Match existing formatting; do not normalize the tree. |

---

## 4. When in doubt

- For architecture-level questions: open a draft ADR (see
  [docs/adr/template.md](docs/adr/template.md)) and link it in the PR.
  An ADR with `Status: Proposed` is the right artifact for "I think we
  should do X; here is the context."
- For security-sensitive questions: open a private report per
  [SECURITY.md](SECURITY.md). Do not open a public issue with a working
  exploit narrative.
- For "is this in scope": open an issue first. A small issue conversation
  is cheaper than a large PR that gets closed.

---

## 5. Why this exists

Tests passing is necessary; it is not sufficient. Decepticon's value
proposition rests on the philosophy in
[docs/red-team/operations.md](docs/red-team/operations.md), the
isolation in [docs/security/sandbox-isolation.md](docs/security/sandbox-isolation.md),
and the tradecraft in the published docs. None of those are
test-enforceable in their entirety. They are enforced by the people who
review the PR — and, when the PR was AI-assisted, by the person who
opened it being willing to defend every line.

If you cannot, do not open the PR yet.
