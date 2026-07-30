"""Pemeriksaan checksum, dokumentasi, credential pattern, dan hygiene rilis."""

from __future__ import annotations

import hashlib
import re
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]

EXPECTED_DATA = {
    "customers_dataset.csv": (
        9_033_957,
        "983a422239e1712ded753b3bf9ecf47dc73f144d306029dcfa99e70a226883d2",
    ),
    "geolocation_dataset.csv": (
        61_273_883,
        "b514f6fc991b9566aeba02aa5d67e2c3630f034b60a0e05aa0d082a3b66d88d6",
    ),
    "order_items_dataset.csv": (
        15_438_671,
        "0bc4d068c4fe38cbb01bd90e8746e3c613fe7b4baef75fab7b0e329701c3e279",
    ),
    "order_payments_dataset.csv": (
        5_777_138,
        "4f713964f2815dbbaa40b9488268c55aac3627bfce5aa96cf58d1f3616de3cc0",
    ),
    "order_reviews_dataset.csv": (
        14_346_950,
        "81336b6e5183133b632a3d9ed899428e33430987fa540926a6daa8b4a2157598",
    ),
    "orders_dataset.csv": (
        17_654_914,
        "8df58ef3d2d7e9944010f7beecd9b75367f5588ec6e3c91cec19ae3345ef9ecf",
    ),
    "product_category_name_translation.csv": (
        2_542,
        "9da093e114e517534d7a6903b253b0d24a582830b99ea9e8ef48a90b79d60967",
    ),
    "products_dataset.csv": (
        2_379_446,
        "3e6569628a17fbc75fd206ee357b59e20364b9afa90f5b6cd5b4d624c58aa9cc",
    ),
    "sellers_dataset.csv": (
        174_703,
        "1f643d2b950373b85735e7794b20986f528d7a000432e7c6f9bcbb44d0846a0e",
    ),
}

LOCAL_LINK = re.compile(r"!?\[[^\]]*]\(([^)]+)\)")
SECRET_PATTERNS = {
    "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"),
    "AWS access key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "GitHub token": re.compile(r"\b(?:github_pat_|gh[pousr]_)[A-Za-z0-9_]{20,}\b"),
    "Slack token": re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b"),
    "OpenAI-style key": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
}
TEXT_SUFFIXES = {
    "",
    ".gitignore",
    ".ipynb",
    ".json",
    ".md",
    ".py",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}


def _tracked_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
    )
    return [
        REPO_ROOT / relative.decode("utf-8")
        for relative in result.stdout.split(b"\0")
        if relative
    ]


@pytest.mark.slow
def test_dataset_sizes_and_checksums() -> None:
    for filename, (expected_size, expected_hash) in EXPECTED_DATA.items():
        path = REPO_ROOT / "data" / filename
        payload = path.read_bytes()

        # Git pada Windows dapat checkout CSV text sebagai CRLF. Hash inventaris
        # menggunakan LF, sehingga non-LFS dinormalisasi tanpa mengubah file.
        # Geolocation ditandai `-text` dan wajib identik byte-per-byte dengan
        # objek Git LFS.
        canonical = (
            payload
            if filename == "geolocation_dataset.csv"
            else payload.replace(b"\r\n", b"\n")
        )
        assert len(canonical) == expected_size
        assert hashlib.sha256(canonical).hexdigest() == expected_hash


def test_no_forbidden_release_artifacts_are_tracked() -> None:
    tracked = {
        path.relative_to(REPO_ROOT).as_posix()
        for path in _tracked_files()
    }
    forbidden_parts = {
        ".env",
        ".pytest_cache",
        ".venv",
        "__pycache__",
        "htmlcov",
        "outputs",
        "secrets.toml",
    }

    violations = sorted(
        relative
        for relative in tracked
        if any(part in forbidden_parts for part in Path(relative).parts)
        or relative.endswith((".log", ".pyc", ".tmp"))
    )
    assert not violations


def test_tracked_text_has_no_known_credential_pattern() -> None:
    findings: list[str] = []
    for path in _tracked_files():
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8")
        for label, pattern in SECRET_PATTERNS.items():
            if pattern.search(text):
                findings.append(f"{path.relative_to(REPO_ROOT)}: {label}")
    assert not findings


def test_markdown_local_links_resolve() -> None:
    broken: list[str] = []
    markdown_files = [REPO_ROOT / "README.md", *(REPO_ROOT / "docs").glob("*.md")]

    for markdown_file in markdown_files:
        text = markdown_file.read_text(encoding="utf-8")
        for raw_target in LOCAL_LINK.findall(text):
            target = raw_target.strip().split(maxsplit=1)[0].strip("<>")
            if (
                not target
                or target.startswith(("#", "http://", "https://", "mailto:"))
            ):
                continue
            relative_target = target.split("#", 1)[0]
            resolved = (markdown_file.parent / relative_target).resolve()
            if not resolved.exists():
                broken.append(
                    f"{markdown_file.relative_to(REPO_ROOT)} -> {target}"
                )

    assert not broken
