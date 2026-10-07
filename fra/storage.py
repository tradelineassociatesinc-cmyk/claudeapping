"""Local, private case storage.

Each case is a folder under data/cases/<case_id>/ holding case.json and the
uploaded files. data/ is git-ignored: client data never goes into the repo.
"""
from __future__ import annotations

import os
import shutil
import uuid
from datetime import datetime
from pathlib import Path

from fra.models import Case

DATA_DIR = Path(os.environ.get("FRA_DATA_DIR", Path(__file__).resolve().parent.parent / "data"))
CASES_DIR = DATA_DIR / "cases"


def case_dir(case_id: str) -> Path:
    return CASES_DIR / case_id


def new_case() -> Case:
    case = Case(id=uuid.uuid4().hex[:8])
    save_case(case)
    return case


def save_case(case: Case) -> None:
    folder = case_dir(case.id)
    (folder / "files").mkdir(parents=True, exist_ok=True)
    case.updated_at = datetime.now()
    tmp = folder / "case.json.tmp"
    tmp.write_text(case.model_dump_json(indent=2))
    tmp.replace(folder / "case.json")


def load_case(case_id: str) -> Case:
    return Case.model_validate_json((case_dir(case_id) / "case.json").read_text())


def list_cases() -> list[Case]:
    if not CASES_DIR.exists():
        return []
    cases = []
    for folder in CASES_DIR.iterdir():
        f = folder / "case.json"
        if f.exists():
            try:
                cases.append(Case.model_validate_json(f.read_text()))
            except ValueError:
                continue
    return sorted(cases, key=lambda c: c.updated_at, reverse=True)


def save_upload(case_id: str, doc_id: str, filename: str, data: bytes) -> Path:
    safe = Path(filename).name.replace("/", "_")
    path = case_dir(case_id) / "files" / f"{doc_id}_{safe}"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return path


def upload_path(case_id: str, doc_id: str) -> Path | None:
    folder = case_dir(case_id) / "files"
    matches = list(folder.glob(f"{doc_id}_*")) if folder.exists() else []
    return matches[0] if matches else None


def delete_case(case_id: str) -> None:
    shutil.rmtree(case_dir(case_id), ignore_errors=True)
