# optima_formatter.py
import pandas as pd

class OptimaFormatter:
    @staticmethod
    def format(df: pd.DataFrame) -> str:
        """
        Formatuje dane do postaci zgodnej z systemem ERP Optima.

        Args:
            df (pd.DataFrame): Przetworzone dane wejściowe po parsowaniu i wzbogaceniu kontrahentami.

        Returns:
            str: Dane w formacie tekstowym, gotowe do zapisu w pliku TXT.
        """
        formatted_lines = []

        for _, row in df.iterrows():
            line = '|'.join([
                row.get('kod_kontrahenta', ''),
                row.get('nazwa_pelna', ''),
                row.get('adres', ''),
                row.get('nip', ''),
                row.get('numer_faktury', ''),
                row.get('data_sprzedazy').strftime('%Y-%m-%d') if pd.notna(row.get('data_sprzedazy')) else '',
                row.get('data_wystawienia').strftime('%Y-%m-%d') if pd.notna(row.get('data_wystawienia')) else '',
                f"{row.get('wartosc_netto', 0.0):.2f}".replace('.', ','),
                f"{row.get('vat', 0.0):.2f}".replace('.', ','),
                f"{row.get('wartosc_brutto', 0.0):.2f}".replace('.', ',')
            ])
            formatted_lines.append(line)

        formatted_txt = '\n'.join(formatted_lines)
        return formatted_txt
