# csv_reader.py
import pandas as pd

def read_csv_file(filepath: str) -> pd.DataFrame:
    """Wczytaj dane z pliku CSV."""
    df = pd.read_csv(filepath, delimiter=';', encoding='utf-8')
    return df
