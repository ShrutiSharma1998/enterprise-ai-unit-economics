# SPDX-License-Identifier: Apache-2.0
"""Break the browser engine on purpose and confirm the tests notice. The original file is always restored.

    python app/build/mutation_check.py

Each mutation changes one rule in app/js/engine.js. The run passes only if the test suite fails for every one.
"""
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
ENGINE = ROOT / "app" / "js" / "engine.js"
MUTATIONS = [
    ("totals not limited to the horizon (team rows)", "const h = m <= hz ? 1 : 0;\n        const st = m >= t.start;", "const h = 1;\n        const st = m >= t.start;"),
    ("outcomes summed over all 60 months", "const hs = (arr) => sum(arr.slice(1, org.horizon + 1));", "const hs = (arr) => sum(arr.slice(1));"),
    ("cache read priced as full input", "t.cached * m.c_read", "t.cached * m.p_in"),
    ("batch discount ignored", "const fb = 1 - t.async_ * (1 - m.batch);", "const fb = 1;"),
    ("headcount allocation uses usage", "\"Headcount proxy\": lics.map((l) => div(l, sum(lics))),", "\"Headcount proxy\": outs.map((o) => div(o, sum(outs))),"),
    ("review share not capped at 100%", "Math.min(1, t.review * P(\"rev_mult\"))", "(t.review * P(\"rev_mult\"))"),
    ("unknown price ID priced at zero", "throw new Error(\"Unknown price ID: \" + pid);", "return 0;"),
    ("committed capacity ignored", "((buy === \"Committed capacity\" && st) ? t.cap_cost : 0)", "0"),
    ("federated duplication ignored", "alloc = flags.map((f) => hubRawTotal * P(\"fed_dup\") * f);", "alloc = flags.map((f) => hubRawTotal * f);"),
]


def suite_passes():
    r = subprocess.run(["node", "--test", str(ROOT / "app" / "tests" / "engine.test.js")], capture_output=True, text=True, cwd=ROOT)
    return r.returncode == 0


def main():
    original = ENGINE.read_text(encoding="utf-8")
    if not suite_passes():
        sys.exit("The tests fail before any mutation. Fix that first.")
    caught = 0
    try:
        for name, old, new in MUTATIONS:
            if original.count(old) != 1:
                sys.exit(f"Mutation pattern must match exactly once ({original.count(old)}): {name}")
            ENGINE.write_text(original.replace(old, new), encoding="utf-8", newline="\n")
            ok = not suite_passes()
            caught += ok
            print(f"{'caught' if ok else 'MISSED'}  {name}")
    finally:
        ENGINE.write_text(original, encoding="utf-8", newline="\n")
    assert suite_passes(), "engine.js was not restored correctly"
    print(f"{caught} of {len(MUTATIONS)} deliberate breakages caught; engine.js restored and the suite passes again")
    sys.exit(0 if caught == len(MUTATIONS) else 1)


if __name__ == "__main__":
    main()
