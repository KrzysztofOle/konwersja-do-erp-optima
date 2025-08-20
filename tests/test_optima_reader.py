# tests/test_optima_reader.py
import unittest
from io import StringIO
import csv
import sys
from pathlib import Path

# Umożliwiamy import pakietu projektu (żeby "working" był widoczny jako moduł)
sys.path.append(str(Path('.').resolve()))

from working.optima_reader import (
    read_optima_export,
    read_optima_export_from_string,
    sum_columns,
    OPTIMA_COLUMNS,
)

MIN_REQUIRED_COLS = 1 + len(OPTIMA_COLUMNS)  # lp + 59 rdzeniowych


class TestOptimaReader(unittest.TestCase):

    def _make_csv_with_rows(self, rows):
        """
        Tworzy bufor CSV (StringIO) z podanymi wierszami.
        Każdy wiersz MUSI mieć co najmniej MIN_REQUIRED_COLS pól (lp + 59).
        W razie potrzeby wiersz jest dopełniany pustymi polami.
        """
        sio = StringIO()
        writer = csv.writer(
            sio,
            delimiter=',',
            quotechar='"',
            quoting=csv.QUOTE_MINIMAL,
            lineterminator='\n',
        )
        for r in rows:
            if len(r) < MIN_REQUIRED_COLS:
                r = r + [""] * (MIN_REQUIRED_COLS - len(r))
            writer.writerow(r[:MIN_REQUIRED_COLS])
        sio.seek(0)
        return sio

    def test_read_assigns_column_names(self):
        # 1 pusty wiersz o długości = lp + rdzeniowe
        # kolumna 0: lp
        row = ["0"] + ([""] * len(OPTIMA_COLUMNS))
        buf = self._make_csv_with_rows([row])

        df = read_optima_export(buf)

        # Oczekiwane nazwy: ['lp'] + OPTIMA_COLUMNS (+ brak ogona)
        expected_names = ['lp'] + OPTIMA_COLUMNS
        self.assertEqual(list(df.columns), expected_names)
        self.assertEqual(df.shape, (1, len(expected_names)))

    def test_sum_columns_numeric_and_strings(self):
        # Indeksy w obrębie rdzeniowych (bez lp)
        idx_brutto = OPTIMA_COLUMNS.index('brutto')
        idx_netto3 = OPTIMA_COLUMNS.index('netto3')
        idx_kwvat3 = OPTIMA_COLUMNS.index('kwvat3')

        # Tworzymy dwa wiersze (dodajemy lp na pozycji 0, dane rdzeniowe wchodzą od indeksu 1)
        row1 = ["1"] + ([""] * len(OPTIMA_COLUMNS))
        row2 = ["2"] + ([""] * len(OPTIMA_COLUMNS))

        # Ustawiamy wartości we właściwych kolumnach: przesunięcie +1 względem OPTIMA_COLUMNS
        row1[1 + idx_brutto] = "100.50"
        row1[1 + idx_netto3] = "80,40"
        row1[1 + idx_kwvat3] = "18.50"

        row2[1 + idx_brutto] = "20,5"      # 20.5
        row2[1 + idx_netto3] = "19.60"
        row2[1 + idx_kwvat3] = ""          # puste -> 0

        buf = self._make_csv_with_rows([row1, row2])
        df = read_optima_export(buf)

        totals = sum_columns(df, ["brutto", "netto3", "kwvat3", "nieistniejaca"])
        self.assertAlmostEqual(totals["brutto"], 121.0, places=6)     # 100.50 + 20.5
        self.assertAlmostEqual(totals["netto3"], 100.0, places=6)     # 80.40 + 19.60
        self.assertAlmostEqual(totals["kwvat3"], 18.5, places=6)      # 18.50 + 0
        self.assertAlmostEqual(totals["nieistniejaca"], 0.0, places=6)

    def test_read_from_string_helper(self):
        # Jeden wiersz minimalny z trzema wartościami kontrolnymi
        values = ["0"] + ([""] * len(OPTIMA_COLUMNS))  # lp + rdzeniowe
        values[1 + OPTIMA_COLUMNS.index("IK")] = "SPRZEDAŻ"
        values[1 + OPTIMA_COLUMNS.index("dokument")] = "F/1/04/2025"
        values[1 + OPTIMA_COLUMNS.index("brutto")] = "2216,44"

        sio = StringIO()
        writer = csv.writer(sio, delimiter=',', quotechar='"', lineterminator='\n')
        writer.writerow(values)
        csv_text = sio.getvalue()

        df = read_optima_export_from_string(csv_text)
        self.assertEqual(df.loc[0, "IK"], "SPRZEDAŻ")
        self.assertEqual(df.loc[0, "dokument"], "F/1/04/2025")
        self.assertEqual(df.loc[0, "brutto"], "2216,44")


if __name__ == '__main__':
    unittest.main()
