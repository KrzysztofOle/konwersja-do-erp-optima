# === processor.py ===
import pandas as pd
from converter.dom5_parser import Dom5Parser
from converter.optima_formatter import OptimaFormatter
from converter.contractor_matcher import ContractorMatcher


def analiza_zestawienia_faktur(sciezka_csv, sciezka_lista_firm, wynikowy_plik):
    # 1. Wczytaj CSV do DataFrame
    df = pd.read_csv(sciezka_csv)

    try:
        # 2. Przetwórz DataFrame przez Dom5Parser
        df_przetworzony = Dom5Parser.parse(df)
    except ValueError as e:
        raise ValueError(f"Błąd w pliku {sciezka_csv} - {str(e)}") from e

    # 3. Dopasuj kontrahentów
    matcher = ContractorMatcher(sciezka_lista_firm)
    df_po_dopasowaniu = matcher.dopasuj(df_przetworzony)

    # 4. Sformatuj dane do pliku tekstowego
    formatter = OptimaFormatter()
    dane_sformatowane = formatter.formatuj(df_po_dopasowaniu)

    # 5. Zapisz wynik do pliku
    with open(wynikowy_plik, 'w', encoding='utf-8') as f:
        f.write(dane_sformatowane)

    return wynikowy_plik
