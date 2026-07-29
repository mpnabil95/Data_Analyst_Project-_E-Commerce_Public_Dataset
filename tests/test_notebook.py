"""Eksekusi notebook kandidat rilis dari working directory repository."""

from __future__ import annotations

from pathlib import Path

import nbformat
import pytest
from nbclient import NotebookClient

REPO_ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_PATH = REPO_ROOT / "notebooks" / "ecommerce_analysis.ipynb"

pytestmark = [pytest.mark.slow, pytest.mark.notebook]


def test_notebook_executes_all_code_cells() -> None:
    notebook = nbformat.read(NOTEBOOK_PATH, as_version=4)
    code_cells = [cell for cell in notebook.cells if cell.cell_type == "code"]

    assert len(notebook.cells) == 74
    assert len(code_cells) == 19

    client = NotebookClient(
        notebook,
        timeout=600,
        kernel_name="python3",
        resources={"metadata": {"path": str(REPO_ROOT)}},
        allow_errors=False,
        record_timing=False,
    )
    executed = client.execute()
    executed_code = [cell for cell in executed.cells if cell.cell_type == "code"]

    assert [cell.execution_count for cell in executed_code] == list(range(1, 20))
    assert not [
        output
        for cell in executed_code
        for output in cell.get("outputs", [])
        if output.get("output_type") == "error"
    ]
