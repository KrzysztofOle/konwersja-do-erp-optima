# === test_marka_parser.py ===
from pathlib import Path
from converter.contractor_matcher import ContractorMatcher
from converter.marka_parser import parse_marka_sales


def test_parse_marka_sales():
    plik_sprzedazy = Path("../data/input/sprzedaz.csv")
    plik_kontrahenci = Path("../data/input/listaFirm.csv")

    matcher = ContractorMatcher(plik_kontrahenci)
    wynik = parse_marka_sales(plik_sprzedazy, matcher)

    assert wynik, "Parser nie zwrócił żadnych danych!"

    print(f"\nWynik parsowania: {len(wynik)} faktur\n")
    for idx, row in enumerate(wynik[75:86], start=76):
        print(f"{idx + 1}. Numer faktury: {row['numer_faktury']}")
        print(f"   Kontrahent: {row['nazwa_kontrahenta']} (NIP: {row['nip']})")
        print(f"   Data wystawienia: {row['data_wystawienia']}, Data sprzedaży: {row['data_sprzedazy']}")
        print(f"   Wartość netto: {row['wartosc_netto']} PLN, Wartość brutto: {row['wartosc_brutto']} PLN, VAT: {row['vat']} PLN")
        if 'stawki_vat' in row and row['stawki_vat']:
            print("   Stawki VAT:")
            for stawka in row['stawki_vat']:
                print(f"     - {stawka['stawka']}%: Netto {stawka['netto']} PLN, VAT {stawka['vat']} PLN")
        print("")


if __name__ == "__main__":
    test_parse_marka_sales()
