# **SOTAX i ERP Optima BR**

# Konwersja do ERP Optima

## Opis projektu
Aplikacja w Pythonie konwertująca pliki raportów CSV z systemu DOM 5 do formatu TXT zgodnego z Comarch ERP Optima.

## Wymagania
- Python 3.10+
- Biblioteki z `requirements.txt`

## Instalacja
```bash
pip install -r requirements.txt
```

## Struktura projektu
```
konwersja_erp_optima/
├── config/                 # Konfiguracja aplikacji
├── data/                   # Dane wejściowe i wyjściowe
│   ├── input/              # Pliki wejściowe CSV
│   └── output/             # Pliki wyjściowe TXT
├── utils/                  # Narzędzia pomocnicze do obsługi plików
│   ├── csv_reader.py       # Moduł do czytania plików CSV
│   └── txt_writer.py       # Moduł do zapisywania plików TXT
├── converter/              # Parsowanie i formatowanie danych
│   ├── dom5_parser.py      # Parser danych systemu Dom5
│   ├── contractor_matcher.py # Dopasowanie kontrahentów
│   └── optima_formatter.py # Formatter danych do formatu Optima
├── logs/                   # Pliki logów aplikacji
├── tests/                  # Testy jednostkowe
│   ├── test_dom5_parser.py
│   └── test_optima_formatter.py
├── main.py                 # Główny plik uruchamiający aplikację z GUI
├── requirements.txt        # Lista zależności
└── README.md               # Dokumentacja projektu
```

## Uruchomienie aplikacji

```bash
python main.py <ścieżka_do_pliku_wejściowego.csv> <ścieżka_do_pliku_wyjściowego.txt>
```

### Przykład
```bash
python main.py data/input/raport_dom5.csv data/output/raport_optima.txt
```

## Testowanie

Aby uruchomić testy jednostkowe:
```bash
python -m unittest discover tests
```

## Autor
Projekt rozwijany w ramach konwersji raportów dla systemu ERP Optima BR.
