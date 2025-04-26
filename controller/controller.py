# === controller.py ===

from pathlib import Path
from tkinter import messagebox
from converter.processor import analiza_zestawienia_faktur


class Controller:
    def __init__(self, config):
        if not config.has_section('sciezki'):
            raise ValueError("Brakuje sekcji [sciezki] w pliku config.ini!")
        self.sciezka_lista_firm = Path(config.get('sciezki', 'sciezka_lista_firm'))
        self.sciezka_pliku_csv = Path(config.get('sciezki', 'sciezka_pliku_csv'))

    def set_lista_firm_path(self, path):
        self.sciezka_lista_firm = Path(path)

    def set_plik_csv_path(self, path):
        self.sciezka_pliku_csv = Path(path)

    def sprawdz_sciezke(self, path: Path) -> bool:
        return path.exists() and path.is_file()

    def przetworz_dane(self):
        if not self.sprawdz_sciezke(self.sciezka_lista_firm):
            messagebox.showerror('Nieprawidłowy plik', 'Wadliwa ścieżka do listy firm!')
            return None

        if not self.sprawdz_sciezke(self.sciezka_pliku_csv):
            messagebox.showerror('Nieprawidłowy plik', 'Wadliwa ścieżka do pliku sprzedaży!')
            return None

        wynikowy_plik = self.sciezka_pliku_csv.with_stem(self.sciezka_pliku_csv.stem + "_OPTIMA").with_suffix(".txt")
        result = analiza_zestawienia_faktur(self.sciezka_pliku_csv, self.sciezka_lista_firm, wynikowy_plik)
        messagebox.showinfo('Zakończono analizę', f"Wynik zapisany do: {result}")
        return result