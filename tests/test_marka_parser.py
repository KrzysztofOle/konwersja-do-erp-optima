# === tests/test_marka_parser.py ===
from pathlib import Path
from converter.contractor_matcher import ContractorMatcher
from converter.marka_parser import parse_marka_sales


def test_parse_marka_sales():
    # Poprawione ścieżki do plików
    plik_sprzedazy = Path("../data/input/sprzedaz.csv")
    plik_kontrahenci = Path("../data/input/listaFirm.csv")  # <<< poprawiona nazwa

    matcher = ContractorMatcher(plik_kontrahenci)
    wynik = parse_marka_sales(plik_sprzedazy, matcher)

    assert wynik, "Parser nie zwrócił żadnych danych!"

    # Wyświetlenie kilku pierwszych wyników dla porównania
    for idx, row in enumerate(wynik[:10]):
        print(f"{idx + 1}. {row}")


if __name__ == "__main__":
    test_parse_marka_sales()
