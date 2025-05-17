"""
Gui aplikacji
Plik: gui/gui.py
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import configparser
from pathlib import Path
from controller.controller import Controller


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Import zestawienia sprzedaży Marka")
        self.root.geometry("400x500")

        # Wczytaj konfigurację
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.controller = Controller(config)

        # Budowa GUI
        self.build_gui()

    def build_gui(self):
        # Sekcja: Lista firm
        self.label_lista_firm = tk.Label(self.root, text=str(self.controller.sciezka_lista_firm), wraplength=380)
        self.button_lista_firm = tk.Button(
            self.root,
            text="Wybierz plik CSV z firmami",
            command=self.wybierz_lista_firm,
            font=("Arial", 12, "bold")
        )
        self.button_lista_firm.pack(fill=tk.X, padx=10, pady=10)
        self.label_lista_firm.pack(fill=tk.X, padx=10, pady=10)

        self.separator1 = tk.Canvas(self.root, height=3, bg="gray", highlightthickness=1)
        self.separator1.pack(fill=tk.X, padx=10, pady=10)

        # Sekcja: Plik sprzedaży
        self.label_plik_csv = tk.Label(self.root, text=str(self.controller.sciezka_pliku_csv), wraplength=380)
        self.button_plik_csv = tk.Button(
            self.root,
            text="Wybierz plik CSV do importu",
            command=self.wybierz_plik_csv,
            font=("Arial", 12, "bold")
        )
        self.button_plik_csv.pack(fill=tk.X, padx=10, pady=10)
        self.label_plik_csv.pack(fill=tk.X, padx=10, pady=10)

        # Sekcja: Plik wynikowy (nowe pole)
        self.separator2 = tk.Canvas(self.root, height=3, bg="gray", highlightthickness=1)
        self.separator2.pack(fill=tk.X, padx=10, pady=10)

        self.label_plik_wynikowy = tk.Label(self.root, text="Plik wynikowy:", anchor="w")
        self.label_plik_wynikowy.pack(fill=tk.X, padx=10)
        self.entry_plik_wynikowy = tk.Entry(self.root)
        self.entry_plik_wynikowy.insert(0, str(self.controller.sciezka_pliku_wynikowego))
        self.entry_plik_wynikowy.pack(fill=tk.X, padx=10, pady=5)

        # Sekcja: Start
        self.separator3 = tk.Canvas(self.root, height=3, bg="gray", highlightthickness=1)
        self.separator3.pack(fill=tk.X, padx=10, pady=10)

        self.button_start = tk.Button(
            self.root,
            text="Uruchom przetwarzanie",
            command=self.uruchom_przetwarzanie,
            font=("Arial", 16, "bold")
        )
        self.button_start.pack(fill=tk.X, padx=10, pady=20)

    def wybierz_lista_firm(self):
        default_dir = self.controller.sciezka_lista_firm.parent if self.controller.sciezka_lista_firm.exists() else "data/input"
        file_path = filedialog.askopenfilename(
            initialdir=default_dir,
            title="Wybierz plik CSV z firmami",
            filetypes=[("Pliki CSV", "*.csv")]
        )
        if file_path and self._plik_jest_lista_firm(file_path):
            self.controller.set_lista_firm_path(file_path)
            self.label_lista_firm.config(text=f"Plik z firmami: {file_path}")
        elif file_path:
            messagebox.showerror("Błąd pliku", "Wybrany plik nie wygląda na listę firm (brak nagłówka z kolumnami: Kod;Nazwa;NIP;...)")

    def wybierz_plik_csv(self):
        default_dir = self.controller.sciezka_pliku_csv.parent if self.controller.sciezka_pliku_csv.exists() else "data/input"
        file_path = filedialog.askopenfilename(
            initialdir=default_dir,
            title="Wybierz plik CSV do importu",
            filetypes=[("Pliki CSV", "*.csv")]
        )
        if file_path and self._plik_jest_zestawieniem_sprzedazy(file_path):
            self.controller.set_plik_csv_path(file_path)
            self.label_plik_csv.config(text=f"Plik sprzedaży: {file_path}")
            # Automatycznie ustaw ścieżkę pliku wynikowego na podstawie pliku wejściowego
            wynikowa_sciezka = self._generuj_nazwe_wynikowa(Path(file_path))
            self.entry_plik_wynikowy.delete(0, tk.END)
            self.entry_plik_wynikowy.insert(0, str(wynikowa_sciezka))
        elif file_path:
            messagebox.showerror("Błąd pliku", "Wybrany plik nie wygląda na plik sprzedaży (brak drugiego wiersza: \"Zestawienie dokumentów sprzedaży wg daty księgowej\")")

    def _plik_jest_lista_firm(self, filepath):
        try:
            with open(filepath, encoding="utf-8-sig") as f:
                naglowek = f.readline().strip()
                kolumny = [col.strip().lower().lstrip('\ufeff') for col in naglowek.split(';')]
                wymagane = {"kod", "nazwa", "nip"}
                if not wymagane.issubset(set(kolumny)):
                    print("❌ BŁĄD: W pliku nie znaleziono wymaganych kolumn: Kod, Nazwa, NIP")
                    print("🔍 Nagłówek wykryty w pliku firm:", kolumny)
                    return False
                return True
        except Exception as e:
            print("❗ Błąd podczas walidacji pliku firm:", e)
            return False

    def _plik_jest_zestawieniem_sprzedazy(self, filepath):
        try:
            with open(filepath, encoding="utf-8") as f:
                _ = f.readline()  # pomijamy pierwszy wiersz
                drugi_wiersz = f.readline().strip().strip('"')
                return drugi_wiersz.startswith("Zestawienie dokumentów sprzedaży wg daty księgowej")
        except Exception:
            return False

    def _generuj_nazwe_wynikowa(self, sciezka_csv: Path) -> Path:
        suffix = "_OPTIMA.txt"
        # Pobieramy katalog z config.ini
        folder_z_ini = self.controller.sciezka_pliku_wynikowego.parent
        # Tworzymy nową nazwę pliku
        nowa_nazwa = sciezka_csv.stem + suffix
        return folder_z_ini / nowa_nazwa

    def uruchom_przetwarzanie(self):
        # Przechwycenie ścieżki z pola tekstowego
        wynikowa_sciezka = self.entry_plik_wynikowy.get().strip()
        if wynikowa_sciezka:
            self.controller.sciezka_pliku_wynikowego = Path(wynikowa_sciezka)
        self.controller.przetworz_dane()
