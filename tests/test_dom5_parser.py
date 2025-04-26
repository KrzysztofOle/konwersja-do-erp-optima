# test_dom5_parser.py
import unittest
import pandas as pd
from converter.dom5_parser import Dom5Parser

class TestDom5Parser(unittest.TestCase):
    def setUp(self):
        # Przykładowe dane wejściowe
        self.input_data = pd.DataFrame({
            'Nazwa kontrahenta': ['ABC Sp. z o.o.'],
            'NIP': ['1234567890'],
            'Numer faktury': ['Fakt/001/2024'],
            'Data sprzedaży': ['15.04.2024'],
            'Data wystawienia': ['16.04.2024'],
            'Wartość netto': ['1000,00'],
            'VAT': ['230,00'],
            'Wartość brutto': ['1230,00']
        })

    def test_parse_successful(self):
        parsed_df = Dom5Parser.parse(self.input_data)

        # Sprawdzenie czy dane mają prawidłowe typy
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(parsed_df['data_sprzedazy']))
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(parsed_df['data_wystawienia']))
        self.assertTrue(pd.api.types.is_float_dtype(parsed_df['wartosc_netto']))
        self.assertTrue(pd.api.types.is_float_dtype(parsed_df['vat']))
        self.assertTrue(pd.api.types.is_float_dtype(parsed_df['wartosc_brutto']))

        # Sprawdzenie poprawności przekształcenia
        self.assertEqual(parsed_df.iloc[0]['nazwa_kontrahenta'], 'ABC Sp. z o.o.')
        self.assertEqual(parsed_df.iloc[0]['nip'], '1234567890')
        self.assertEqual(parsed_df.iloc[0]['numer_faktury'], 'Fakt/001/2024')
        self.assertEqual(parsed_df.iloc[0]['wartosc_netto'], 1000.00)
        self.assertEqual(parsed_df.iloc[0]['vat'], 230.00)
        self.assertEqual(parsed_df.iloc[0]['wartosc_brutto'], 1230.00)

    def test_missing_columns(self):
        # Dane bez kolumny NIP
        invalid_data = self.input_data.drop(columns=['NIP'])
        with self.assertRaises(ValueError):
            Dom5Parser.parse(invalid_data)

if __name__ == '__main__':
    unittest.main()
