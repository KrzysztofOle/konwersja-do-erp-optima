# === contractor_matcher.py ===
from typing import Optional
import pandas as pd
from dataclasses import dataclass

@dataclass
class Contractor:
    name: str
    nip: str

class ContractorMatcher:
    def __init__(self, contractors_filepath: str):
        self.contractors_df = pd.read_csv(contractors_filepath, delimiter=';', encoding='utf-8')

        # Dynamiczne wykrywanie kolumny z nazwą firmy
        possible_name_columns = ['Nazwa', 'Nazwa firmy', 'Kontrahent', 'Firma']
        self.name_column = None
        for col in self.contractors_df.columns:
            if col.strip() in possible_name_columns:
                self.name_column = col.strip()
                break

        if self.name_column is None:
            raise ValueError("Brak kolumny z nazwą kontrahenta w pliku listaFirm.csv!")

    def match_by_nip(self, nip: str) -> Optional[Contractor]:
        result = self.contractors_df[self.contractors_df['NIP'] == nip]
        if not result.empty:
            contractor_data = result.iloc[0]
            return Contractor(name=contractor_data[self.name_column], nip=contractor_data['NIP'])
        return None

    def match_by_name_fragment(self, name_fragment: str) -> Optional[Contractor]:
        """
        Szuka kontrahenta po fragmencie nazwy.

        :param name_fragment: Fragment nazwy kontrahenta.
        :return: Obiekt Contractor lub None.
        """
        matches = self.contractors_df[self.contractors_df[self.name_column].str.contains(name_fragment, case=False, na=False)]
        if not matches.empty:
            first_match = matches.iloc[0]
            return Contractor(name=first_match[self.name_column], nip=first_match['NIP'])
        return None
