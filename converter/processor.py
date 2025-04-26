from converter.dom5_parser import Dom5Parser
from converter.optima_formatter import OptimaFormatter
from converter.contractor_matcher import ContractorMatcher


def analiza_zestawienia_faktur(sciezka_csv, sciezka_lista_firm, wynikowy_plik):
    # Tu powinna być faktyczna logika łącząca parser + formatter + matcher
    parser = Dom5Parser()
    formatter = OptimaFormatter()
    matcher = ContractorMatcher(sciezka_lista_firm)

    # Wczytaj dane CSV
    dane = parser.wczytaj_raport(sciezka_csv)

    # Dopasuj kontrahentów
    dane_po_dopasowaniu = matcher.dopasuj(dane)

    # Sformatuj dane
    dane_sformatowane = formatter.formatuj(dane_po_dopasowaniu)

    # Zapisz do pliku wynikowego
    with open(wynikowy_plik, 'w', encoding='utf-8') as f:
        f.write(dane_sformatowane)

    return wynikowy_plik
