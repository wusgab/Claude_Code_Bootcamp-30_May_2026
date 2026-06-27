# Code Review Rubric — AI-Generated Code

One page. Eight yes/no checks, each answerable in ≤ 30 seconds by reading the
diff. Tuned for the failure modes LLMs hit most: untested boundaries, skipped
error paths, and silent assumptions about types and shapes. **Any "No" blocks
merge** until fixed or explicitly waived with a reason.

> How to use: read each check, answer Yes/No, jot the line number on a No.
> If a check isn't applicable, mark N/A and move on.

---

### 1. Boundaries — are the edges exercised, not just the happy middle?
Empty input, zero, one, off-by-one, max length, last element, the `n+1`th item.
**Yes if** the code (and/or a test) clearly handles empty/`0`/single-item cases,
not only the typical multi-item path.
*Why it catches Claude:* it writes for the representative case and quietly drops the extremes.

### 2. Error paths — does every failure return or raise, with nothing swallowed?
Find each call that can fail (I/O, DB, parse, network, lookup). Trace what
happens when it does.
**Yes if** every failure surfaces (raised, returned, logged-and-handled) and no
`except` block silently passes or returns a misleading success.
*Why:* Claude tends to write the success branch fully and stub or omit the failure branch.

### 3. Type & shape assumptions — would surprising-but-valid input break it?
`None`/`null`, `""` vs absent, `0`/`False` vs missing, string-vs-int, a list
where a scalar was assumed, a dict missing a key.
**Yes if** falsy-but-valid values and type coercions are handled deliberately
(e.g. `if x is None:` not `if not x:` when `0`/`""` are legal).
*Why:* Claude conflates "falsy" with "absent" and assumes inputs match the declared type.

### 4. State & ordering — is the result independent of run order and prior state?
Shared globals, module-level singletons, caches, DB rows, file contents,
monkeypatches that must revert.
**Yes if** each unit starts from known state and leaves no residue that changes
the next run's outcome.
*Why:* Claude reuses module-level state and assumes a clean slate that real runs don't provide.

### 5. Hidden contracts — is the *real* production path the one being run?
Lifespan/startup hooks, migrations, auth middleware, env-dependent config,
framework magic (ASGI lifespan, DI, decorators).
**Yes if** the code/tests go through the same wiring production uses — not a
shortcut that bypasses setup the real entrypoint depends on.
*Why:* Claude hand-rolls setup in tests, so the wiring it skipped can break in prod while tests stay green.

### 6. External input safety — is untrusted data validated before use?
User/query/path params reaching SQL, shell, paths, format strings, or
deserialization. Wildcards, separators, and injection metacharacters.
**Yes if** inputs are parameterized/escaped/validated and special characters
(`%`, `_`, `..`, quotes, `;`) can't change the operation's meaning.
*Why:* Claude interpolates inputs into queries/commands and forgets metacharacters are live.

### 7. Resource & lifecycle hygiene — is everything opened also closed?
Files, DB connections, sockets, locks, temp files, background tasks.
**Yes if** every acquired resource is released on both success and error paths
(context manager / `finally` / explicit close), with no leak on early return.
*Why:* Claude opens resources in the happy path and forgets the error/early-exit cleanup.

### 8. Claim vs. reality — does the code actually do what the message says?
Compare the PR/commit description to the diff. Look for "handles X", "tested",
"validates Y" claims.
**Yes if** each claim maps to real code/tests in the diff — no aspirational
comments, TODOs masquerading as done, or asserts that can't fail.
*Why:* Claude narrates intended behavior confidently even when the diff only partially delivers it.

---

**Scoring:** 8/8 Yes → merge. Any No → fix or record an explicit waiver
(`waived: <reason>`) in the review thread. Two or more Nos in checks 1–3 →
request a focused round on boundaries/errors/types before re-review.
