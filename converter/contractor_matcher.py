# contractor_matcher.py
import pandas as pd
import logging
from typing import Dict, Optional

class ContractorMatcher:
    def __init__(self, contractors_filepath: str):
        """
        Inicjalizuje matcher kontrahentów.

        Args:
            contractors_filepath (str): Ścieżka do pliku CSV z kontrahentami.
        """
        self.contractors_df = pd.read_csv(contractors_filepath, delimiter=';', encoding='utf-8')
        self.contractors_df.columns = [col.strip().lower().replace(' ', '_') for col in self.contractors_df.columns]
        self.prepare_contractors()

    def prepare_contractors(self):
        """ Przygotowuje dane kontrahentów do szybkiego wyszukiwania."""
        self.contractors_df['nip'] = self.contractors_df['nip'].astype(str).str.replace('-', '').str.strip()
        self.contractors_df['nazwa_simplified'] = self.contractors_df['nazwa'].str.lower().str.replace(' ', '').str.strip()

    def find_contractor(self, nip: str, nazwa: str) -> Optional[Dict[str, str]]:
        """
        Szuka kontrahenta po NIP lub nazwie.

        Args:
            nip (str): Numer NIP kontrahenta.
            nazwa (str): Nazwa kontrahenta.

        Returns:
            dict lub None: Dane kontrahenta lub None jeśli nie znaleziono.
        """
        nip = (nip or '').replace('-', '').strip()
        nazwa_simplified = (nazwa or '').lower().replace(' ', '').strip()

        if nip:
            match = self.contractors_df[self.contractors_df['nip'] == nip]
            if not match.empty:
                return match.iloc[0].to_dict()

        if nazwa_simplified:
            match = self.contractors_df[self.contractors_df['nazwa_simplified'] == nazwa_simplified]
            if not match.empty:
                return match.iloc[0].to_dict()

        # Jeśli nie znaleziono, zapisujemy ostrzeżenie
        logging.warning(f"Nie znaleziono kontrahenta: NIP={nip}, Nazwa={nazwa}")
        return None

    def enrich_row_with_contractor(self, row: pd.Series) -> pd.Series:
        """
        Uzupełnia pojedynczy rekord danymi kontrahenta.

        Args:
            row (pd.Series): Pojedynczy wiersz danych sprzedaży.

        Returns:
            pd.Series: Uzupełniony wiersz.
        """
        contractor = self.find_contractor(row.get('nip', ''), row.get('nazwa_kontrahenta', ''))

        if contractor:
            row['kod_kontrahenta'] = contractor.get('kod', '')
            row['nazwa_pelna'] = contractor.get('nazwa', '')
            row['adres'] = contractor.get('adres', '')
        else:
            row['kod_kontrahenta'] = ''
            row['nazwa_pelna'] = ''
            row['adres'] = ''

        return row
