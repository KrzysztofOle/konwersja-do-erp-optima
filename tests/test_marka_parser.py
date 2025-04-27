# === test_marka_parser.py ===
import unittest
from pathlib import Path
from converter.contractor_matcher import ContractorMatcher
from converter.marka_parser import parse_marka_sales


class TestMarkaParser(unittest.TestCase):

    def setUp(self):
        self.plik_sprzedazy = Path("../data/input/sprzedaz.csv")
        self.plik_kontrahenci = Path("../data/input/listaFirm.csv")
        self.matcher = ContractorMatcher(self.plik_kontrahenci)

    def test_liczba_faktur(self):
        wynik = parse_marka_sales(self.plik_sprzedazy, self.matcher)

        # Sprawdzamy, że wczytano dokładnie 91 faktur
        self.assertEqual(len(wynik), 91, f"Powinno być 91 faktur, jest {len(wynik)}!")

        # Sprawdzamy numery pierwszych 87 faktur
        for idx in range(87):
            expected_number = f"S/F-2025-02/{idx+1}"
            self.assertEqual(
                wynik[idx]['numer_faktury'], expected_number,
                f"Błędny numer faktury na pozycji {idx}: {wynik[idx]['numer_faktury']} != {expected_number}"
            )

    def test_parse_with_zero_vat(self):
        wynik = parse_marka_sales(self.plik_sprzedazy, self.matcher)
        faktura = wynik[75]  # Faktura S/F-2025-02/76 (index 75)

        self.assertEqual(faktura['numer_faktury'], 'S/F-2025-02/76')
        self.assertAlmostEqual(faktura['vat'], 0.0, places=2)

    def test_parse_with_single_vat_23(self):
        wynik = parse_marka_sales(self.plik_sprzedazy, self.matcher)
        faktura = wynik[76]  # Faktura S/F-2025-02/77 (index 76)

        self.assertEqual(faktura['numer_faktury'], 'S/F-2025-02/77')
        self.assertEqual(len(faktura['stawki_vat']), 1)
        self.assertAlmostEqual(faktura['stawki_vat'][0]['stawka'], 23.0, places=2)

    def test_parse_with_multiple_vat(self):
        wynik = parse_marka_sales(self.plik_sprzedazy, self.matcher)
        faktura = wynik[79]  # Faktura S/F-2025-02/80 (index 79)

        self.assertEqual(faktura['numer_faktury'], 'S/F-2025-02/80')
        self.assertEqual(len(faktura['stawki_vat']), 2)

        stawki = sorted(faktura['stawki_vat'], key=lambda x: x['stawka'])
        self.assertAlmostEqual(stawki[0]['stawka'], 8.0, places=2)
        self.assertAlmostEqual(stawki[1]['stawka'], 23.0, places=2)

    def test_parse_first_invoice(self):
        wynik = parse_marka_sales(self.plik_sprzedazy, self.matcher)
        faktura = wynik[0]

        self.assertEqual(faktura['numer_faktury'], 'S/F-2025-02/1')
        self.assertIsNotNone(faktura['data_wystawienia'])
        self.assertIsNotNone(faktura['data_sprzedazy'])


if __name__ == "__main__":
    unittest.main()
