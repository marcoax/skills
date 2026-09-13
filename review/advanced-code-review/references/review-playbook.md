# Scope and verification mechanics

Read the relevant section when resolving a comparison or designing an experiment.

## Capture the reviewed state

| Scope | Evidence |
|---|---|
| File | Review the requested file as it stands, or its diff when the request asks for changes. An empty diff does not authorize switching to a previous commit. |
| Uncommitted | Include staged, unstaged, and relevant untracked files; record the state reviewed. |
| Commit | Inspect the named commit and record its SHA. |
| Branch | Record base and head SHAs. For changes introduced by a branch, compare its merge-base with the target against the head (`git diff <base>...<head>`); use endpoint comparison only when that is the intended question. |

Without a Git repository, review supplied files or patches and state the missing history. Ask for a
repository only when the requested comparison depends on it. A large diff calls for organizing the
review, not automatically asking the user to approve each file.

## Counterfactual checks

An experiment can resolve whether a test detects a defect or whether a disputed change is necessary.
Use one when inspection leaves a material uncertainty; it is not a prerequisite for every finding.

Run mutations in an isolated copy or disposable worktree containing the exact reviewed state,
including relevant uncommitted and untracked inputs. Preserve the user's working tree. Use local,
disposable resources within the session's authorization and clean up only resources you created.
If isolation or a required dependency is unavailable, state the limitation instead of modifying
unrelated work. A dirty working tree alone does not prevent review or non-mutating checks.

Compare failures with the baseline when attribution is uncertain. A matching exit code is insufficient:
compare the actual failing behavior. Record an unresolved attribution as a verification limitation,
not as a proven regression or a proven baseline failure.

For scope questions, consider the implementation's dependency on a change as well as test results:
a passing suite after removal does not by itself prove the removed code was unnecessary.
