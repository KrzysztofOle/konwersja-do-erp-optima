# main.py
import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import logging
from utils.csv_reader import read_csv_file
from utils.txt_writer import write_txt_file
from converter.dom5_parser import Dom5Parser
from converter.contractor_matcher import ContractorMatcher
from converter.optima_formatter import OptimaFormatter

logging.basicConfig(filename='logs/konwersja.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Konwersja raportów do ERP Optima")

        self.sales_csv_path = None
        self.contractors_csv_path = None
        self.output_txt_path = None

        self.create_widgets()

    def create_widgets(self):
        tk.Button(self.root, text="Wybierz plik sprzedaży (CSV)", command=self.select_sales_file).pack(pady=5)
        tk.Button(self.root, text="Wybierz plik kontrahentów (CSV)", command=self.select_contractors_file).pack(pady=5)
        tk.Button(self.root, text="Wybierz miejsce zapisu (TXT)", command=self.select_output_file).pack(pady=5)
        tk.Button(self.root, text="Konwertuj", command=self.convert_files).pack(pady=10)

        self.log_text = tk.Text(self.root, height=10, width=80)
        self.log_text.pack(pady=5)

    def log_message(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        logging.info(message)

    def select_sales_file(self):
        self.sales_csv_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if self.sales_csv_path:
            self.log_message(f"Wybrano plik sprzedaży: {self.sales_csv_path}")

    def select_contractors_file(self):
        self.contractors_csv_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if self.contractors_csv_path:
            self.log_message(f"Wybrano plik kontrahentów: {self.contractors_csv_path}")

    def select_output_file(self):
        self.output_txt_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if self.output_txt_path:
            self.log_message(f"Wybrano plik docelowy: {self.output_txt_path}")

    def convert_files(self):
        try:
            if not all([self.sales_csv_path, self.contractors_csv_path, self.output_txt_path]):
                messagebox.showerror("Błąd", "Proszę wybrać wszystkie pliki przed rozpoczęciem konwersji.")
                return

            # Wczytaj dane
            sales_df = read_csv_file(self.sales_csv_path)

            # Przetwórz dane sprzedaży
            sales_df = Dom5Parser.parse(sales_df)

            # Dopasuj kontrahentów
            matcher = ContractorMatcher(self.contractors_csv_path)
            sales_df = sales_df.apply(matcher.enrich_row_with_contractor, axis=1)

            # Sformatuj dane do TXT
            txt_data = OptimaFormatter.format(sales_df)

            # Zapisz dane do pliku
            write_txt_file(txt_data, self.output_txt_path)

            self.log_message("Konwersja zakończona sukcesem.")
            messagebox.showinfo("Sukces", "Plik został poprawnie wygenerowany!")

        except Exception as e:
            self.log_message(f"Błąd: {e}")
            messagebox.showerror("Błąd", f"Wystąpił błąd: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ConverterApp(root)
    root.mainloop()
