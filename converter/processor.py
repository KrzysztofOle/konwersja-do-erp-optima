# === processor.py ===
from pathlib import Path
import pandas as pd
from converter.marka_parser import parse_marka_sales
from converter.contractor_matcher import ContractorMatcher
from converter.optima_formatter import OptimaFormatter


class Processor:
    def __init__(self, config):
        self.config = config

    def przetworz_dane(self):
        plik_sprzedazy = Path(self.config['sciezki']['sciezka_pliku_csv'])
        plik_kontrahenci = Path(self.config['sciezki']['sciezka_lista_firm'])
        plik_wynikowy = Path(self.config['sciezki']['sciezka_pliku_wynikowego'])

        matcher = ContractorMatcher(plik_kontrahenci)
        dane_sprzedazy = parse_marka_sales(plik_sprzedazy, matcher)

        dane_df = pd.DataFrame(dane_sprzedazy)

        wymagane_kolumny = [
            'kod_kontrahenta', 'nazwa_pelna', 'adres', 'nip',
            'numer_faktury', 'data_sprzedazy', 'data_wystawienia',
            'wartosc_netto', 'vat', 'wartosc_brutto'
        ]

        for kolumna in wymagane_kolumny:
            if kolumna not in dane_df.columns:
                dane_df[kolumna] = ''

        dane_df = dane_df.fillna('')

        # NOWE: Zamiana kolumn dat na datetime
        for kolumna in ['data_sprzedazy', 'data_wystawienia']:
            if kolumna in dane_df.columns:
                dane_df[kolumna] = pd.to_datetime(dane_df[kolumna], errors='coerce')

        tekst_do_zapisu = OptimaFormatter.format_full(dane_df)

        with plik_wynikowy.open('w', encoding='utf-8') as f:
            f.write(tekst_do_zapisu)
