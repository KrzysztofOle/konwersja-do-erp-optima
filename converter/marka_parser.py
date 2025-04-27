from typing import List, Dict
from pathlib import Path
from converter.contractor_matcher import ContractorMatcher
from converter.marka_parser_basic import parse_marka_sales_basic

def parse_marka_sales(filepath: Path, contractor_matcher: ContractorMatcher) -> List[Dict[str, str]]:
    parsed_rows = parse_marka_sales_basic(filepath)

    for row in parsed_rows:
        # Jeśli mamy NIP - próbujemy znaleźć lepszego kontrahenta
        nip = row.get('nip')
        if nip:
            matched_contractor = contractor_matcher.match_by_nip(nip)
            if matched_contractor:
                row['nazwa_kontrahenta'] = matched_contractor.name
                row['nip'] = matched_contractor.nip

    return parsed_rows
