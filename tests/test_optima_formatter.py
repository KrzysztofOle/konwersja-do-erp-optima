# test_optima_formatter.py
import unittest
import pandas as pd
from converter.optima_formatter import OptimaFormatter

class TestOptimaFormatter(unittest.TestCase):
    def setUp(self):
        # Przygotowanie przykładowych danych
        self.input_data = pd.DataFrame({
            'nazwa_kontrahenta': ['ABC Sp. z o.o.'],
            'nip': ['1234567890'],
            'numer_faktury': ['Fakt/001/2024'],
            'data_sprzedazy': [pd.Timestamp('2024-04-15')],
            'data_wystawienia': [pd.Timestamp('2024-04-16')],
            'wartosc_netto': [1000.00],
            'vat': [230.00],
            'wartosc_brutto': [1230.00]
        })

    def test_format_output(self):
        formatted_output = OptimaFormatter.format(self.input_data)

        expected_output = (
            'ABC Sp. z o.o.|1234567890|Fakt/001/2024|2024-04-15|2024-04-16|1000,00|230,00|1230,00'
        )

        self.assertEqual(formatted_output.strip(), expected_output)

if __name__ == '__main__':
    unittest.main()
