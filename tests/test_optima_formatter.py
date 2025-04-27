# === test_optima_formatter.py ===
# === test_optima_formatter.py ===
import unittest
import pandas as pd
from converter.optima_formatter import OptimaFormatter


class TestOptimaFormatter(unittest.TestCase):
    def setUp(self):
        # Przygotowanie przykładowych danych
        self.input_data_single_vat = pd.DataFrame({
            'nazwa_kontrahenta': ['ABC Sp. z o.o.'],
            'nip': ['1234567890'],
            'numer_faktury': ['Fakt/001/2024'],
            'data_sprzedazy': [pd.Timestamp('2024-04-15')],
            'data_wystawienia': [pd.Timestamp('2024-04-16')],
            'wartosc_netto': [1000.00],
            'wartosc_brutto': [1230.00],
            'netto3': [1000.00],   # netto 23%
            'kwvat3': [230.00],    # vat 23%
        })

        self.input_data_multi_vat = pd.DataFrame({
            'nazwa_kontrahenta': ['XYZ S.A.'],
            'nip': ['0987654321'],
            'numer_faktury': ['Fakt/002/2024'],
            'data_sprzedazy': [pd.Timestamp('2024-04-20')],
            'data_wystawienia': [pd.Timestamp('2024-04-21')],
            'wartosc_netto': [1300.00],
            'wartosc_brutto': [1600.00],
            'netto2': [500.00],   # netto 8%
            'kwvat2': [40.00],    # vat 8%
            'netto3': [800.00],   # netto 23%
            'kwvat3': [184.00],   # vat 23%
        })

    def test_format_full_single_vat(self):
        """Test faktury z jedną stawką VAT (23%)"""
        formatted_output = OptimaFormatter.format_full(self.input_data_single_vat)
        formatted_lines = formatted_output.strip().split('\n')

        self.assertEqual(len(formatted_lines), 1)

        line = formatted_lines[0]
        parts = line.split(',')

        self.assertEqual(parts[1], '"IMPORT"')
        self.assertEqual(parts[2], '"24/04/16"')  # data wystawienia
        self.assertEqual(parts[3], '"24/04/15"')  # data sprzedaży
        self.assertEqual(parts[5], '"Fakt/001/2024"')
        self.assertEqual(parts[18], '"1234567890"')
        self.assertEqual(parts[20], '64')  # GTU
        self.assertEqual(parts[47], '"SO"')
        self.assertEqual(parts[64], '0')     # flaga VAT
        self.assertEqual(parts[65], '23.00') # stawka VAT
        self.assertEqual(parts[66], '1000.00') # netto

    def test_format_full_multi_vat(self):
        """Test faktury z dwoma stawkami VAT (8% i 23%)"""
        formatted_output = OptimaFormatter.format_full(self.input_data_multi_vat)
        formatted_lines = formatted_output.strip().split('\n')

        self.assertEqual(len(formatted_lines), 1)

        line = formatted_lines[0]
        parts = line.split(',')

        self.assertEqual(parts[1], '"IMPORT"')
        self.assertEqual(parts[2], '"24/04/21"')  # data wystawienia
        self.assertEqual(parts[3], '"24/04/20"')  # data sprzedaży
        self.assertEqual(parts[5], '"Fakt/002/2024"')
        self.assertEqual(parts[18], '"0987654321"')
        self.assertEqual(parts[20], '64')  # GTU
        self.assertEqual(parts[47], '"SO"')

        # Pierwsza stawka VAT 8%
        self.assertEqual(parts[64], '0')      # flaga VAT
        self.assertEqual(parts[65], '8.00')   # stawka 8%
        self.assertEqual(parts[66], '500.00') # netto
        self.assertEqual(parts[67], '40.00')  # vat

        # Druga stawka VAT 23%
        self.assertEqual(parts[68], '0')      # flaga VAT
        self.assertEqual(parts[69], '23.00')  # stawka 23%
        self.assertEqual(parts[70], '800.00') # netto
        self.assertEqual(parts[71], '184.00') # vat


if __name__ == '__main__':
    unittest.main()
