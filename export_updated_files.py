"""
Tworzy plik ZIP z wybranymi plikami projektu (np. .py, .ini, .csv)
Opcjonalnie: tylko pliki zmodyfikowane w ostatnich N minutach.

Plik: export_updated_files.py
"""

import zipfile
from pathlib import Path
import time
from datetime import datetime

# --- PARAMETRY ---

# Ścieżka do katalogu głównego projektu
PROJECT_FOLDER = Path("/Users/krzysztof/PycharmProjects/konwersja-do-erp-optima")  # np. Path("C:/Users/Krzysztof/PycharmProjects/Optima_SOTAX")

# Nazwa pliku wynikowego ZIP
OUTPUT_ZIP = Path("pakiet_aktualizacji.zip")

# Typy plików do zebrania
EXTENSIONS = {'.py', '.ini', '.csv'}

# Ile minut wstecz sprawdzać datę modyfikacji (None = bierz wszystkie)
MINUTES_BACK = 28800  # np. 10 28800=8h


# --- FUNKCJA GŁÓWNA ---
def create_zip_with_updates():
    files_to_zip = []

    for file in PROJECT_FOLDER.rglob('*'):
        if file.is_file() and file.suffix.lower() in EXTENSIONS:
            if MINUTES_BACK is None:
                files_to_zip.append(file)
            else:
                mtime = file.stat().st_mtime
                age_minutes = (time.time() - mtime) / 60
                if age_minutes <= MINUTES_BACK:
                    files_to_zip.append(file)

    if not files_to_zip:
        print("⚠️ Nie znaleziono żadnych plików do spakowania.")
        return

    with zipfile.ZipFile(OUTPUT_ZIP, 'w', compression=zipfile.ZIP_DEFLATED) as zipf:
        for file in files_to_zip:
            rel_path = file.relative_to(PROJECT_FOLDER)
            zipf.write(file, rel_path)
            print(f"✅ Dodano: {rel_path}")

    print(f"\n📦 Plik ZIP utworzony: {OUTPUT_ZIP.resolve()}")


# --- PUNKT STARTOWY ---
if __name__ == '__main__':
    create_zip_with_updates()