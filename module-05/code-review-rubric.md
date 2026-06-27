# Code Review Rubric — AI-Generated Code

One pass, ~3 minutes. Answer each **yes/no** in ≤30s. **Any "no" = stop and fix
before merge.** Tuned for the failure modes AI models (incl. Claude) miss most:
boundaries, error paths, and silent assumptions about types and input shape.

> Tip: a "yes" must be *checkable*, not hopeful. If you can't point at the line
> that makes it true in 30s, score it "no."

---

### 1. Empty / boundary inputs — does it handle `0`, `""`, `[]`, and one-past-the-end?
Look for the empty collection, the zero-length string, the single-element list,
and the last index. AI code loves the happy middle and skips the edges.
**Yes** if each edge has a visible branch or is provably safe. **No** if untested.

### 2. Error paths — is every failure surfaced, not swallowed or faked?
Find each `try`, external call, and "not found" branch. Does the error go to the
caller (right status/exit code/stderr), or get caught-and-ignored, returned as a
fake success, or printed to the wrong stream? **Yes** = failures are visible.

### 3. Null / missing — what happens when a lookup returns nothing?
Every DB row, dict `get`, regex match, or API field can be `None`/absent. Is the
"not there" case handled *before* the value is used (no attribute/key access on
`None`)? **Yes** = the empty result has its own path.

### 4. Type & coercion assumptions — does it trust the shape of its inputs?
Does it assume a str is non-empty, an int won't overflow/parse-fail, a list is
sorted, or user text contains no special characters (quotes, `%`, `_`, newlines,
unicode)? **Yes** = inputs are validated/escaped, not assumed.

### 5. Hidden state & side effects — does it mutate anything it doesn't restore?
Global vars, module attributes, shared caches, env, files, the passed-in object.
Is each mutation either local, or cleaned up/restored after use? **Yes** = no
surprise leftovers for the next caller or test.

### 6. Off-by-one & range — are all loop/index/slice bounds correct?
Check `<` vs `<=`, `range(n)` vs `range(n+1)`, slice ends, and pagination/limit
math. Spot-check the first and last iteration by hand. **Yes** = bounds verified.

### 7. Concurrency & resource cleanup — are shared resources safe and released?
Connections/files/locks closed on every path (incl. errors)? Any shared mutable
state touched by concurrent requests/threads without protection? **Yes** = every
resource has a guaranteed close and no unguarded shared writes.

### 8. Claims vs. reality — does it actually do what its name/comment/docs say?
Read the function name, docstring, and any README/spec line, then the body. Do
they match? AI often writes a correct-sounding label over subtly different
behavior (e.g. "full replace" that's really a partial update). **Yes** = aligned.

---

**Score:** ___ / 8 yes. Merge only at 8/8, or with each "no" explicitly waived
and noted in the PR.
