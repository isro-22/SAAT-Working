import unittest

from app.core.vba_compat import clean_text, get_base_bom, get_version_label, normalize_component_key, sort_version_keys


class VbaCompatTest(unittest.TestCase):
    def test_clean_text_handles_nbsp_and_line_breaks(self):
        self.assertEqual(clean_text(" A\u00a0B\n C\t"), "A B C")

    def test_version_helpers_match_export_bom_pattern(self):
        self.assertEqual(get_base_bom("GEN-FBL-00129-V3"), "GEN-FBL-00129")
        self.assertEqual(get_version_label("GEN-FBL-00129-V3"), "V3")
        self.assertEqual(get_version_label(""), "V1")
        self.assertEqual(sort_version_keys(["V10", "V2", "V1"]), ["V1", "V2", "V10"])

    def test_component_duplicate_key(self):
        self.assertTrue(normalize_component_key("Item", "ABC", 2).endswith("|DUP002"))


if __name__ == "__main__":
    unittest.main()
