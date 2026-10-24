"""Build a deterministic transport ZIP and file manifest; never publishes."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

from check_release import check


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out",type=Path)
    args=parser.parse_args()
    root=Path(__file__).resolve().parents[1]
    out=args.out.resolve() if args.out else root.parent/"tAilorPack.zip"
    check(root)
    files=sorted(p for p in root.rglob("*") if p.is_file()
                 and not any(part in {"__pycache__","runs",".venv",".git","data","build","dist","node_modules",".vercel"}
                             for part in p.relative_to(root).parts)
                 and p.name not in {"MANIFEST.sha256.json","kaggle.json"}
                 and not p.name.startswith(".env") and p.resolve()!=out)
    manifest={p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    manifest_path=root/"MANIFEST.sha256.json"
    manifest_path.write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n")
    out.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(out,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        for path in sorted(files+[manifest_path]):
            info=zipfile.ZipInfo("tAilorPack/"+path.relative_to(root).as_posix(),date_time=(2026,10,23,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=0o100644 << 16
            archive.writestr(info,path.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    print(f"Packaged {len(files)+1} files: {out}")
    print("ZIP SHA-256: "+hashlib.sha256(out.read_bytes()).hexdigest())


if __name__=="__main__":
    main()
