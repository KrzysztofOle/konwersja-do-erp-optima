# -*- coding: utf-8 -*-
"""
summary_parser.py — parser PODSUMOWANIA z raportu DOM 5 (sprzedaż z kontrahentami)

Zmiana: funkcja parse_summary_from_dom5_csv() ZWRACA teraz **słownik** (dict),
ułatwiający dalsze wykorzystanie danych.
Struktura zwracanego dict-a:

{
  "categories": [
    {
      "name": "<nazwa kategorii>",
      "totals": {"gross": float, "net": float, "vat": float},
      "rates": [
        {"rate": "zw.", "gross": float, "net": float, "vat": float},
        {"rate": "8%",  "gross": float, "net": float, "vat": float},
        {"rate": "23%", "gross": float, "net": float, "vat": float},
        ...
      ]
    },
    ...
  ],
  "overall": {
    "label": "Ogółem:",
    "totals": {"gross": float, "net": float, "vat": float},
    "rates": [
      {"rate": "...", "gross": float, "net": float, "vat": float},
      ...
    ]
  }
}
"""

from __future__ import annotations
from pathlib import Path
from typing import List, Optional, Dict, Any
import csv
import re


# ====== KONWERSJE ======

def _to_float(s: Optional[str]) -> float:
    """
    Odporna konwersja liczby do float.
    - przycina cudzysłowy i spacje
    - zamienia przecinki dziesiętne na kropki
    - wyłuskuje pierwszy *pełny* literał liczbowy: [-+]?\\d+(?:\\.\\d+)?
    """
    if s is None:
        return 0.0
    s = str(s).strip().strip('"').strip("'")
    if not s:
        return 0.0
    s = s.replace("\\u00A0", " ")  # NBSP (w treści może trafić jako dosłowny znak, ale i jako ucieczka)
    s = s.replace("\u00A0", " ")
    s = s.replace(" ", "")
    s = s.replace(",", ".")
    m = re.search(r"[-+]?\d+(?:\.\d+)?", s)
    if not m:
        return 0.0
    try:
        return float(m.group(0))
    except ValueError:
        return 0.0


def _is_empty(cell: Optional[str]) -> bool:
    return cell is None or cell == ""


def _row_is_category_header(row: List[str]) -> bool:
    c0 = (row[0] or "").strip()
    return bool(c0) and c0 != "Ogółem:"


def _row_is_rate_line(row: List[str]) -> bool:
    # pusta nazwa w kol0, stawka w kol5 (np. "zw.", "8%", "23%")
    return _is_empty(row[0]) and bool((row[5] or "").strip())


def _row_is_overall_header(row: List[str]) -> bool:
    return (row[0] or "").strip() == "Ogółem:"


# ====== PARSER ======

