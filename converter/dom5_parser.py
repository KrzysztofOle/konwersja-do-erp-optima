# dom5_parser.py
import pandas as pd


class Dom5Parser:

    @staticmethod
    def parse(df: pd.DataFrame) -> pd.DataFrame:
        """
        Analizuje i przetwarza dane z raportu CSV generowanego przez system Dom 5 (moduł „Sprzedaż Zarządcy dla Wspólnot”).

        Args:
            df (pd.DataFrame): Ramka danych wejściowych z systemu Dom 5.

        Returns:
            pd.DataFrame: Przetworzone dane gotowe do formatowania pod ERP Optima.
        """
        # Upewnij się, że nazwy kolumn są poprawnie ustandaryzowane
        df.columns = [col.strip().lower().replace(' ', '_') for col in df.columns]

        # Przykładowe wymagane kolumny z Dom 5
        required_columns = ['nazwa_kontrahenta', 'nip', 'numer_faktury', 'data_sprzedazy',
                            'data_wystawienia', 'wartosc_netto', 'vat', 'wartosc_brutto']

        # Sprawdzenie czy wszystkie wymagane kolumny są dostępne
        missing_cols = set(required_columns) - set(df.columns)
        if missing_cols:
            raise ValueError(f'Brakuje wymaganych kolumn w pliku wejściowym: {missing_cols}')

        # Konwersja typów danych na odpowiednie formaty
        df['data_sprzedazy'] = pd.to_datetime(df['data_sprzedazy'], dayfirst=True)
        df['data_wystawienia'] = pd.to_datetime(df['data_wystawienia'], dayfirst=True)
        df['wartosc_netto'] = df['wartosc_netto'].replace(',', '.', regex=True).astype(float)
        df['vat'] = df['vat'].replace(',', '.', regex=True).astype(float)
        df['wartosc_brutto'] = df['wartosc_brutto'].replace(',', '.', regex=True).astype(float)

        # Usuwanie duplikatów, jeśli istnieją
        df.drop_duplicates(subset=['numer_faktury'], inplace=True)

        # Sortowanie po dacie sprzedaży
        df.sort_values(by='data_sprzedazy', inplace=True)

        # Resetowanie indeksu
        df.reset_index(drop=True, inplace=True)

        return df
