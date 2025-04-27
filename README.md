# **SOTAX i ERP Optima BR**

# Konwersja danych DOM 5 → ERP Optima

## Opis projektu
Aplikacja w Pythonie konwertująca pliki raportów CSV (moduł **Sprzedaż Zarządcy dla Wspólnot** z systemu DOM 5) na pliki TXT zgodne z formatem importu faktur do programu **Comarch ERP Optima**.

Aktualny parser obsługuje:
- rozpoznawanie faktur,
- rozdzielanie stawek VAT (w tym wiele stawek na jednej fakturze),
- weryfikację poprawności danych,
- dopasowanie kontrahentów po NIP.

## Wymagania
- Python 3.10 lub nowszy
- Biblioteki wymienione w pliku `requirements.txt`

## Instalacja
```bash
pip install -r requirements.txt
```

## Struktura projektu
```
konwersja_erp_optima/
├── config/                  # Konfiguracja aplikacji
├── data/
│   ├── input/               # Pliki źródłowe CSV (np. sprzedaz.csv, listaFirm.csv)
│   └── output/              # Wygenerowane pliki TXT
├── converter/
│   ├── marka_parser_basic.py    # Parser podstawowy (bez dopasowania kontrahentów)
│   ├── marka_parser.py          # Parser faktur z dopasowaniem NIP
│   ├── contractor_matcher.py    # Moduł dopasowujący kontrahentów po NIP
│   └── optima_formatter.py      # (planowane) formatowanie danych do pliku TXT
├── utils/
│   ├── csv_reader.py            # (planowane) Czytanie plików CSV
│   └── txt_writer.py            # (planowane) Zapisywanie plików TXT
├── logs/                        # Pliki logów
├── tests/                       # Testy jednostkowe
│   ├── test_marka_parser_basic.py
│   └── test_marka_parser.py
├── main.py                      # (planowane) Uruchamianie aplikacji z GUI
├── requirements.txt             # Lista zależności
└── README.md                    # Dokumentacja projektu
```

## Uruchomienie parsera

Aktualnie parser uruchamiamy bez GUI:
```bash
python -m tests.test_marka_parser_basic
python -m tests.test_marka_parser
```

W przyszłości (po ukończeniu main.py) planowane:
```bash
python main.py <ścieżka_do_pliku_wejściowego.csv> <ścieżka_do_pliku_wyjściowego.txt>
```

### Przykład
```bash
python main.py data/input/sprzedaz.csv data/output/sprzedaz_optima.txt
```

## Testowanie

Aby uruchomić wszystkie testy jednostkowe:
```bash
python -m unittest discover tests
```

Testy obejmują:
- liczbę poprawnie sparsowanych faktur,
- poprawność numeracji faktur,
- obecność i poprawność stawek VAT,
- porównanie sumy podatków VAT ze sumą na fakturze.

## Autor
Projekt rozwijany w ramach **konwersji raportów dla ERP Optima BR**.  
Wersja robocza (kwiecień 2025).
