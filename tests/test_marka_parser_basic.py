# === test_marka_parser_basic.py ===

from pathlib import Path
import unittest
from converter.marka_parser_basic import parse_marka_sales_basic


class TestParseMarkaSalesBasic(unittest.TestCase):

    def setUp(self):
        self.plik_sprzedazy = Path("../data/input/sprzedaz.csv")

    def test_basic_parse(self):
        wynik = parse_marka_sales_basic(self.plik_sprzedazy)

        # Podstawowe sprawdzenie
        self.assertGreater(len(wynik), 0, "Nie wczytano żadnych faktur!")

        # Sprawdzamy, że wczytano dokładnie 91 faktur
        self.assertEqual(len(wynik), 91, f"Powinno być 91 faktur, jest {len(wynik)}!")

        # Wydruk 10 pierwszych faktur
        print(f"\nWynik parsowania: {len(wynik)} faktur\n")
        for idx, faktura in enumerate(wynik[:10], start=1):
            self._drukuj_fakture(idx, faktura)

        # Wydruk faktur od 76 do 86
        for idx, faktura in enumerate(wynik[75:86], start=76):
            self._drukuj_fakture(idx, faktura)

    def test_all_invoices_have_stawki_vat(self):
        wynik = parse_marka_sales_basic(self.plik_sprzedazy)
        for faktura in wynik:
            self.assertIn('stawki_vat', faktura, "Brak pola 'stawki_vat' w fakturze")
            self.assertIsInstance(faktura['stawki_vat'], list, "'stawki_vat' powinno być listą")

    def test_sum_vat_matches_invoice_total(self):
        wynik = parse_marka_sales_basic(self.plik_sprzedazy)
        for faktura in wynik:
            suma_vat_stawki = sum(stawka['vat'] for stawka in faktura['stawki_vat'])
            wartosc_vat_ogolna = faktura.get('suma_podatkow_vat', 0.0)  # <-- poprawiona nazwa!

            # Pozwalamy na minimalne różnice zaokrągleń (do 1 grosza)
            self.assertAlmostEqual(
                suma_vat_stawki,
                wartosc_vat_ogolna,
                places=2,
                msg=f"Błąd w fakturze {faktura.get('numer_faktury')}: suma stawek VAT {suma_vat_stawki} ≠ {wartosc_vat_ogolna}"
            )


    @staticmethod
    def _drukuj_fakture(idx, faktura):
        print(f"{idx}. Numer faktury: {faktura['numer_faktury']}")
        print(f"   Kontrahent: {faktura['nazwa_kontrahenta']} (NIP: {faktura['nip']})")
        print(f"   Data wystawienia: {faktura['data_wystawienia']}, Data sprzedaży: {faktura['data_sprzedazy']}")
        print(f"   Wartość netto: {faktura['wartosc_netto']} PLN, Wartość brutto: {faktura['wartosc_brutto']} PLN, VAT: {faktura['vat']} PLN")
        if 'stawki_vat' in faktura and faktura['stawki_vat']:
            print("   Stawki VAT:")
            for stawka in faktura['stawki_vat']:
                print(f"     - {stawka['stawka']}%: Netto {stawka['netto']} PLN, VAT {stawka['vat']} PLN")
        print("")


if __name__ == "__main__":
    unittest.main()
