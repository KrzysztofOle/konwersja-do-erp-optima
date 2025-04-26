# txt_writer.py

def write_txt_file(data: str, filepath: str):
    """Zapisz dane do pliku TXT."""
    with open(filepath, 'w', encoding='utf-8') as file:
        file.write(data)
