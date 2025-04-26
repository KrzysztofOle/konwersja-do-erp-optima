# === main.py ===

import sys
import configparser
from tkinter import Tk
from gui.gui import App
from controller.controller import Controller


def main():
    config = configparser.ConfigParser()
    config.read('config.ini')

    if '--nogui' in sys.argv:
        print("Tryb bez GUI - automatyczne przetwarzanie danych...")
        controller = Controller(config)
        controller.przetworz_dane()
    else:
        root = Tk()
        app = App(root)
        root.mainloop()


if __name__ == "__main__":
    main()
