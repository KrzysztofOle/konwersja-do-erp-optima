"""
Gui aplikacji
Plik: gui/gui.py
"""

import tkinter as tk
from tkinter import filedialog
import configparser
from pathlib import Path
from controller.controller import Controller


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Import zestawienia sprzedaży Marka")
        self.root.geometry("400x400")

        # Wczytaj konfigurację
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.controller = Controller(config)

        # Budowa GUI
        self.build_gui()

    def build_gui(self):
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

        self.label_plik_csv = tk.Label(self.root, text=str(self.controller.sciezka_pliku_csv), wraplength=380)
        self.button_plik_csv = tk.Button(
            self.root,
            text="Wybierz plik CSV do importu",
            command=self.wybierz_plik_csv,
            font=("Arial", 12, "bold")
        )
        self.button_plik_csv.pack(fill=tk.X, padx=10, pady=10)
        self.label_plik_csv.pack(fill=tk.X, padx=10, pady=10)

        self.separator2 = tk.Canvas(self.root, height=3, bg="gray", highlightthickness=1)
        self.separator2.pack(fill=tk.X, padx=10, pady=10)

        self.button_start = tk.Button(
            self.root,
            text="Uruchom przetwarzanie",
            command=self.controller.przetworz_dane,
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
        if file_path:
            self.controller.set_lista_firm_path(file_path)
            self.label_lista_firm.config(text=str(file_path))

    def wybierz_plik_csv(self):
        default_dir = self.controller.sciezka_pliku_csv.parent if self.controller.sciezka_pliku_csv.exists() else "data/input"
        file_path = filedialog.askopenfilename(
            initialdir=default_dir,
            title="Wybierz plik CSV do importu",
            filetypes=[("Pliki CSV", "*.csv")]
        )
        if file_path:
            self.controller.set_plik_csv_path(file_path)
            self.label_plik_csv.config(text=str(file_path))