"""Parent verification: real scripts, full receipts, no PHP on Windows.

This command writes only production/T-01/preuves. It never prepares an image.
Exit 0 means the real PHP suite and all tooling checks passed; 1 means NOT READY.
"""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "production/T-01/preuves"


def hashes(paths):
    return {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(paths) if p.is_file()}


def run(item):
    name, relative = item
    command = ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", relative]
    result = subprocess.run(command, cwd=ROOT, capture_output=True, timeout=720)
    data = result.stdout + result.stderr
    (OUT / ("final-" + name + ".log")).write_bytes(data)
    text = data.decode("utf-8", errors="replace")
    receipt = {"command": command, "exit_code": result.returncode,
               "stdout_sha256": hashlib.sha256(result.stdout).hexdigest(),
               "stderr_sha256": hashlib.sha256(result.stderr).hexdigest()}
    if name == "rejeu":
        lines = [line for line in text.splitlines() if line.strip()]
        receipt["last_line"] = lines[-1] if lines else ""
        receipt["summary_valid"] = bool(re.fullmatch(
            r"REJEU : \d+ tests, \d+ assertions, \d+ échecs, \d+ erreurs, \d+ ignorés — (PASS|FAIL)",
            receipt["last_line"]))
    return name, receipt


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    library_files = list((ROOT / "wp/plugins").rglob("*"))
    source_files = list((ROOT / "wp/tests/t01").rglob("*")) + [ROOT / "wp/tests/rejouer.ps1", ROOT / "wp/tests/preparer-image.ps1"]
    before = hashes(library_files + source_files)
    items = [("contrat", "wp/tests/t01/test-rejeu.ps1"),
             ("isolation", "wp/tests/t01/test-isolation.ps1"),
             ("rejeu", "wp/tests/rejouer.ps1")]
    with ThreadPoolExecutor(max_workers=3) as pool:
        results = dict(pool.map(run, items))
    after_files = list((ROOT / "wp/plugins").rglob("*")) + list((ROOT / "wp/tests/t01").rglob("*")) + [ROOT / "wp/tests/rejouer.ps1", ROOT / "wp/tests/preparer-image.ps1"]
    unchanged = before == hashes(after_files)
    ready = unchanged and all(r["exit_code"] == 0 for r in results.values()) and results["rejeu"]["summary_valid"]
    receipt = {"time_utc": datetime.now(timezone.utc).isoformat(), "ready": ready,
               "immutable_libraries_and_runner_unchanged": unchanged,
               "source_sha256": before, "results": results,
               "preparation_executed": False,
               "limitations": [] if ready else ["See final-rejeu.log: the real suite must PASS; boundary doubles and isolation checks do not replace it."]}
    (OUT / "final-verification.json").write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for name, result in results.items():
        print(name + ": exit=" + str(result["exit_code"]) + " ; full output=production/T-01/preuves/final-" + name + ".log")
    print(results["rejeu"]["last_line"])
    print("T01 READY" if ready else "T01 NOT READY — no PRET")
    return 0 if ready else 1


if __name__ == "__main__":
    raise SystemExit(main())
