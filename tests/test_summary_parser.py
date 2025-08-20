# -*- coding: utf-8 -*-
import unittest
from pathlib import Path
import tempfile
from working.summary_parser import parse_summary_from_dom5_csv

SAMPLE = r"""
"Zestawienie dokumentów sprzedaży wg daty księgowej",,,,,,,,,,,
"Jakieś nagłówki",,,,,,,,,,,
"Razem rejestry w rozbiciu: ",,,,,,,,,,,
"Administrowanie",,,,"319532,99","","288920,09","30612,90","-","30612,90",""
"",,,,"155153,34","zw.","155153,34","0,00","-","0,00",""
"",,,,"1106,94","8%","1024,95","81,99","-","81,99",""
"",,,,"163272,71","23%","132741,80","30530,91","-","30530,91",""
"Ogółem:",,,,"319532,99","","288920,09","30612,90","-","30612,90",""
"",,,,"155153,34","zw.","155153,34","0,00","-","0,00",""
"",,,,"1106,94","8%","1024,95","81,99","-","81,99",""
"",,,,"163272,71","23%","132741,80","30530,91","-","30530,91",""
"""

class TestSummaryParserDict(unittest.TestCase):
    def test_parse_to_dict(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            p = Path(tmpdir) / "sum.csv"
            p.write_text(SAMPLE, encoding="utf-8")
            data = parse_summary_from_dom5_csv(p)

            self.assertIn("categories", data)
            self.assertIn("overall", data)
            self.assertEqual(len(data["categories"]), 1)

            cat = data["categories"][0]
            self.assertEqual(cat["name"], "Administrowanie")
            self.assertAlmostEqual(cat["totals"]["gross"], 319532.99, places=2)
            self.assertAlmostEqual(cat["totals"]["net"],   288920.09, places=2)
            self.assertAlmostEqual(cat["totals"]["vat"],    30612.90, places=2)
            self.assertEqual(len(cat["rates"]), 3)

            rates = {r["rate"]: r for r in cat["rates"]}
            self.assertAlmostEqual(rates["zw."]["gross"], 155153.34, places=2)
            self.assertAlmostEqual(rates["8%"]["net"],    1024.95,   places=2)
            self.assertAlmostEqual(rates["23%"]["vat"],   30530.91,  places=2)

            overall = data["overall"]
            self.assertEqual(overall["label"], "Ogółem:")
            self.assertAlmostEqual(overall["totals"]["gross"], 319532.99, places=2)
            self.assertAlmostEqual(overall["totals"]["net"],   288920.09, places=2)
            self.assertAlmostEqual(overall["totals"]["vat"],    30612.90, places=2)
            self.assertEqual(len(overall["rates"]), 3)

if __name__ == "__main__":
    unittest.main()
