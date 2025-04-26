# === marka_parser.py ===
from typing import List, Dict, Optional
from pathlib import Path
from converter.contractor_matcher import ContractorMatcher
import re


def parse_marka_sales(filepath: Path, contractor_matcher: ContractorMatcher) -> List[Dict[str, str]]:
    """
    Parsuje plik płaski sprzedaz.csv od Marka JDG do struktury danych zgodnej z wymaganiami ERP Optima.

    :param filepath: Ścieżka do pliku CSV.
    :param contractor_matcher: Instancja ContractorMatcher do dopasowania kontrahentów.
    :return: Lista słowników zawierających dane sprzedaży.
    """
    parsed_rows = []

    with filepath.open('r', encoding='utf-8') as file:
        lines = file.readlines()

    current_date = None
    current_contractor_name = None
    current_contractor_nip = None

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if is_date_line(line):
            current_date = extract_date(line)
            continue

        if is_contractor_line(line):
            current_contractor_name, current_contractor_nip = match_contractor(line, contractor_matcher)
            continue

        numer_faktury, netto, brutto = extract_invoice_data(line)

        if numer_faktury and netto and brutto:
            try:
                vat = round(float(brutto) - float(netto), 2)
            except ValueError:
                vat = ''

            parsed_rows.append({
                'data_wystawienia': current_date,
                'data_sprzedazy': current_date,
                'numer_faktury': numer_faktury,
                'nazwa_kontrahenta': current_contractor_name,
                'nip': current_contractor_nip,
                'wartosc_netto': netto,
                'wartosc_brutto': brutto,
                'vat': vat,
            })

    return parsed_rows


def is_date_line(line: str) -> bool:
    return bool(re.search(r'\d{4}-\d{2}-\d{2}', line))


def extract_date(line: str) -> Optional[str]:
    match = re.search(r'(\d{4}-\d{2}-\d{2})', line)
    return match.group(1) if match else None


def is_contractor_line(line: str) -> bool:
    # Zakładamy, że linia z kontrahentem nie zawiera cyfr kwotowych
    return any(c.isalpha() for c in line) and not any(c.isdigit() for c in line.split()[-1])


def match_contractor(line: str, contractor_matcher: ContractorMatcher) -> (Optional[str], Optional[str]):
    contractor = contractor_matcher.match_by_name_fragment(line)
    if contractor:
        return contractor.name, contractor.nip
    return line, None


def extract_invoice_data(line: str) -> (Optional[str], Optional[float], Optional[float]):
    parts = line.split(';')
    if len(parts) < 3:
        return None, None, None

    numer_faktury = parts[0].strip()
    try:
        netto = float(parts[1].replace(',', '.'))
        brutto = float(parts[2].replace(',', '.'))
        return numer_faktury, netto, brutto
    except ValueError:
        return None, None, None
