"""Fetch and unpack DANE's "Medición de Pobreza Monetaria y Desigualdad" microdata.

DANE's portal asks you to log in (free registration) and accept the terms
before downloading, so the download step is semi-manual:

  1. Open the catalog page for the year (see CATALOG below) -> "Obtener Microdatos".
  2. Either
       a) download the zip(s) in your browser and run
            python data/download.py 2025 --zip ~/Downloads/<file>.zip
     or
       b) copy the direct file link after logging in and run
            python data/download.py 2025 --url "<link>"
          (works only if the link does not need your session cookie)

Files are unpacked to data/raw/<year>/ and a SHA-256 manifest is written so
the exact inputs behind every result are recorded. data/raw/ is gitignored.
"""
from __future__ import annotations

import argparse
import hashlib
import shutil
import sys
import urllib.request
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw"

CATALOG = {
    2025: "https://microdatos.dane.gov.co/index.php/catalog/908/get-microdata",
    2024: "https://microdatos.dane.gov.co/index.php/catalog/874/get-microdata",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def unpack(zip_path: Path, dest: Path, _nested: bool = False) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    before = set(dest.rglob("*.zip"))  # zips already there (e.g. the source zip) are never touched
    with zipfile.ZipFile(zip_path) as zf:
        for m in zf.infolist():
            target = (dest / m.filename).resolve()
            if not str(target).startswith(str(dest.resolve())):
                raise RuntimeError(f"Unsafe path in zip: {m.filename}")
        zf.extractall(dest)
    # nested zips (DANE sometimes ships CSV.zip / SAV.zip inside)
    for inner in set(dest.rglob("*.zip")) - before - {zip_path.resolve(), zip_path}:
        unpack(inner, inner.with_suffix(""), _nested=True)
        inner.unlink()  # only zips that came out of the archive are removed


def write_manifest(dest: Path) -> None:
    lines = [f"{sha256(p)}  {p.relative_to(dest)}"
             for p in sorted(dest.rglob("*"))
             if p.is_file() and p.name not in {"MANIFEST.sha256", ".DS_Store"} and p.suffix != ".zip"]
    (dest / "MANIFEST.sha256").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("year", type=int)
    src = ap.add_mutually_exclusive_group()
    src.add_argument("--zip", type=Path, help="zip downloaded from the DANE portal")
    src.add_argument("--url", help="direct download link")
    args = ap.parse_args()

    dest = RAW / str(args.year)
    if args.zip is None and args.url is None:
        print(f"Log in and download from: {CATALOG.get(args.year, 'https://microdatos.dane.gov.co')}")
        print(f"Then: python data/download.py {args.year} --zip <path-to-zip>")
        return 1

    if args.url:
        dest.mkdir(parents=True, exist_ok=True)
        zip_path = dest / "download.zip"
        print(f"Downloading {args.url}")
        with urllib.request.urlopen(args.url) as r, open(zip_path, "wb") as fh:
            shutil.copyfileobj(r, fh)
    else:
        zip_path = args.zip.expanduser()

    unpack(zip_path, dest)
    if args.url:
        zip_path.unlink()
    write_manifest(dest)
    print(f"Unpacked to {dest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
