# === optima_reader.py ===
"""
Moduł do wczytywania plików eksportu ERP Optima (TXT/CSV)
i przypisywania im odpowiednich nazw kolumn oraz sumowania wybranych kolumn.

Założenia:
- Plik wynikowy tworzony dla Optima zaczyna się kolumną 'lp', po której
  następuje 59 kolumn rdzeniowych (OPTIMA_COLUMNS), a następnie opcjonalny
  „ogon” sekcji VAT (powtarzające się czwórki: flaga, stawka, netto, vat).
- Funkcja read_optima_export przyjmuje ścieżkę (Path/str) **albo** bufor pliku
  tekstowego (np. io.StringIO).
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, IO, Union, Dict, List

import pandas as pd

# 59 rdzeniowych kolumn (bez 'lp' na początku!)
OPTIMA_COLUMNS: List[str] = [
    'GRUPA', 'data_tr', 'data_wyst', 'IK', 'dokument', 'KOREKTA_DO', 'TYP',
    'KOREKTA', 'ZAKUP', 'ODLICZENIA', 'KASA', 'kontrahent', 'k_nazwa1',
    'k_nazwa2', 'ulica', 'kod', 'miasto', 'nip', 'KONTO', 'FIN', 'EXPORT',
    'ID_O', 'KOD_O', 'OPIS', 'netto0', 'netto1', 'netto2', 'netto3',
    'netto4', 'kwvat2', 'kwvat3', 'kwvat4', 'st5', 'uslugi', 'produkcja',
    'ROZLICZONO', 'PLATNOSC', 'termin', 'brutto', 'zaplata', 'ID_FPP',
    'NR_FPP', 'wartosc_z', 'clo', 'akcyza', 'pod_imp', 'USER', 'kaucja',
    'netto6', 'netto7', 'vat6', 'vat7', 'x1', 'x2', 'x3', 'x4', 'x5',
    'wartosc_s', 'vat_s'
]


def _tail_names(n: int) -> List[str]:
    """
    Generuje nazwy dla kolumn „ogona” po 59 kolumnach rdzeniowych:
    flaga_1, stawka_1, netto_1, vat_1, flaga_2, stawka_2, netto_2, vat_2, ...

    Jeśli kolumn jest więcej i nie mieszczą się w pełnych czwórkach,
    nadmiarowe nazywamy 'extra_{i}'.
    """
    pattern = ['flaga', 'stawka', 'netto', 'vat']
    names: List[str] = []
    i = 1
    # pełne paczki po 4
    while len(names) + 4 <= n:
        names.extend([f'{p}_{i}' for p in pattern])
        i += 1
    # ewentualne resztki
    while len(names) < n:
        names.append(f'extra_{len(names) + 1}')
    return names


def read_optima_export(path_or_buffer: Union[str, Path, IO[str]], dtypes: Dict[str, str] | None = None) -> pd.DataFrame:
    """
    Wczytuje plik/bufor TXT/CSV (bez nagłówka) i przypisuje nazwy kolumn:
    - kolumna 0: 'lp'
    - kolumny 1..59: OPTIMA_COLUMNS
    - kolumny 60..: ogon VAT (flaga_*, stawka_*, netto_*, vat_*)

    :param path_or_buffer: ścieżka do pliku lub bufor plikowy (np. io.StringIO)
    :param dtypes: (opcjonalnie) wymuszenie typów dla wybranych kolumn
    :return: DataFrame z nazwanymi kolumnami
    :raises ValueError: jeśli liczba kolumn < 60 (lp + 59 rdzeniowych)
    """
    df = pd.read_csv(
        path_or_buffer,
        header=None,
        sep=',',
        quotechar='"',
        encoding='utf-8-sig',
        dtype=dtypes if dtypes is not None else None,
        engine='python'
    )

    min_required = 1 + len(OPTIMA_COLUMNS)  # lp + 59
    if df.shape[1] < min_required:
        raise ValueError(
            f"Zbyt mało kolumn w danych (znaleziono {df.shape[1]}). "
            f"Oczekiwano co najmniej {min_required} (lp + 59 kolumn rdzeniowych)."
        )

    total_cols = df.shape[1]
    names = ['lp'] + OPTIMA_COLUMNS
    if total_cols > min_required:
        tail_count = total_cols - min_required
        names += _tail_names(tail_count)

    df.columns = names
    return df


def sum_columns(df: pd.DataFrame, columns: Iterable[str]) -> Dict[str, float]:
    """
    Sumuje wybrane kolumny i zwraca wynik jako {kolumna: suma(float)}.
    - Ignoruje wartości puste/NaN.
    - Akceptuje liczby jako stringi z przecinkiem dziesiętnym (zamienia na kropkę).
    - Jeśli kolumna nie istnieje, zwraca 0.0 dla tej kolumny.
    """
    result: Dict[str, float] = {}
    for col in columns:
        if col not in df.columns:
            result[col] = 0.0
            continue
        series = (
            df[col]
            .astype(str)
            .str.replace(",", ".", regex=False)
            .replace({"": "0"})
        )
        result[col] = pd.to_numeric(series, errors="coerce").fillna(0.0).sum()
    return result


def read_optima_export_from_string(csv_text: str) -> pd.DataFrame:
    """
    Wygodna funkcja pomocnicza: wczytuje dane z surowego tekstu CSV.
    Przydatna w testach i szybkich próbkach.
    """
    from io import StringIO
    return read_optima_export(StringIO(csv_text))


if __name__ == "__main__":
    # Uruchomienie modułu jako skrypt:
    # - czyta ścieżkę pliku wynikowego z config.ini
    # - wczytuje dane, drukuje podgląd
    # - liczy sumy wskazanych kolumn i sprawdza zgodność brutto vs (netto + VAT)

    import configparser
    from pathlib import Path

    config = configparser.ConfigParser()
    config.read('config.ini')

    plik = Path(config['sciezki']['sciezka_pliku_wynikowego'])

    df = read_optima_export(plik)
    print(f'Wczytano {len(df)} wierszy z pliku: {plik}')
    print(df.columns.tolist())
    print('-' * 40 + '\n\n\nPrzykładowe dane:\n')
    print(df.head(10))

    # przykład sumowania
    kolumny_do_sumy = ["brutto", "netto_1", "netto_2", "netto_3", "vat_1", "vat_2", "vat_3"]
    suma = sum_columns(df, kolumny_do_sumy)

    print("\n\nSumy wybranych kolumn:")
    for k, v in suma.items():
        print(f"{k}: {v:.2f}")

    # sprawdzenie sumy netto i vat
    brutto_sum = suma.get("brutto", 0.0)
    netto_sum = suma.get("netto_1", 0.0) + suma.get("netto_2", 0.0) + suma.get("netto_3", 0.0)
    vat_sum = suma.get("vat_1", 0.0) + suma.get("vat_2", 0.0) + suma.get("vat_3", 0.0)

    print('-' * 40)
    if abs(brutto_sum - (netto_sum + vat_sum)) > 0.01:
        print(f"Uwaga: Suma brutto ({brutto_sum:.2f}) nie zgadza się z sumą netto ({netto_sum:.2f}) i VAT ({vat_sum:.2f}).")
    else:
        print(f"Suma brutto ({brutto_sum:.2f}) zgadza się z sumą netto ({netto_sum:.2f}) i VAT ({vat_sum:.2f}).")
    print('-' * 40)
    print("Koniec programu.")
    