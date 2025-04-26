# === main.py ===
import sys
import configparser
from tkinter import Tk
from gui.gui import App
from controller.controller import Controller
from converter.przetwarzaj_zestawienia import analiza_zestawienia_faktur


def main():
    config = configparser.ConfigParser()
    config.read('config.ini')

    if '--nogui' in sys.argv:
        print("[INFO] Tryb bez GUI - automatyczne przetwarzanie danych...")
        controller = Controller(config, gui_mode=False)
        try:
            controller.przetworz_dane()
        except ValueError as e:
            print(f"[BŁĄD] {e}")
    else:
        root = Tk()
        app = App(root)
        root.mainloop()


if __name__ == "__main__":
    main()
