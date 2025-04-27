from typing import List, Dict, Optional
from pathlib import Path
import re
from converter.contractor_matcher import ContractorMatcher


def parse_marka_sales(filepath: Path, contractor_matcher: ContractorMatcher) -> List[Dict[str, str]]:
    parsed_rows = []

    with filepath.open('r', encoding='utf-8') as file:
        lines = file.readlines()

    current_invoice = None
    current_contractor_name = None
    current_contractor_nip = None

    for idx, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue

        if is_contractor_line(line):
            current_contractor_name, current_contractor_nip = extract_contractor_data(line, contractor_matcher)
            continue

        if is_invoice_line(line):
            # Jeśli mamy już fakturę — zapisz ją przed rozpoczęciem nowej
            if current_invoice:
                parsed_rows.append(current_invoice)

            # Nowa faktura
            numer_faktury, data_wystawienia, data_sprzedazy, wartosc_netto, wartosc_brutto = extract_invoice_data(line)
            current_invoice = {
                'data_wystawienia': data_wystawienia,
                'data_sprzedazy': data_sprzedazy,
                'numer_faktury': numer_faktury,
                'nazwa_kontrahenta': current_contractor_name,
                'nip': current_contractor_nip,
                'wartosc_netto': wartosc_netto,
                'wartosc_brutto': wartosc_brutto,
                'vat': round(wartosc_brutto - wartosc_netto, 2),
                'stawki_vat': []  # Lista stawek VAT
            }
            continue

        if is_additional_vat_line(line) and current_invoice:
            vat_rate, vat_netto, vat_value = extract_additional_vat(line)
            if vat_rate is not None:
                current_invoice['stawki_vat'].append({
                    'stawka': vat_rate,
                    'netto': vat_netto,
                    'vat': vat_value
                })

    # Dodaj ostatnią fakturę
    if current_invoice:
        parsed_rows.append(current_invoice)

    return parsed_rows


def is_contractor_line(line: str) -> bool:
    return bool(re.search(r'NIP\s*\d{10}', line))


def is_invoice_line(line: str) -> bool:
    return bool(re.match(r'^\"?\d+\"?,', line))


def is_additional_vat_line(line: str) -> bool:
    return line.startswith('"","","","","","')


def extract_contractor_data(line: str, contractor_matcher: ContractorMatcher) -> (Optional[str], Optional[str]):
    nip_match = re.search(r'NIP\s*(\d{10})', line)
    nip = nip_match.group(1) if nip_match else None
    if nip:
        contractor = contractor_matcher.match_by_nip(nip)
        if contractor:
            return contractor.name, contractor.nip
    return line, nip


def extract_invoice_data(line: str) -> (Optional[str], Optional[str], Optional[str], Optional[float], Optional[float]):
    parts = [p.strip('"') for p in line.split('","')]
    if len(parts) < 7:
        return None, None, None, None, None

    numer_faktury = parts[1]
    data_wystawienia = parts[2].replace('.', '-')
    data_sprzedazy = parts[3].replace('.', '-')

    try:
        wartosc_brutto = float(parts[4].replace(',', '.'))
        wartosc_netto = float(parts[6].replace(',', '.'))
        return numer_faktury, data_wystawienia, data_sprzedazy, wartosc_netto, wartosc_brutto
    except ValueError:
        return None, None, None, None, None


def extract_additional_vat(line: str) -> (Optional[float], Optional[float], Optional[float]):
    parts = [p.strip('"') for p in line.split('","')]
    if len(parts) < 7:
        return None, None, None
    try:
        vat_rate = float(parts[5].replace('%', '').replace(',', '.'))
        vat_netto = float(parts[6].replace(',', '.'))
        vat_value = float(parts[7].replace(',', '.'))
        return vat_rate, vat_netto, vat_value
    except ValueError:
        return None, None, None