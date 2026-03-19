# UWAGA_RUN

## Konfiguracja uruchomienia

Konfiguracja debugowania `Debug: analiza_zestawienia_faktur` jest zdefiniowana w pliku `.vscode/launch.json`.

Uruchamia ona bezpośrednio skrypt:

- `converter/przetwarzaj_zestawienia.py`

z argumentem:

- `--test`

Uwaga: w pliku `converter/przetwarzaj_zestawienia.py` nie ma obecnie obsługi `sys.argv` ani `argparse`, więc argument `--test` nie wpływa na działanie skryptu.

## Gdzie definiują się pliki danych

Ścieżki do plików danych nie są wpisane bezpośrednio w `.vscode/launch.json`.

Skrypt `converter/przetwarzaj_zestawienia.py` w bloku `if __name__ == "__main__":` odczytuje plik:

- `config.ini`

i pobiera wartości z sekcji:

- `[sciezki]`

## Jakie pliki są używane

Skrypt przetwarza dwa zestawy danych.

### Zestaw 1

- plik sprzedaży CSV: `data/input/2025.09 - sprzedaż MARKA JDG z kontrahentami.csv`
- plik kontrahentów CSV: `data/input/Kontrahenci_Marka_jdg_converted.csv`
- plik wynikowy TXT: `data/output/2025-09_sprzedaz_MARKA_JDG_OPTIMA.txt`

### Zestaw 2

- plik sprzedaży CSV: `data/input/2025.09 - sprzedaż MARKA Spółka z kontrahentami.csv`
- plik kontrahentów CSV: `data/input/Kontrahenci_Marka_spolka_converted.csv`
- plik wynikowy TXT: `data/output/2025-09_sprzedaz_MARKA_ZOO_OPTIMA.txt`

## Gdzie są wykorzystywane w kodzie

W `converter/przetwarzaj_zestawienia.py`:

- `plik_kontrahenci` jest wczytywany przez `pd.read_csv(...)`
- `plik_csv` jest wczytywany przez `pd.read_csv(...)`
- `plik_koncowy` jest zapisywany przez `open(..., "w", ...)`

Dodatkowo skrypt tworzy plik tymczasowy:

- `data/temp/temp_csv_optima.txt`

## Istotna uwaga o obecnym stanie workspace

W aktualnym katalogu roboczym nie widać wymaganych plików wejściowych wskazanych w `config.ini`.

Obecnie w `data/input` znajduje się tylko:

- `data/input/readme.md`

To oznacza, że uruchomienie konfiguracji `Debug: analiza_zestawienia_faktur` w obecnym stanie najprawdopodobniej zakończy się błędem braku plików wejściowych.
