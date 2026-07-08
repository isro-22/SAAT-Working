from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import pandas as pd


@dataclass(frozen=True)
class LineageRef:
    file_hash: str
    sheet: str
    row: int
    col: int | None
    header: str
    parsed_at: str
    parser_ver: str = "0.1.0"
    rule_set: str = "default"


@dataclass
class WorkbookData:
    headers: pd.DataFrame
    lines: pd.DataFrame
    cf: pd.DataFrame
    file_hash: str
    parsed_at: datetime
    header_rows: dict[str, int]
    column_maps: dict[str, dict[str, int]]
    warnings: list[str] = field(default_factory=list)


@dataclass
class SectionPrint:
    base_bom: str
    version_label: str
    version_code: str
    description: str
    rows: pd.DataFrame
    anchor_id: str
    notes: list[str] = field(default_factory=list)
    lineage_refs: list[LineageRef] = field(default_factory=list)


@dataclass
class CFEntry:
    row_idx: int
    code: str
    item_name: str
    family_name: str
    target_versions: list[str]
    status: str
    anchors: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


@dataclass
class DeltaResult:
    base_bom: str
    v_old: str
    v_new: str
    added: list[dict[str, Any]]
    removed: list[dict[str, Any]]
    changed: list[dict[str, Any]]


@dataclass
class GraphData:
    nodes: list[dict[str, Any]]
    edges: list[dict[str, Any]]
    version_label: str
    lineage_refs: list[LineageRef] = field(default_factory=list)
