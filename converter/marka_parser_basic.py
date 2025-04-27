# === marka_parser_basic.py ===
from typing import List, Dict, Optional
from pathlib import Path
import re


def parse_marka_sales_basic(filepath: Path) -> List[Dict[str, str]]:
    parsed_rows = []

    with filepath.open('r', encoding='utf-8') as file:
        lines = file.readlines()

    current_invoice = None
    current_contractor_name = None
    current_contractor_nip = None

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if is_contractor_line(line):
            current_contractor_name, current_contractor_nip = extract_contractor_data(line)
            continue

        if is_invoice_line(line):
            if current_invoice:
                parsed_rows.append(current_invoice)

            numer_faktury, data_wystawienia, data_sprzedazy, wartosc_brutto, stawka_vat, wartosc_netto, wartosc_vat, suma_podatkow_vat = extract_invoice_data(line)

            current_invoice = {
                'data_wystawienia': data_wystawienia,
                'data_sprzedazy': data_sprzedazy,
                'numer_faktury': numer_faktury,
                'nazwa_kontrahenta': current_contractor_name,
                'nip': current_contractor_nip,
                'wartosc_netto': wartosc_netto if wartosc_netto else 0.0,
                'wartosc_brutto': wartosc_brutto if wartosc_brutto else 0.0,
                'vat': wartosc_vat if wartosc_vat else 0.0,
                'suma_podatkow_vat': suma_podatkow_vat if suma_podatkow_vat else 0.0,
                'stawki_vat': []
            }

            # Jeśli jest stawka VAT na fakturze (nawet zwolniona), dodajemy do listy stawek VAT
            if stawka_vat is not None:
                current_invoice['stawki_vat'].append({
                    'stawka': stawka_vat,
                    'netto': wartosc_netto or 0.0,
                    'vat': wartosc_vat or 0.0
                })
            continue

        if is_additional_vat_line(line) and current_invoice:
            vat_rate, vat_netto, vat_value = extract_additional_vat(line)
            if vat_rate is not None:
                current_invoice['stawki_vat'].append({
                    'stawka': vat_rate,
                    'netto': vat_netto,
                    'vat': vat_value
                })

    if current_invoice:
        parsed_rows.append(current_invoice)

    return parsed_rows

# === Pomocnicze funkcje ===

def is_contractor_line(line: str) -> bool:
    return bool(re.search(r'NIP\s*\d{10}', line))


def is_invoice_line(line: str) -> bool:
    return bool(re.match(r'^"?\d+"?,', line))


def is_additional_vat_line(line: str) -> bool:
    return line.startswith('"","","","","","')


def extract_contractor_data(line: str) -> (Optional[str], Optional[str]):
    # Szukamy numeru NIP
    nip_match = re.search(r'NIP\s*(\d{10})', line)
    nip = nip_match.group(1) if nip_match else None

    if nip_match:
        # Jeśli jest NIP, bierzemy wszystko do miejsca, gdzie zaczyna się NIP
        name_part = line[:nip_match.start()]
    else:
        # Jeśli nie ma NIP, szukamy frazy 'dotyczy:'
        dotyczy_match = re.search(r'dotyczy:', line, re.IGNORECASE)
        if dotyczy_match:
            name_part = line[:dotyczy_match.start()]
        else:
            # Jeśli nie ma ani NIP, ani 'dotyczy:', bierzemy całą linię
            name_part = line

    # Usuwamy nadmiarowe cudzysłowy i przecinki na końcu
    name_part = name_part.replace('"', '').strip()
    name_part = re.sub(r',$', '', name_part).strip()

    return name_part, nip


def extract_invoice_data(line: str) -> (Optional[str], Optional[str], Optional[str], Optional[float], Optional[float], Optional[float], Optional[float], Optional[float]):
    parts = [p.strip('"') for p in line.split('","')]
    if len(parts) < 10:
        return None, None, None, None, None, None, None, None

    numer_faktury = parts[1]
    data_wystawienia = parts[2].replace('.', '-') if parts[2] else None
    data_sprzedazy = parts[3].replace('.', '-') if parts[3] else None

    try:
        wartosc_brutto = float(parts[4].replace(',', '.')) if parts[4] else 0.0

        if parts[5] and parts[5] != 'zw.':
            stawka_vat = float(parts[5].replace('%', '').replace(',', '.'))
        else:
            stawka_vat = 0.0

        wartosc_netto = float(parts[6].replace(',', '.')) if parts[6] else 0.0
        wartosc_vat = float(parts[7].replace(',', '.')) if parts[7] else 0.0
        suma_podatkow_vat = float(parts[9].replace(',', '.')) if parts[9] else 0.0

        return numer_faktury, data_wystawienia, data_sprzedazy, wartosc_brutto, stawka_vat, wartosc_netto, wartosc_vat, suma_podatkow_vat
    except ValueError:
        return None, None, None, None, None, None, None, None


def extract_additional_vat(line: str) -> (Optional[float], Optional[float], Optional[float]):
    parts = [p.strip('"') for p in line.split('","')]
    if len(parts) < 8:
        return None, None, None
    try:
        vat_rate = float(parts[5].replace('%', '').replace(',', '.')) if parts[5] else 0.0
        vat_netto = float(parts[6].replace(',', '.')) if parts[6] else 0.0
        vat_value = float(parts[7].replace(',', '.')) if parts[7] else 0.0
        return vat_rate, vat_netto, vat_value
    except ValueError:
        return None, None, None