def parse_summary_from_dom5_csv(filepath: Path | str) -> Dict[str, Any]:
    """
    Parsuje dwuczęściowe podsumowanie wg opisu:
      - Start od wiersza: "Razem rejestry w rozbiciu: "
      - Część 1: kategorie + ich stawki VAT
      - Część 2: "Ogółem:" + stawki VAT

    Zwraca dict zgodnie ze strukturą w nagłówku pliku.
    Kolumny w CSV (wg przykładów):
      [0] = kategoria / "" / "Ogółem:"
      [4] = brutto
      [5] = stawka VAT (np. "zw.", "8%", "23%")
      [6] = netto
      [7] = VAT
    """
    fp = Path(filepath)

    rows: List[List[str]] = []
    with fp.open("r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter=",", quotechar='"')
        for r in reader:
            # Upewnij się, że mamy co najmniej 11 kolumn (jak w przykładach)
            if len(r) < 11:
                r = r + [""] * (11 - len(r))
            rows.append(r)

    # Znajdź punkt startowy
    start_idx = None
    for i, r in enumerate(rows):
        if (r[0] or "").strip() == "Razem rejestry w rozbiciu:":
            start_idx = i + 1  # zaczynamy od kolejnej linii
            break

    result: Dict[str, Any] = {"categories": [], "overall": None}

    if start_idx is None:
        return result

    i = start_idx

    # --- Część 1: kategorie + rozbicia stawek ---
    while i < len(rows):
        row = rows[i]
        if _row_is_overall_header(row):
            break  # przechodzimy do części 2
        if _row_is_category_header(row):
            name = (row[0] or "").strip()
            gross = _to_float(row[4])
            net = _to_float(row[6])
            vat = _to_float(row[7])

            cat_dict: Dict[str, Any] = {
                "name": name,
                "totals": {"gross": gross, "net": net, "vat": vat},
                "rates": []
            }

            # zbierz linie stawek dla tej kategorii
            j = i + 1
            while j < len(rows) and _row_is_rate_line(rows[j]):
                rj = rows[j]
                rate_label = (rj[5] or "").strip()
                rate_gross = _to_float(rj[4])
                rate_net = _to_float(rj[6])
                rate_vat = _to_float(rj[7])
                cat_dict["rates"].append({
                    "rate": rate_label,
                    "gross": rate_gross,
                    "net": rate_net,
                    "vat": rate_vat
                })
                j += 1

            result["categories"].append(cat_dict)
            i = j
            continue
        i += 1

    # --- Część 2: ogółem + rozbicie stawek ---
    while i < len(rows):
        row = rows[i]
        if _row_is_overall_header(row):
            gross = _to_float(row[4])
            net = _to_float(row[6])
            vat = _to_float(row[7])
            overall_dict: Dict[str, Any] = {
                "label": "Ogółem:",
                "totals": {"gross": gross, "net": net, "vat": vat},
                "rates": []
            }
            j = i + 1
            while j < len(rows) and _row_is_rate_line(rows[j]):
                rj = rows[j]
                rate_label = (rj[5] or "").strip()
                rate_gross = _to_float(rj[4])
                rate_net = _to_float(rj[6])
                rate_vat = _to_float(rj[7])
                overall_dict["rates"].append({
                    "rate": rate_label,
                    "gross": rate_gross,
                    "net": rate_net,
                    "vat": rate_vat
                })
                j += 1
            result["overall"] = overall_dict
            break
        i += 1

    return result


# ====== POMOCNICZE WYPISYWANIE (dla uruchomienia standalone) ======

def print_summary_dict(data: Dict[str, Any]) -> None:
    print("\n== PODSUMOWANIE WG KATEGORII ==")
    for cat in data.get("categories", []):
        t = cat["totals"]
        print(f'- {cat["name"]}: brutto={t["gross"]:.2f}, netto={t["net"]:.2f}, VAT={t["vat"]:.2f}')
        for r in cat.get("rates", []):
            print(f'    • {r["rate"]:<4}  brutto={r["gross"]:.2f}  netto={r["net"]:.2f}  VAT={r["vat"]:.2f}')

    overall = data.get("overall")
    if overall:
        t = overall["totals"]
        print("\n== OGÓŁEM ==")
        print(f'{overall["label"]}: brutto={t["gross"]:.2f}, netto={t["net"]:.2f}, VAT={t["vat"]:.2f}')
        if overall.get("rates"):
            print("  Rozbicie VAT ogółem:")
            for r in overall["rates"]:
                print(f'    • {r["rate"]:<4}  brutto={r["gross"]:.2f}  netto={r["net"]:.2f}  VAT={r["vat"]:.2f}')


# ====== URUCHOMIENIE STANDALONE (config.ini) ======

if __name__ == "__main__":
    import configparser

    config = configparser.ConfigParser()
    config.read('config.ini')

    plik = Path(config['sciezki']['sciezka_pliku_csv'])

    res = parse_summary_from_dom5_csv(plik)
    print("\n\n== PODSUMOWANIA ==")
    print(f'  dla pliku: {plik}\n')
    print_summary_dict(res)
