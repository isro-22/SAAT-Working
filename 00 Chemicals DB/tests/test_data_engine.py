import gzip
import json
import tempfile
import unittest
from pathlib import Path

from src.flavor_db.data_engine import (
    analytics_summary,
    clean_value,
    descriptor_terms,
    detail_sections,
    format_organoleptic_text,
    format_synonyms,
    get_material,
    load_materials,
    material_id,
    read_json_records,
    search_materials,
    similar_materials,
    summarize_material,
)


class DataEngineTest(unittest.TestCase):
    def test_load_materials(self):
        materials = load_materials()
        self.assertGreater(len(materials), 1000)
        self.assertIn("name", materials[0])
        self.assertIn("material_key", materials[0])

    def test_hybrid_reader_loads_json_and_gzip(self):
        records = [{"name": "alpha"}, {"name": "beta"}, "ignored"]
        with tempfile.TemporaryDirectory() as tmpdir:
            json_path = Path(tmpdir) / "materials.json"
            gzip_path = Path(tmpdir) / "materials.json.gz"
            json_path.write_text(json.dumps(records), encoding="utf-8")
            with gzip.open(gzip_path, mode="wt", encoding="utf-8") as file:
                json.dump(records, file)

            self.assertEqual(read_json_records(json_path), records[:2])
            self.assertEqual(read_json_records(gzip_path), records[:2])

    def test_partial_cas_search(self):
        results = search_materials("111-70", ["CAS"], limit=10)
        self.assertTrue(any(item.get("cas") == "111-70-6" for item in results))

    def test_organoleptic_search(self):
        results = search_materials("caramellic", ["Organoleptic"], limit=10)
        self.assertGreater(len(results), 0)
        combined = " ".join(
            " ".join(str(item.get(field, "")) for field in ("organoleptic_notes", "odor", "flavor"))
            for item in results
        ).lower()
        self.assertIn("caramellic", combined)

    def test_synonym_or_name_search(self):
        results = search_materials("ethyl maltol", ["All fields"], limit=10)
        self.assertTrue(any(item.get("name") == "ethyl maltol" for item in results))

    def test_detail_mapping_has_four_sections(self):
        material = get_material("ethyl maltol")
        self.assertIsNotNone(material)
        sections = detail_sections(material)
        self.assertEqual(set(sections), {"Identifier", "Properties", "Organoleptic", "Insight"})
        for values in sections.values():
            self.assertTrue(all(isinstance(value, str) and value for value in values.values()))

    def test_summary_is_safe_for_missing_values(self):
        summary = summarize_material({})
        self.assertEqual(summary["name"], "N/A")
        self.assertEqual(summary["cas"], "N/A")
        self.assertEqual(summary["fema"], "N/A")

    def test_format_synonyms_splits_pipe_delimited_text(self):
        self.assertEqual(format_synonyms("alpha | beta | gamma"), "alpha\nbeta\ngamma")

    def test_descriptor_terms_cleanup(self):
        terms = descriptor_terms(
            "1. Odor Type: fruity sweet fresh juicy apple woody brown fusel | "
            "Odor Description:at 100.00 %. sweet fresh juicy apple woody brown fusel oil"
        )
        self.assertEqual(terms[:8], ["fruity", "sweet", "fresh", "juicy", "apple", "woody", "brown", "fusel"])

    def test_search_without_limit_returns_more_than_page_size(self):
        results = search_materials("sweet", ["Organoleptic"], limit=None)
        self.assertGreater(len(results), 60)

    def test_ainsights_disclosure_is_hidden(self):
        text = (
            "About FlavScents AInsights (Disclosure) FlavScents AInsights integrates information "
            "from authoritative government, scientific, academic, and industry sources to provide "
            "applied, exposure-aware insight into flavor and fragrance materials. Generated GMT (p)"
        )
        self.assertEqual(clean_value(text), "N/A")

    def test_ainsights_disclosure_without_footer_is_hidden(self):
        text = (
            "About FlavScents AInsights (Disclosure) FlavScents AInsights integrates information "
            "from authoritative government, scientific, academic, and industry sources to provide applied insight."
        )
        self.assertEqual(clean_value(text), "N/A")

    def test_organoleptic_pipe_text_becomes_lines(self):
        formatted = format_organoleptic_text(
            "1. Odor Type: herbal Odor Strength:high ,recommend smelling in a 10.00 % solution or less | "
            "Substantivity:8 hour(s) at 100.00 % | herbal green woody amber leafy | "
            "Odor Description:at 10.00 % in dipropylene glycol. herbal green woody amber leafy"
        )
        self.assertIn("Odor Type: herbal", formatted)
        self.assertIn("\nSubstantivity:8 hour(s) at 100.00 %", formatted)
        self.assertIn("\nOdor Description:at 10.00 % in dipropylene glycol.", formatted)

    def test_analytics_summary_has_core_sections(self):
        summary = analytics_summary()
        self.assertGreater(summary["total"], 1000)
        self.assertIn("CAS", summary["coverage"])
        self.assertGreater(len(summary["top_descriptors"]), 0)
        self.assertIn("duplicate_cas", summary)

    def test_material_id_prefers_material_key(self):
        material = get_material("ethyl maltol")
        self.assertTrue(material_id(material))
        self.assertEqual(material_id(material), material.get("material_key"))

    def test_similar_materials_returns_scored_rows(self):
        material = get_material("ethyl maltol")
        rows = similar_materials(material, limit=5)
        self.assertLessEqual(len(rows), 5)
        if rows:
            self.assertIn("material", rows[0])
            self.assertIn("score", rows[0])
            self.assertIn("shared", rows[0])


if __name__ == "__main__":
    unittest.main()
