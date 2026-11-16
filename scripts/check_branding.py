"""Check tracked and new publishable files, including dotfiles, for retired display names."""
from __future__ import annotations
import argparse,fnmatch,json,re,subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
POLICY_PATH="scripts/branding_compatibility.json"
RETIRED=re.compile(r"dev[ _-]?flow",re.IGNORECASE)

def scan(root=ROOT):
    rules=json.loads((root/POLICY_PATH).read_text(encoding="utf-8"))["rules"]
    names=subprocess.check_output(["git","-C",str(root),"ls-files","--cached","--others","--exclude-standard","-z"]).decode().split("\0")
    findings=[];retained=[];scanned=0
    for name in sorted(set(filter(None,names))):
        path=root/name
        if name==POLICY_PATH or not path.is_file():continue
        try:text=path.read_bytes().decode("utf-8")
        except UnicodeDecodeError:continue
        scanned+=1
        for number,line in enumerate(text.splitlines(),1):
            if not RETIRED.search(line):continue
            remainder=line
            for rule in rules:
                if name=="docs/branding.md" or any(fnmatch.fnmatchcase(name,p) for p in rule["paths"]):
                    remainder=re.sub(rule["pattern"],"",remainder)
            record={"path":name,"line":number}
            if RETIRED.search(remainder):findings.append(record)
            else:retained.append(record)
    return {"passed":not findings,"scanned_text_files":scanned,"unapproved_legacy_references":findings,
            "documented_compatibility_lines":len(retained),"policy":POLICY_PATH}

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument("--json",action="store_true");args=parser.parse_args()
    report=scan()
    print(json.dumps(report,ensure_ascii=False,indent=2))
    return 0 if report["passed"] else 1

if __name__=="__main__":raise SystemExit(main())
