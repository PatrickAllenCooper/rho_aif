# Historical claim-checker repair

The editorial regression run initially passed five tests and failed the preserved historical regression against commits `4adc223..247a10c`. The failure is saved in `pytest_editorial_initial_failure.txt`. The historical wrong-table claim was no longer detected because `--head` selected historical added lines but resolved their labels and CSV context from today's working tree. The appendix cuts removed the current table and exposed that defect.

The checker now resolves `--head` to a commit and reads source context, table inventory/content, and result CSV inventory/content from that same revision. Normal working-tree checking retains its previous behavior. Immutable historical text and inventories are cached. Invalid head revisions fail explicitly. No experimental algorithm or result value changes.

A new regression test creates and commits a small independent Git repository, then deletes its historical table and CSV and changes the live manuscript. The historical check must still detect the original table-content error, resolve its reference, and find its numerical value using the historical source-level CSV scope. The working-tree helpers must see the deletions and new source. The existing real-commit regression is unchanged and passes.

Validation: all seven focused tests pass. The complete suite passes 541 tests with 26 pre-existing warnings in 168.67 seconds. The final manuscript run has no hard failures. Its 24 numeric advisory occurrences are the same independently adjudicated cases documented in `independent_evidence_review.md`; the checker intentionally does not suppress these context-dependent advisories.
