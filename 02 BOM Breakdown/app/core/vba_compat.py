from __future__ import annotations

import math
import re
from typing import Iterable


VERSION_RE = re.compile(r"^(?P<base>.+?)-V(?P<num>\d+)$", re.IGNORECASE)


def clean_text(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and math.isnan(value):
        return ""
    text = str(value).replace("\u00a0", " ")
    text = re.sub(r"[\t\r\n]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def normalize_compare(value: object) -> str:
    return clean_text(value).casefold()


def normalize_component_key(type_value: object, no_value: object, duplicate_no: int = 0) -> str:
    base = f"{normalize_compare(type_value)}|{normalize_compare(no_value)}"
    if duplicate_no > 0:
        return f"{base}|DUP{duplicate_no:03d}"
    return base


def has_version_suffix(value: object) -> bool:
    return VERSION_RE.match(clean_text(value)) is not None


def get_base_bom(value: object) -> str:
    text = clean_text(value)
    match = VERSION_RE.match(text)
    return match.group("base") if match else text


def get_version_label(version_code: object) -> str:
    text = clean_text(version_code)
    if not text:
        return "V1"
    match = VERSION_RE.match(text)
    return f"V{int(match.group('num'))}" if match else text


def version_number(version_label: object) -> int:
    text = clean_text(version_label).upper()
    match = re.match(r"^V(\d+)$", text)
    if match:
        return int(match.group(1))
    return math.inf


def sort_version_keys(labels: Iterable[str]) -> list[str]:
    return sorted(set(labels), key=lambda x: (version_number(x), clean_text(x)))


def line_sort_value(value: object) -> tuple[int, str]:
    text = clean_text(value)
    try:
        return (0, f"{float(text):020.6f}")
    except ValueError:
        return (1, text)
