from __future__ import annotations

from datetime import datetime

import pandas as pd

from .models import LineageRef


def ref_for_cell(
    row: pd.Series,
    *,
    sheet: str,
    header: str,
    column_maps: dict[str, dict[str, int]],
    file_hash: str,
    parsed_at: datetime,
) -> LineageRef:
    return LineageRef(
        file_hash=file_hash,
        sheet=sheet,
        row=int(row.get("__source_row", 0) or 0),
        col=column_maps.get(sheet, {}).get(header),
        header=header,
        parsed_at=parsed_at.isoformat(timespec="seconds"),
    )


def refs_for_row(
    row: pd.Series,
    *,
    sheet: str,
    headers: list[str],
    column_maps: dict[str, dict[str, int]],
    file_hash: str,
    parsed_at: datetime,
) -> list[LineageRef]:
    return [
        ref_for_cell(
            row,
            sheet=sheet,
            header=header,
            column_maps=column_maps,
            file_hash=file_hash,
            parsed_at=parsed_at,
        )
        for header in headers
    ]
