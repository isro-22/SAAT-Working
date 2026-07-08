"""Data loading, search, and retrieval for the flavor chemical database."""

from __future__ import annotations

import json
import gzip
import re
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_FILE = PROJECT_ROOT / "data" / "materials_final.json"
COMPRESSED_DATA_FILE = DATA_FILE.with_suffix(".json.gz")
AINSIGHTS_DISCLOSURE_MARKER = "about flavscents ainsights (disclosure)"
AINSIGHTS_DISCLOSURE_END_PATTERN = re.compile(r"Generated GMT \(p\)", flags=re.IGNORECASE)
DESCRIPTOR_STOP_WORDS = {
    "and",
    "at",
    "from",
    "high",
    "hour",
    "hours",
    "in",
    "less",
    "luebke",
    "recommend",
    "resources",
    "sample",
    "smelling",
    "solution",
    "strength",
    "substantivity",
    "tgsc",
    "the",
    "william",
}

SEARCH_FIELD_GROUPS: dict[str, tuple[str, ...]] = {
    "All fields": (
        "name",
        "synonyms",
        "occurrence",
        "organoleptic_notes",
        "odor",
        "flavor",
        "fema",
        "cas",
        "einecs",
        "jecfa_food_flavoring",
        "jecfa_food_additive",
    ),
    "Name": ("name",),
    "Synonym": ("synonyms", "synonym"),
    "Occurrence": ("occurrence",),
    "Organoleptic": ("organoleptic_notes", "odor", "flavor"),
    "FEMA": ("fema",),
    "CAS": ("cas",),
    "EINECS": ("einecs",),
    "JECFA": ("jecfa_food_flavoring", "jecfa_food_additive"),
}


def clean_value(value: Any, fallback: str = "N/A") -> str:
    if value is None:
        return fallback
    if isinstance(value, list):
        value = " | ".join(clean_value(item, "") for item in value)
    elif isinstance(value, dict):
        value = " | ".join(f"{key}: {clean_value(val, '')}" for key, val in value.items())
    else:
        value = str(value)

    value = strip_ainsights_disclosure(value)
    value = " ".join(value.replace("\u00c2", "").split())
    if not value or value.strip().lower() in {"n/a", "na", "none", "null"}:
        return fallback
    return value.strip()


def strip_ainsights_disclosure(value: str) -> str:
    marker_index = value.lower().find(AINSIGHTS_DISCLOSURE_MARKER)
    if marker_index == -1:
        return value

    tail = value[marker_index:]
    end_match = AINSIGHTS_DISCLOSURE_END_PATTERN.search(tail)
    if end_match:
        remove_end = marker_index + end_match.end()
        return (value[:marker_index] + value[remove_end:]).strip()

    return value[:marker_index].strip()


def split_list_value(value: Any) -> list[str]:
    text = clean_value(value, "")
    if not text:
        return []
    parts = []
    for chunk in text.replace("\n", " | ").split("|"):
        cleaned = clean_value(chunk, "")
        if cleaned:
            parts.append(cleaned)
    return parts


def format_synonyms(value: Any) -> str:
    synonyms = split_list_value(value)
    return "\n".join(synonyms) if synonyms else "N/A"


