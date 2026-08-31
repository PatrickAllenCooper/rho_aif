"""Guarded string-replacement applier for manuscript edits.

Failure mode this exists to prevent (observed twice, both reached the PDFs):
when `new` contains `old` as a substring, running the same replacement a
second time appends instead of no-opping, duplicating a sentence or clause.
"""
import re


def apply(paths, reps, report=True):
    results = {}
    for path in paths:
        s = open(path).read()
        applied, skipped, refused = 0, [], []
        for old, new in reps:
            c = s.count(old)
            if c == 0:
                skipped.append(("absent", old[:60]))
                continue
            if c > 1:
                refused.append(("ambiguous x%d" % c, old[:60]))
                continue
            # Guard: if new contains old, the edit is non-idempotent. Refuse
            # when the intended result is already present.
            if old in new and new in s:
                refused.append(("already-applied", old[:60]))
                continue
            # Guard: refuse replacement text that is an INSTRUCTION rather than
            # prose. A reviewer's suggested_fix once reached the manuscript
            # verbatim ("Add a bibliography entry for ... and cite it at ...").
            INSTRUCTION = (
                "add a bibliography entry", "replace the", "change \"", "change the",
                "e.g.,", "e.g. ", "for example, write", "rewrite the", "delete the",
                "propagate to", "apply identically", "suggested fix", "should read",
            )
            low = new.lower()
            if any(t in low for t in INSTRUCTION):
                refused.append(("looks-like-instruction", new[:70]))
                continue
            s = s.replace(old, new)
            applied += 1
        open(path, "w").write(s)
        # Post-check: no consecutive duplicate sentences, no comma stutters.
        body = "\n".join(l for l in s.split("\n") if not l.strip().startswith("%"))
        sents = [x.strip() for x in re.split(r"(?<=\.)\s+", body) if len(x.strip()) > 50]
        seen, dups = {}, []
        for i, x in enumerate(sents):
            k = re.sub(r"\s+", " ", x)
            if k in seen and i - seen[k] <= 2:
                dups.append(k[:80])
            seen[k] = i
        stutter = re.findall(r"\b(\w+ \w+), \1\b", body)
        results[path] = dict(applied=applied, skipped=skipped, refused=refused,
                             dup_sentences=dups, stutters=stutter)
        if report:
            print(f"{path}: applied {applied}, skipped {len(skipped)}, refused {len(refused)}, "
                  f"dups {len(dups)}, stutters {len(stutter)}")
            for r in refused:
                print("   REFUSED:", r)
            for dcheck in dups:
                print("   DUP:", dcheck)
    return results