def format_organoleptic_text(value: Any) -> str:
    text = clean_value(value, "")
    if not text:
        return "N/A"

    text = re.sub(r"\s*\|\s*", "\n", text)
    text = re.sub(
        r"\s+(Odor Type|Odor Strength|Odor Description|Substantivity|Odor sample from|Flavor Type|Flavor Description):",
        r"\n\1:",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(r"(^|\s)(\d+\.)\s+", r"\1\n\2 ", text)
    lines = [clean_value(line, "") for line in text.splitlines()]
    return "\n".join(line for line in lines if line) or "N/A"


def _text_for_fields(item: dict[str, Any], fields: tuple[str, ...]) -> str:
    return " ".join(clean_value(item.get(field), "") for field in fields).lower()


@lru_cache(maxsize=1)
def load_materials() -> tuple[dict[str, Any], ...]:
    if DATA_FILE.exists():
        with DATA_FILE.open(encoding="utf-8") as file:
            data = json.load(file)
    elif COMPRESSED_DATA_FILE.exists():
        with gzip.open(COMPRESSED_DATA_FILE, mode="rt", encoding="utf-8") as file:
            data = json.load(file)
    else:
        raise FileNotFoundError(
            f"Material data file not found: {DATA_FILE} or {COMPRESSED_DATA_FILE}"
        )

    if not isinstance(data, list):
        raise ValueError("materials_final.json must contain a list of material objects.")

    return tuple(item for item in data if isinstance(item, dict))


@lru_cache(maxsize=1)
def _search_index() -> tuple[dict[str, str], ...]:
    index: list[dict[str, str]] = []
    for item in load_materials():
        material_key = clean_value(item.get("material_key"), "")
        fallback_key = clean_value(item.get("cas"), "") or clean_value(item.get("name"), "")
        index.append(
            {
                "id": material_key or fallback_key,
                **{
                    label: _text_for_fields(item, fields)
                    for label, fields in SEARCH_FIELD_GROUPS.items()
                },
            }
        )
    return tuple(index)


def get_all_materials(limit: int | None = None) -> list[dict[str, Any]]:
    materials = list(load_materials())
    featured = sorted(
        materials,
        key=lambda item: (
            clean_value(item.get("fema")) == "N/A",
            clean_value(item.get("odor")) == "N/A" and clean_value(item.get("flavor")) == "N/A",
            clean_value(item.get("name")).lower(),
        ),
    )
    return featured[:limit] if limit else featured


def search_materials(
    query: str,
    fields: list[str] | tuple[str, ...] | None = None,
    limit: int | None = 60,
) -> list[dict[str, Any]]:
    query = clean_value(query, "").lower()
    if not query:
        return get_all_materials(limit)

    selected_fields = fields or ["All fields"]
    if "All fields" in selected_fields:
        selected_fields = ["All fields"]

    materials = load_materials()
    results: list[tuple[int, dict[str, Any]]] = []
    for position, indexed in enumerate(_search_index()):
        haystack = " ".join(indexed.get(field, "") for field in selected_fields)
        if query in haystack:
            score = _score_match(query, indexed, selected_fields)
            results.append((score, materials[position]))

    results.sort(key=lambda pair: (-pair[0], clean_value(pair[1].get("name")).lower()))
    items = [item for _, item in results]
    return items[:limit] if limit else items


def material_id(item: dict[str, Any]) -> str:
    return clean_value(item.get("material_key"), clean_value(item.get("cas"), clean_value(item.get("name"))))


@lru_cache(maxsize=1)
def _material_feature_index() -> tuple[dict[str, Any], ...]:
    index = []
    for item in load_materials():
        index.append(
            {
                "id": material_id(item),
                "descriptors": set(
                    term.lower()
                    for field in ("organoleptic_notes", "odor", "flavor")
                    for term in descriptor_terms(item.get(field))
                ),
                "occurrences": set(term.lower() for term in split_list_value(item.get("occurrence"))),
                "name": clean_value(item.get("name")).lower(),
                "mw": _float_value(item.get("molecular_weight")),
            }
        )
    return tuple(index)


def similar_materials(item: dict[str, Any], limit: int = 8) -> list[dict[str, Any]]:
    source_id = material_id(item)
    source_features = _features_for_material(item)
    if not source_features["descriptors"] and not source_features["occurrences"]:
        return []

    materials = load_materials()
    scored: list[tuple[float, dict[str, Any], list[str]]] = []
    for candidate, features in zip(materials, _material_feature_index()):
        if features["id"] == source_id:
            continue

        descriptor_overlap = source_features["descriptors"] & features["descriptors"]
        occurrence_overlap = source_features["occurrences"] & features["occurrences"]
        if not descriptor_overlap and not occurrence_overlap:
            continue

        score = len(descriptor_overlap) * 4 + len(occurrence_overlap) * 2
        if source_features["mw"] and features["mw"]:
            delta = abs(source_features["mw"] - features["mw"])
            if delta <= 10:
                score += 3
            elif delta <= 25:
                score += 1

        shared = sorted(descriptor_overlap)[:8] + sorted(occurrence_overlap)[:4]
        scored.append((score, candidate, shared))

    scored.sort(key=lambda pair: (-pair[0], clean_value(pair[1].get("name")).lower()))
    return [
        {
            "material": candidate,
            "score": f"{score:.0f}",
            "shared": ", ".join(shared) if shared else "N/A",
        }
        for score, candidate, shared in scored[:limit]
    ]


def _features_for_material(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "descriptors": set(
            term.lower()
            for field in ("organoleptic_notes", "odor", "flavor")
            for term in descriptor_terms(item.get(field))
        ),
        "occurrences": set(term.lower() for term in split_list_value(item.get("occurrence"))),
        "mw": _float_value(item.get("molecular_weight")),
    }


def _float_value(value: Any) -> float | None:
    text = clean_value(value, "")
    if not text:
        return None
    match = re.search(r"-?\d+(?:\.\d+)?", text)
    return float(match.group()) if match else None


@lru_cache(maxsize=1)
def analytics_summary() -> dict[str, Any]:
    materials = load_materials()
    total = len(materials)
    coverage_fields = {
        "CAS": ("cas",),
        "FEMA": ("fema",),
        "EINECS": ("einecs",),
        "JECFA": ("jecfa_food_flavoring", "jecfa_food_additive"),
        "Odor": ("odor",),
        "Flavor": ("flavor",),
        "Occurrence": ("occurrence",),
        "Formula": ("molecular_formula",),
        "Molecular Weight": ("molecular_weight",),
    }

    coverage = {
        label: _coverage_count(materials, fields)
        for label, fields in coverage_fields.items()
    }

    descriptor_counter: Counter[str] = Counter()
    occurrence_counter: Counter[str] = Counter()
    cas_counter: Counter[str] = Counter()
    name_counter: Counter[str] = Counter()
    weird_cas: list[dict[str, str]] = []

    for item in materials:
        descriptor_counter.update(
            term.lower()
            for field in ("organoleptic_notes", "odor", "flavor")
            for term in descriptor_terms(item.get(field))
        )
        occurrence_counter.update(term.lower() for term in split_list_value(item.get("occurrence")))

        cas = clean_value(item.get("cas"), "")
        if cas:
            cas_counter[cas] += 1
            if not re.match(r"^\d{2,7}-\d{2}-\d$", cas):
                weird_cas.append(_quality_row(item, cas))

        name = clean_value(item.get("name"), "").lower()
        if name:
            name_counter[name] += 1

    duplicate_cas = _duplicate_rows(cas_counter)
    duplicate_names = _duplicate_rows(name_counter)
    empty_core = [
        _quality_row(item, "Missing CAS/FEMA/EINECS/JECFA")
        for item in materials
        if not any(clean_value(item.get(field), "") for field in ("cas", "fema", "einecs", "jecfa_food_flavoring", "jecfa_food_additive"))
    ][:25]

    return {
        "total": total,
        "coverage": coverage,
        "top_descriptors": descriptor_counter.most_common(30),
        "top_occurrences": occurrence_counter.most_common(30),
        "duplicate_cas": duplicate_cas[:25],
        "duplicate_names": duplicate_names[:25],
        "weird_cas": weird_cas[:25],
        "empty_core_identifiers": empty_core,
    }


def _coverage_count(materials: tuple[dict[str, Any], ...], fields: tuple[str, ...]) -> int:
    return sum(1 for item in materials if any(clean_value(item.get(field), "") for field in fields))


def _duplicate_rows(counter: Counter[str]) -> list[dict[str, str]]:
    return [
        {"value": value, "count": str(count)}
        for value, count in counter.most_common()
        if count > 1
    ]


def _quality_row(item: dict[str, Any], issue: str) -> dict[str, str]:
    return {
        "name": clean_value(item.get("name")),
        "cas": clean_value(item.get("cas")),
        "fema": clean_value(item.get("fema")),
        "issue": issue,
    }


def descriptor_terms(value: Any) -> list[str]:
    text = clean_value(value, "")
    if not text:
        return []

    text = re.sub(r"\bat\s+\d+(?:\.\d+)?\s*%\s*\.?", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"\b(?:odor|flavor|taste)\s+(?:type|description)\s*:", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"\b(?:odor|flavor|taste)\b", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"\d+(?:\.\d+)?", " ", text)
    text = text.replace("|", ",")

    terms: list[str] = []
    seen: set[str] = set()
    for chunk in re.split(r"[,;./()\[\]\n]+", text):
        for word in chunk.split():
            word = clean_value(word.strip("-_: "), "")
            if not word or len(word) <= 1:
                continue
            normalized = word.lower()
            if normalized in DESCRIPTOR_STOP_WORDS:
                continue
            if normalized not in seen:
                seen.add(normalized)
                terms.append(word)
    return terms


def get_material(identifier: str) -> dict[str, Any] | None:
    identifier = clean_value(identifier, "").lower()
    if not identifier:
        return None

    for item in load_materials():
        candidates = (
            item.get("material_key"),
            item.get("cas"),
            item.get("name"),
        )
        if any(clean_value(candidate, "").lower() == identifier for candidate in candidates):
            return item
    return None


def summarize_material(item: dict[str, Any]) -> dict[str, str]:
    organoleptic = first_available(
        item,
        "organoleptic_notes",
        "odor",
        "flavor",
        "description",
        fallback="No organoleptic description available.",
    )
    return {
        "id": material_id(item),
        "name": clean_value(item.get("name")),
        "cas": clean_value(item.get("cas")),
        "fema": clean_value(item.get("fema")),
        "description": truncate(organoleptic, 180),
    }


def first_available(item: dict[str, Any], *keys: str, fallback: str = "N/A") -> str:
    for key in keys:
        value = clean_value(item.get(key), "")
        if value:
            return value
    return fallback


def detail_sections(item: dict[str, Any]) -> dict[str, dict[str, str]]:
    return {
        "Identifier": {
            "CAS": clean_value(item.get("cas")),
            "FEMA": clean_value(item.get("fema")),
            "EINECS": clean_value(item.get("einecs")),
            "Name Detail": first_available(item, "description", "name"),
            "Synonyms": format_synonyms(item.get("synonyms")),
            "JECFA Flavoring": clean_value(item.get("jecfa_food_flavoring")),
            "JECFA Additive": clean_value(item.get("jecfa_food_additive")),
            "DG SANTE Food Flavourings": clean_value(item.get("dg_sante_food_flavourings")),
            "DG SANTE Food Contact Materials": clean_value(item.get("dg_sante_food_contact_materials")),
            "Formula": clean_value(item.get("molecular_formula")),
        },
        "Properties": {
            "Molecular Weight": clean_value(item.get("molecular_weight")),
            "Boiling Point": clean_value(item.get("boiling_point")),
            "Melting Point": clean_value(item.get("melting_point")),
            "Solubility": clean_value(item.get("soluble_in")),
            "Flash Point": clean_value(item.get("flash_point")),
            "LogP": first_available(item, "logp", "xlogp3_aa"),
            "Appearance": clean_value(item.get("appearance")),
        },
        "Organoleptic": {
            "Taste": clean_value(item.get("flavor")),
            "Odor": clean_value(item.get("odor")),
            "Threshold": first_available(item, "threshold", "odor_threshold", "flavor_threshold"),
            "Characteristics": first_available(item, "organoleptic_notes", "description"),
            "Occurrence": clean_value(item.get("occurrence")),
        },
        "Insight": {
            "Usage": first_available(item, "ainsights_4_use_in_flavors", "ainsights_5_use_in_fragrances"),
            "Regulation": first_available(
                item,
                "ainsights_6_regulatory_status",
                "dg_sante_food_flavourings",
                "food_chemicals_codex_listed",
            ),
            "Safety": first_available(
                item,
                "ainsights_7_toxicology_safety_exposure_considerations",
                "flash_point",
            ),
            "Notes": first_available(item, "ainsights_9_confidence_data_quality_notes", "ainsights_text", "description"),
        },
    }


def truncate(text: str, length: int) -> str:
    text = clean_value(text)
    if len(text) <= length:
        return text
    return text[: length - 3].rstrip() + "..."


def _score_match(query: str, indexed: dict[str, str], selected_fields: list[str] | tuple[str, ...]) -> int:
    score = 0
    name = indexed.get("Name", "")
    if name == query:
        score += 100
    if name.startswith(query):
        score += 50
    for field in selected_fields:
        value = indexed.get(field, "")
        if query in value:
            score += 10 + value.count(query)
    return score
