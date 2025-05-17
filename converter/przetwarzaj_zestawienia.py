"""
zawera analiza_zestawienia_faktur
Plik: converter/przetwarzaj_zestawienia.py
"""
# przetwarzaj_zestawienia.py


import numpy as np
import pandas as pd
import re
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import csv
from pathlib import Path

ENCODING = "utf-8-sig"   # "latin1"  #   "windows-1250"       # "utf-8"

def analiza_zestawienia_faktur(plik_csv: Path, plik_kontrahenci:Path, plik_koncowy:Path=None) -> None:
    """
    Analizuje zestawienie faktur i przygotowuje dane do importu do optimy
    :param plik_csv: Plik z danymi do importu, ale w formacie niezgodnym z optima
    :param plik_kontrahenci: Plik z kontrahentami z programu optima
    :param plik_koncowy: Wynikowy plik do zaimportowania do programu optima
    :return: None
    """

    FORMAT_DATY_IN = '%Y.%m.%d'
    FORMAT_DATY_OUT = '%y/%m/%d'

    df_kontrahenci = pd.read_csv(plik_kontrahenci, sep=";", dtype=str, encoding="utf-8")  # Podstawowy odczyt pliku
    df_kontrahenci["NIP"] = df_kontrahenci["NIP"].str.replace("-", "", regex=True)

    # Tworzenie nowej kolumny "kontrahent_opis" będącej połączeniem kilku kolumn
    # na potrzebę szukania najlepiej dopasowanych kontrahentów
    df_kontrahenci["kontrahent_opis"] = df_kontrahenci["Nazwa"] + ' ' + df_kontrahenci["Ulica"] + ' ' + df_kontrahenci["Kod pocztowy"] + ' ' + df_kontrahenci["Miasto"]

    # oczyszczamy z dużych liter
    df_kontrahenci["kontrahent_opis"] = df_kontrahenci["kontrahent_opis"].str.lower()

    # pozbywamy się zbędnych kolumn
    del df_kontrahenci['EAN']
    del df_kontrahenci['Należności PLN']
    del df_kontrahenci['Zobowiązania PLN']
    del df_kontrahenci['Telefon']
    del df_kontrahenci['Uwagi']
    del df_kontrahenci['Rejestry dłużników']

    # print('------------------------------------------------------')
    # print('KONTRAHENCI: ')
    # print(df_kontrahenci.head())  # Wyświetlenie pierwszych 5 wierszy
    # print('\n\n')

    # Wczytanie danych do DataFrame
    df = pd.read_csv(plik_csv, header=None, dtype=str)

    # pobieramy informacje z nagłówka
    # Przykładowy DataFrame


    # Znalezienie indeksu pierwszego wystąpienia 'Faktura'
    index_faktura = df[df[0] == 'Faktura'].index.min()

    # Wyciągnięcie wartości do wiersza z 'Faktura' (włącznie)
    if pd.notna(index_faktura):  # Sprawdzenie, czy 'Faktura' istnieje w kolumnie
        naglowek = df[0][:index_faktura - 3].tolist()
    else:
        naglowek = df[0].tolist()  # Jeśli 'Faktura' nie ma, pobierz całą kolumnę

    print("===================================================================")
    print(f"  przetwarzam dane z pliku: {plik_csv}")
    print("===================================================================")
    print("\n".join([str(item) for item in naglowek]))
    print("===================================================================")

    # Przesunięcie pierwszej kolumny o 1 wiersz w dół
    df[0] = df[0].shift(1)

    # Usunięcie wierszy, gdzie w kolumnie 6 (indeks 5) jest NaN
    df = df[df[5].notna()]

    # Usunięcie pierwszych dwóch wierszy i przenumerowanie indeksu
    df = df.iloc[2:].reset_index(drop=True)

    # Przypisanie nowych nazw kolumn
    kolumny = ['Dokument','nr','data_dok','data_sprz','war_brutto','stawka_vat','netto','podatek_vat','oplaty','podatek_uslugi','wyd','x']
    df.columns = kolumny

    # Znalezienie indeksu, w którym w pierwszej kolumnie znajduje się 'Razem kategoria:'
    indeks_razem = df[df['Dokument'] == 'Razem kategoria:'].index

    indeks_korekty = df[df['Dokument'] == 'Faktura korygująca'].index

    pass
    # Sprawdzenie, czy taki wiersz istnieje, i usunięcie wszystkich wierszy po nim
    if not indeks_razem.empty:
        indeks_dolny = indeks_razem[-1]  # Bierzemy pierwszy indeks
        df = df.iloc[:indeks_dolny]     # Zostawiamy wiersze przed tym indeksem

    # usuwamy ponizej
    if len(indeks_razem)>1:
        indeks_gorny = indeks_razem[0]
        df = pd.concat([df.loc[:indeks_gorny], df.loc[indeks_gorny + 1:].dropna(subset=['Dokument'])])
        # usowam pozycje Razem kategoria:
        df = df.drop(index=indeks_gorny)

    # Usunięcie wartości w kolumnie 'Dokument' tam, gdzie w kolumnie 'nr' jest NaN
    # df.loc[df['nr'].isna(), 'Dokument'] = np.NaN

    df['Dokument'] = df['Dokument'].mask(df['nr'].isna(), np.nan)

    # zamiast usowac wypelnimi poprzednimi wartosciami
    df[['Dokument', 'nr', 'data_dok', 'data_sprz', 'war_brutto']] = df[['Dokument', 'nr', 'data_dok', 'data_sprz', 'war_brutto']].fillna(method='ffill')


    # Użycie pivot_table do stworzenia kolumn dla każdej stawki VAT
    # df_wide = df.pivot_table(index=['Dokument', 'nr', 'data_dok', 'data_sprz', 'war_brutto'], columns='stawka_vat', values=['netto', 'podatek_vat'], aggfunc='first')
    df_wide = df.pivot_table(index=['Dokument', 'nr', 'data_dok', 'data_sprz', 'war_brutto'],
                             columns='stawka_vat', values=['netto', 'podatek_vat'], aggfunc='first')

    # Spłaszczenie hierarchicznych kolumn
    df_wide.columns = [f'{col[0]} {col[1]}' for col in df_wide.columns]

    kolumny = df_wide.columns
    print(kolumny)

    # Resetowanie indeksu, aby 'nr' był zwykłą kolumną
    df_wide = df_wide.reset_index()

    wymagane_kolumny = ['netto 23%', 'netto 8%', 'netto 0%', 'netto zw.',
                        'podatek_vat 23%', 'podatek_vat 8%', 'podatek_vat 0%', 'podatek_vat zw.']
    # zamieniam nan na 0.00
    for kolumna in wymagane_kolumny:
        if kolumna in df_wide.columns:
            df_wide[kolumna] = df_wide[kolumna].str.replace(',', '.').astype(float)
            df_wide[kolumna] = df_wide[kolumna].fillna(0.00)

    pass

    # Sprawdzenie brakujących kolumn
    brakujace_kolumny = [col for col in wymagane_kolumny if col not in df_wide.columns]

    # Dodanie brakujących kolumn z wartością domyślną (np. 0)
    for col in brakujace_kolumny:
        df_wide[col] = 0.00  # Możesz zmienić na np. None

    print(df_wide.dtypes)


    # Funkcja do wyciągania informacji
    def extract_info(text):
        # wspolnota = re.search(r"(WSPÓLNOTA .+?)(?=\s81)", text)
        # adres = re.search(r"(\d{2}-\d{3} \w+ .+?)(?=, NIP)", text)
        nip = re.search(r"NIP (\d+)", text)
        dotyczy = re.search(r"dotyczy:\s(.+)", text)

        return {
            # 'Wspólnota': wspolnota.group(0) if wspolnota else None,
            # 'Adres': adres.group(0) if adres else None,
            'NIP': nip.group(1) if nip else None,
            'Dotyczy': dotyczy.group(1) if dotyczy else None
        }

    # Zastosowanie funkcji do całego DataFrame
    df_info = df_wide['Dokument'].apply(extract_info).apply(pd.Series)

    # Łączenie wyników z oryginalnym DataFrame
    df_final = pd.concat([df_wide, df_info], axis=1)

    df_kontrahenci_filtered = df_kontrahenci[(df_kontrahenci["NIP"].notna()) & (df_kontrahenci["NIP"] != "")]
    df_kontrahenci_bez_nip = df_kontrahenci[df_kontrahenci["NIP"].isna() | (df_kontrahenci["NIP"] == "")]

    df_merged = pd.merge(df_final, df_kontrahenci_filtered, on="NIP", how="left")

    df_merged["Dokument_lower"] = df_merged["Dokument"].str.lower()

    # Filtrujemy tylko wiersze, gdzie "Kod" jest NaN
    mask = df_merged["Kod"].isna()

    # Dopasowanie tylko dla tych wierszy
    # Dopasowanie przy użyciu rapidfuzz

    # Funkcja dopasowująca kontrahenta i pobierająca kod
    def znajdz_kontrahenta(dokument):
        wynik = process.extractOne(dokument, df_kontrahenci["kontrahent_opis"],
                                   scorer=fuzz.token_sort_ratio, score_cutoff=60)

        if wynik:
            dopasowany_opis = wynik[0]  # Nazwa dopasowanego kontrahenta
            kod = df_kontrahenci.loc[df_kontrahenci["kontrahent_opis"] == dopasowany_opis, "Kod"].values
            _kod = kod[0] if len(kod) > 0 else None
            nazwa = df_kontrahenci.loc[df_kontrahenci["kontrahent_opis"] == dopasowany_opis, "Nazwa"].values
            _nazwa = nazwa[0] if len(nazwa) > 0 else None
            nip = df_kontrahenci.loc[df_kontrahenci["kontrahent_opis"] == dopasowany_opis, "NIP"].values
            _nip = nip[0] if len(nip) > 0 else None
            ulica = df_kontrahenci.loc[df_kontrahenci["kontrahent_opis"] == dopasowany_opis, "Ulica"].values
            _ulica = ulica[0] if len(ulica) > 0 else None
            kod_pocztowy = df_kontrahenci.loc[df_kontrahenci["kontrahent_opis"] == dopasowany_opis, "Kod pocztowy"].values
            _kod_pocztowy = kod_pocztowy[0] if len(kod_pocztowy) > 0 else None
            miasto = df_kontrahenci.loc[df_kontrahenci["kontrahent_opis"] == dopasowany_opis, "Miasto"].values
            _miasto = miasto[0] if len(miasto) > 0 else None

            return dopasowany_opis, _kod, _nazwa, _nip, _ulica, _kod_pocztowy, _miasto
        return None, None, None, None, None, None, None

    wyniki = df_merged.loc[mask, "Dokument"].apply(znajdz_kontrahenta)

    df_merged.loc[mask, "Dopasowany_kontrahent"] = [x[0] for x in wyniki]
    df_merged.loc[mask, "Kod"] = [x[1] for x in wyniki]
    df_merged.loc[mask, "Nazwa"] = [x[2] for x in wyniki]
    df_merged.loc[mask, "NIP"] = [x[3] for x in wyniki]
    df_merged.loc[mask, "Ulica"] = [x[4] for x in wyniki]
    df_merged.loc[mask, "Kod pocztowy"] = [x[5] for x in wyniki]
    df_merged.loc[mask, "Miasto"] = [x[6] for x in wyniki]

    del df_merged['Dopasowany_kontrahent']
    del df_merged['kontrahent_opis']
    del df_merged['Dokument_lower']


    # jakos znajduje dopasowanie ale jeszcze trzeba uzupelnik kolumny danych

    print(df_merged.head())

    # # Zapisanie DataFrame do pliku CSV
    # df_merged.to_csv(plik_posredni, index=False, sep=';', encoding='utf-8')  # Możesz dostosować separator i kodowanie


    # jakies dane z excela

    GRUPA = 'IMPORT'
    IK = 'SPRZEDAŻ'
    KOREKTA_DO = ''
    TYP = 2
    KOREKTA = 0
    ZAKUP = 4
    ODLICZENIA = 2
    KASA = 0
    KONTO = ''
    FIN = 64
    EXPORT = 0
    ID_O = 0
    KOD_O = 'ADMINISTROWANIE'
    OPIS = 'ADMINISTROWANIE POWIERZCHNI MIESZKALNYCH'
    ROZLICZONO = 0
    PLATNOSC = 3
    ID_FPP = 0
    NR_FPP = 0
    FLAGA_3 = 1
    USER = 'SO'

    st5 = ""
    uslugi = 0.00
    produkcja = 0.00
    zaplata = 0.00
    wartosc_z = 0.000000
    clo = 0.00
    akcyza = 0.00
    pod_imp = 0.00
    kaucja = 0.00
    netto6 = 0.00
    netto7 = 0.00
    vat6 = 0.00
    vat7 = 0.00
    x1 = 0.00
    x2 = 0.00
    x3 = 0.00
    x4 = 0.00
    x5 = 0.00
    wartosc_s = 0.00
    vat_s = 0.00




    kolumny_out = ['lp', 'GRUPA', 'data_tr', 'data_wyst', 'IK', 'dokument', 'KOREKTA_DO', 'TYP', 'KOREKTA', 'ZAKUP',
                   'ODLICZENIA', 'KASA', 'kontrahent', 'k_nazwa1', 'k_nazwa2', 'ulica', 'kod', 'miasto','nip', 'KONTO',
                   'FIN', 'EXPORT', 'ID_O', 'KOD_O', 'OPIS', 'netto0', 'netto1', 'netto2', 'netto3', 'netto4', 'kwvat2',
                   'kwvat3', 'kwvat4', 'st5', 'uslugi', 'produkcja', 'ROZLICZONO', 'PLATNOSC', 'termin', 'brutto',
                   'zaplata', 'ID_FPP', 'NR_FPP', 'wartosc_z', 'clo', 'akcyza', 'pod_imp', 'USER', 'kaucja', 'netto6',
                   'netto7', 'vat6', 'vat7', 'x1', 'x2', 'x3', 'x4', 'x5', 'wartosc_s', 'vat_s', 'flaga_1', 'stawka_1',
                   'netto_1', 'vat_1', 'flaga_2', 'stawka_2', 'netto_2', 'vat_2']

    print(f'Mamy nazwane {len(kolumny_out)} klumn.')

    for kn in kolumny_out:
        print(kn)

    pass

    # Tworzenie pustego DataFrame
    ile_wierszy = df_merged.index.size

    df_merged['data_dok'] = pd.to_datetime(df_merged['data_dok'], format=FORMAT_DATY_IN, errors='coerce')
    df_merged['data_sprz'] = pd.to_datetime(df_merged['data_sprz'], format=FORMAT_DATY_IN, errors='coerce')

    print(df_merged.dtypes)
    print('==============================\n\n')

    df_out = pd.DataFrame({
        kolumny_out[1]: pd.Series(dtype='string'),
    }, index=range(ile_wierszy))

    # przenosimy dane w odpowiednej kolejnosci
    df_out[kolumny_out[1]] = GRUPA
    df_out[kolumny_out[1]] = df_out[kolumny_out[1]].astype(str)
    df_out[kolumny_out[2]] = df_merged['data_dok'].dt.strftime(FORMAT_DATY_OUT).astype(str)
    df_out[kolumny_out[3]] = df_merged['data_sprz'].dt.strftime(FORMAT_DATY_OUT).astype(str)
    df_out[kolumny_out[4]] = IK
    df_out[kolumny_out[4]] = df_out[kolumny_out[4]].astype(str)
    df_out[kolumny_out[5]] = df_merged['nr'].astype(str)
    df_out[kolumny_out[6]] = KOREKTA_DO
    df_out[kolumny_out[6]] = df_out[kolumny_out[6]].astype(str)
    df_out[kolumny_out[7]] = TYP
    df_out[kolumny_out[7]] = df_out[kolumny_out[7]].astype(int)
    df_out[kolumny_out[8]] = KOREKTA
    df_out[kolumny_out[8]] = df_out[kolumny_out[8]].astype(int)
    df_out[kolumny_out[9]] = ZAKUP
    df_out[kolumny_out[9]] = df_out[kolumny_out[9]].astype(int)
    df_out[kolumny_out[10]] = ODLICZENIA
    df_out[kolumny_out[10]] = df_out[kolumny_out[10]].astype(int)
    df_out[kolumny_out[11]] = KASA
    df_out[kolumny_out[11]] = df_out[kolumny_out[10]].astype(int)
    df_out[kolumny_out[12]] = df_merged['Kod'].astype(str)
    df_out[kolumny_out[13]] = df_merged['Nazwa'].astype(str)
    df_out[kolumny_out[14]] = ''
    df_out[kolumny_out[14]] = df_out[kolumny_out[14]].astype(str)
    df_out[kolumny_out[15]] = df_merged['Ulica'].astype(str)
    df_out[kolumny_out[16]] = df_merged['Kod pocztowy'].astype(str)
    df_out[kolumny_out[17]] = df_merged['Miasto'].astype(str)
    df_out[kolumny_out[18]] = df_merged['NIP'].astype(str)
    df_out[kolumny_out[19]] = KONTO
    df_out[kolumny_out[19]] = df_out[kolumny_out[19]].astype(str)

    df_out[kolumny_out[20]] = FIN
    df_out[kolumny_out[20]] = df_out[kolumny_out[20]].astype(int)

    df_out[kolumny_out[21]] = EXPORT
    df_out[kolumny_out[21]] = df_out[kolumny_out[21]].astype(int)

    df_out[kolumny_out[22]] = ID_O
    df_out[kolumny_out[22]] = df_out[kolumny_out[22]].astype(int)

    df_out[kolumny_out[23]] = KOD_O
    df_out[kolumny_out[23]] = df_out[kolumny_out[23]].astype(str)

    df_out[kolumny_out[24]] = OPIS
    df_out[kolumny_out[24]] = df_out[kolumny_out[24]].astype(str)

    # 'netto0'
    df_out[kolumny_out[25]] = df_merged['netto zw.'].round(2).astype(float)

    # 'netto1'
    df_out[kolumny_out[26]] = df_merged['netto 0%'].round(2).astype(float)

    # 'netto2'
    df_out[kolumny_out[27]] = df_merged['netto 8%'].round(2).astype(float)
    # df_out[kolumny_out[27]] = 0.00
    # df_out[kolumny_out[27]] = df_out[kolumny_out[27]].round(2).astype(float)

    # 'netto3'
    df_out[kolumny_out[28]] = df_merged['netto 23%'].round(2).astype(float)
    # df_out[kolumny_out[28]] = 0.00
    # df_out[kolumny_out[28]] = df_out[kolumny_out[28]].round(2).astype(float)

    # 'netto4'
    df_out[kolumny_out[29]] = 0.00
    df_out[kolumny_out[29]] = df_out[kolumny_out[29]].round(2).astype(float)

    # 'kwvat2'
    df_out[kolumny_out[30]] = df_merged['podatek_vat 8%'].round(2).astype(float)
    # df_out[kolumny_out[30]] = 0.00
    # df_out[kolumny_out[30]] = df_out[kolumny_out[30]].round(2).astype(float)

    # 'kwvat3'
    df_out[kolumny_out[31]] = df_merged['podatek_vat 23%'].round(2).astype(float)
    # df_out[kolumny_out[31]] = 0.00
    # df_out[kolumny_out[31]] = df_out[kolumny_out[31]].round(2).astype(float)

    # 'kwvat4'
    df_out[kolumny_out[32]] = 0.00
    df_out[kolumny_out[32]] = df_out[kolumny_out[32]].astype(float)

    # 'st5'
    df_out[kolumny_out[33]] = st5
    df_out[kolumny_out[33]] = df_out[kolumny_out[33]].astype(str)

    # 'uslugi'
    df_out[kolumny_out[34]] = uslugi
    df_out[kolumny_out[34]] = df_out[kolumny_out[34]].astype(float)

    # 'produkcja'
    df_out[kolumny_out[35]] = produkcja
    df_out[kolumny_out[35]] = df_out[kolumny_out[35]].astype(float)

    # 'ROZLICZONO'
    df_out[kolumny_out[36]] = ROZLICZONO
    df_out[kolumny_out[36]] = df_out[kolumny_out[36]].astype(int)

    # 'PLATNOSC'
    df_out[kolumny_out[37]] = PLATNOSC
    df_out[kolumny_out[37]] = df_out[kolumny_out[37]].astype(int)

    # 'termin'
    df_out[kolumny_out[38]] = df_out[kolumny_out[2]]

    # 'brutto'
    df_out[kolumny_out[39]] = df_merged['war_brutto'].str.replace(',', '.').astype(float)

    # 'zaplata'
    df_out[kolumny_out[40]] = zaplata
    df_out[kolumny_out[40]] = df_out[kolumny_out[40]].astype(float)

    # 'ID_FPP'
    df_out[kolumny_out[41]] = ID_FPP
    df_out[kolumny_out[41]] = df_out[kolumny_out[41]].astype(int)

    # 'NR_FPP'
    df_out[kolumny_out[42]] = NR_FPP
    df_out[kolumny_out[42]] = df_out[kolumny_out[42]].astype(int)

    # 'wartosc_z'
    df_out[kolumny_out[43]] = wartosc_z
    df_out[kolumny_out[43]] = df_out[kolumny_out[43]].astype(float)

    # 'clo'
    df_out[kolumny_out[44]] = clo
    df_out[kolumny_out[44]] = df_out[kolumny_out[44]].astype(float)

    # 'akcyza'
    df_out[kolumny_out[45]] = akcyza
    df_out[kolumny_out[45]] = df_out[kolumny_out[45]].astype(float)

    # 'pod_imp'
    df_out[kolumny_out[46]] = pod_imp
    df_out[kolumny_out[46]] = df_out[kolumny_out[46]].astype(float)

    # 'USER'
    df_out[kolumny_out[47]] = USER
    df_out[kolumny_out[47]] = df_out[kolumny_out[47]].astype(str)

    # 'kaucja'
    df_out[kolumny_out[48]] = kaucja
    df_out[kolumny_out[48]] = df_out[kolumny_out[48]].astype(float)

    # 'netto6',
    df_out[kolumny_out[49]] = netto6
    df_out[kolumny_out[49]] = df_out[kolumny_out[49]].astype(float)

    # 'netto7'
    df_out[kolumny_out[50]] = netto7
    df_out[kolumny_out[50]] = df_out[kolumny_out[50]].astype(float)

    # 'vat6'
    df_out[kolumny_out[51]] = vat6
    df_out[kolumny_out[51]] = df_out[kolumny_out[51]].astype(float)

    # 'vat7'
    df_out[kolumny_out[52]] = vat7
    df_out[kolumny_out[52]] = df_out[kolumny_out[52]].astype(float)

    # 'x1'
    df_out[kolumny_out[53]] = x1
    df_out[kolumny_out[53]] = df_out[kolumny_out[53]].astype(float)

    # 'x2'
    df_out[kolumny_out[54]] = x2
    df_out[kolumny_out[54]] = df_out[kolumny_out[54]].astype(float)

    # 'x3'
    df_out[kolumny_out[55]] = x3
    df_out[kolumny_out[55]] = df_out[kolumny_out[55]].astype(float)

    # 'x4'
    df_out[kolumny_out[56]] = x4
    df_out[kolumny_out[56]] = df_out[kolumny_out[56]].astype(float)

    # 'x5'
    df_out[kolumny_out[57]] = x5
    df_out[kolumny_out[57]] = df_out[kolumny_out[57]].astype(float)

    # 'wartosc_s'
    df_out[kolumny_out[58]] = wartosc_s
    df_out[kolumny_out[58]] = df_out[kolumny_out[58]].astype(float)

    # 'vat_s'
    df_out[kolumny_out[59]] = vat_s
    df_out[kolumny_out[59]] = df_out[kolumny_out[59]].astype(float)

    # TODO: przeanalizowac stawki i kwoty wat i uzupenic dane
    FLAGA_VAT_XX = -1
    FLAGA_VAT_ZW = 1
    FLAGA_VAT_00 = 0
    FLAGA_VAT_03 = 0
    FLAGA_VAT_05 = 0
    FLAGA_VAT_08 = 0
    FLAGA_VAT_23 = 0
    FLAGA_VAT_NP = 4
    TYP_VAT_ZW = 0
    TYP_VAT_00 = 1
    TYP_VAT_08 = 2
    TYP_VAT_23 = 3

    def analiza_stawek_vat(n0, n1, n2, n3, n4, kv2, kv3, kv4):
        """

        :param n0: netto vat zw  'netto zw.'
        :param n1: netto vat 0%  'netto 0%'
        :param n2: netto vat 8%  'netto 8%'
        :param n3: netto vat 23% 'netto 23%'
        :param n4:
        :param kv2: kwota vat 8%
        :param kv3: kwota vat 23%
        :param kv4:
        :return:
        """
        vat_type_list = []
        netto_all_list = [n0, n1, n2, n3, n4]
        kwvat_all_list = [0.0, 0.0, kv2, kv3, kv4]
        netto_list = []
        kwvat_list = []
        try:
            for index, element in enumerate(netto_all_list):
                if element is not None and pd.notna(element) and element != 0.0:
                    vat_type_list.append(index)
                    netto_list.append(element)
                    kwvat_list.append(kwvat_all_list[index])

            ile_stawek_vat = len(vat_type_list)

            # vatTyp = [2, 3]   # Typy VAT
            # netto = [100, 200]  # Wartości netto
            # kwvat = [8, 46]     # Kwoty VAT
            # xvat = 2           # Ilość VAT

            # TODO: Wymaga poprawy tak by obslugiwac wszystkie typy vat,
            #  obsluge oproscic do trzech przypadkow: ZW, NP i stawka
            def przetworz_vat(vatTyp, netto, kwvat, xvat):
                """
                    Wybiera stawki wat
                :param vatTyp: Lista typów watu zw, 0%, 8$, 23%
                :param netto:  Lista wartości netto
                :param kwvat:  Lista wartość vat
                :param xvat:   Ilość stawek wat
                :return: uzyte stawki wat i ich kwoty
                """
                if not vatTyp or not netto or not kwvat:
                    raise ValueError("Jedna z list VAT jest pusta")
                if xvat == 0:
                    return 0, 0.00, 0.00, 0.00, 0, 0.00, 0.00, 0.00
                elif xvat > 0 and all(xvat == len(lst) for lst in [vatTyp, netto, kwvat]):
                    # Inicjalizacja zmiennych dla pierwszego VAT
                    try:
                        if vatTyp[0] == TYP_VAT_ZW:
                            # zwolnione
                            flaga_1 = FLAGA_VAT_ZW
                            stawka_1 = 0.00
                        elif vatTyp[0] == TYP_VAT_00:
                            # stawka 0%
                            flaga_1 = FLAGA_VAT_00
                            stawka_1 = 0.00
                        elif vatTyp[0] == TYP_VAT_08:
                            # stawka 8%
                            flaga_1 = FLAGA_VAT_08
                            stawka_1 = 8.00
                        elif vatTyp[0] == TYP_VAT_23:
                            # stawka 23%
                            flaga_1 = FLAGA_VAT_23
                            stawka_1 = 23.00
                        else:
                            flaga_1 = 0
                            stawka_1 = 0.00

                        netto_1 = netto[0]
                        vat_1 = kwvat[0]

                        # Inicjalizacja zmiennych dla drugiego VAT
                        flaga_2 = None
                        stawka_2 = None
                        netto_2 = None
                        vat_2 = None

                        if xvat > 1:
                            if vatTyp[1] == TYP_VAT_ZW:
                                # zwolnione
                                flaga_2 = FLAGA_VAT_ZW
                                stawka_2 = 0.00
                            elif vatTyp[1] == TYP_VAT_00:
                                # stawka 0%
                                flaga_2 = FLAGA_VAT_00
                                stawka_2 = 0.00
                            elif vatTyp[1] == TYP_VAT_08:
                                # stawka 8%
                                flaga_2 = FLAGA_VAT_08
                                stawka_2 = 8.00
                            elif vatTyp[1] == TYP_VAT_23:
                                # stawka 23%
                                flaga_2 = FLAGA_VAT_23
                                stawka_2 = 23.00
                            else:
                                flaga_2 = 0
                                stawka_2 = 0.00

                            netto_2 = netto[1]
                            vat_2 = kwvat[1]

                    except Exception as e:
                        print(e)
                        raise e

                else:
                    print(f'{vatTyp}, {netto}, {kwvat}, {xvat}')
                    raise ValueError("Lista vatTyp jest pusta, lub niezgodna ilosc elementow")

                # 'flaga_1', 'stawka_1', 'netto_1', 'vat_1', 'flaga_2', 'stawka_2', 'netto_2', 'vat_2'
                print(f'{flaga_1}, {stawka_1}, {netto_1}, {vat_1}, {flaga_2}, {stawka_2}, {netto_2}, {vat_2}')
                return flaga_1, stawka_1, netto_1, vat_1, flaga_2, stawka_2, netto_2, vat_2

            flaga_1, stawka_1, netto_1, vat_1, flaga_2, stawka_2, netto_2, vat_2 = przetworz_vat(vat_type_list, netto_list, kwvat_list, ile_stawek_vat)
        except Exception as e:
            print(e)
            return 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00

        print(f'{flaga_1}, {stawka_1}, {netto_1}, {vat_1}, {flaga_2}, {stawka_2}, {netto_2}, {vat_2}')
        return flaga_1, stawka_1, netto_1, vat_1, flaga_2, stawka_2, netto_2, vat_2


    print(df_out.columns)

    badane_kolumny = ['netto0', 'netto1', 'netto2', 'netto3', 'netto4', 'kwvat2', 'kwvat3', 'kwvat4']
    badane_kolumny_plus = badane_kolumny + ['flaga_1', 'stawka_1', 'netto_1', 'vat_1', 'flaga_2', 'stawka_2', 'netto_2', 'vat_2']

    # wybrane_kolumny = df_out[badane_kolumny].copy()

    df_out['temp_vat'] = df_out.apply(
        lambda row: analiza_stawek_vat(row['netto0'], row['netto1'], row['netto2'], row['netto3'], row['netto4'],
                                       row['kwvat2'], row['kwvat3'], row['kwvat4']),
        axis=1
    )
    print(df_out['temp_vat'].apply(len).value_counts())  # Powinno zwrócić tylko wartość 8

    print(df_out.shape[0])

    print(df_out.columns.intersection(['flaga_1', 'stawka_1', 'netto_1', 'vat_1', 'flaga_2', 'stawka_2', 'netto_2', 'vat_2']))

    print("Liczba wierszy w wybrane_kolumny:", df_out.shape[0])
    print("Liczba wartości zwróconych przez analiza_stawek_vat:", df_out['temp_vat'].apply(len).shape[0])

    print('Czy wszystkie listy mają długość 8?')
    print(df_out['temp_vat'].apply(lambda x: len(x)).value_counts())  # Czy wszystkie listy mają długość 8?
    print('Jakiego typu są wartości?')
    print(df_out['temp_vat'].apply(lambda x: type(x)).value_counts())  # Jakiego typu są wartości?
    print('Podgląd pierwszych 10 wartości')
    print(df_out['temp_vat'].head(10))  # Podgląd pierwszych 10 wartości
    print('----------------------------------------------------------')
    # Tworzymy nowe kolumny z wartości krotek (temp_vat)
    df_out[['flaga_1', 'stawka_1', 'netto_1', 'vat_1', 'flaga_2', 'stawka_2', 'netto_2', 'vat_2']] = pd.DataFrame(df_out['temp_vat'].tolist(), index=df_out.index)

    # Sprawdzenie wyników
    print(df_out[['flaga_1', 'stawka_1', 'netto_1', 'vat_1', 'flaga_2', 'stawka_2', 'netto_2', 'vat_2']].head())

    del df_out['temp_vat']

    # ======================================
    # distosowanie formatu zapisywanych fanych

    # Zmieniamy kolumny tekstowe na stringi, jeśli nie są
    for col in df_out.select_dtypes(include='object').columns:
        df_out[col] = df_out[col].astype(str)


    # # Stosujemy funkcję do każdego wiersza i rozwijamy wyniki na nowe kolumny
    # df_out[['flaga_1', 'stawka_1', 'netto_1', 'vat_1', 'flaga_2', 'stawka_2', 'netto_2', 'vat_2']] = df_out.apply(
    #     lambda row: analiza_stawek_vat(row['netto0'], row['netto1'], row['netto2'], row['netto3'], row['netto4'],
    #                                    row['kwvat2'], row['kwvat3'], row['kwvat4']),
    #     axis=1
    # )

    # Wyświetlenie listy kolumn i ich typów
    print(df_out.dtypes)
    pass

    # df_out.to_csv('testujemy_wyniki.txt', quoting=csv.QUOTE_NONNUMERIC, sep=',', index=True, header=True)
    # print("Plik wynikowy CSV zapisany jako testujemy_wyniki.txt")

    # na koniec sortujemy po numerze dokumentu
    # Tworzenie nowej kolumny z liczbą po ostatnim "/"
    # df_out['Numer'] = df_out['dokument'].str.extract(r'/(\d+)$')
    df_out[['Reszta', 'Numer']] = df_out['dokument'].str.extract(r'(.*/)?(\d+)$')

    # Konwersja na int, ignorując błędy (puste wartości pozostaną jako NaN)
    df_out['Numer'] = pd.to_numeric(df_out['Numer'], errors='coerce').astype(int)

    # Sortowanie
    df_out = df_out.sort_values(by=['Reszta', 'Numer'], ascending=[True, True])

    # Resetowanie indeksu (usuwa stary indeks i dodaje nowy od 0)
    df_out = df_out.reset_index(drop=True)

    # Usunięcie kolumny 'Numer'
    df_out.drop(columns=['Reszta', 'Numer'], inplace=True)

    # dodaje znaki cudzysłowu do wybranych kolumn
    print(df_out.dtypes)

    # df_out['last'] = "GTU_12"

    kolumny_w_cudzyslow = ['GRUPA', 'data_tr', 'data_wyst', 'IK', 'dokument', 'KOREKTA_DO', 'kontrahent', 'k_nazwa1',
                           'k_nazwa2', 'ulica', 'kod', 'miasto', 'nip', 'KOD_O', 'OPIS', 'st5']
    df_out[kolumny_w_cudzyslow] = df_out[kolumny_w_cudzyslow].astype(str).apply(lambda x: "'" + x + "'")

    # df_out['flaga_1'] = pd.to_numeric(df['flaga_1'], errors='coerce').astype('Int64')
    # df_out['flaga_2'] = pd.to_numeric(df['flaga_2'], errors='coerce').astype('Int64')
    df_out['flaga_1'] = df_out['flaga_1'].astype("Int64")
    df_out['flaga_2'] = df_out['flaga_2'].astype("Int64")
    pass

    # zerowanie wartosci
    df_out[kolumny_out[25]] = 0.0
    df_out[kolumny_out[26]] = 0.0
    df_out[kolumny_out[27]] = 0.0
    df_out[kolumny_out[28]] = 0.0
    df_out[kolumny_out[30]] = 0.0
    df_out[kolumny_out[31]] = 0.0


    # df_out.to_csv(plik_koncowy, quoting=csv.QUOTE_NONNUMERIC, sep=',', index=True, header=False, na_rep="")
    temp_dir = Path('data/temp')
    temp_dir.mkdir(parents=True, exist_ok=True)  # stworzy folder jeśli nie istnieje
    temp_file = temp_dir / 'temp_csv_optima.txt'

    df_out.to_csv(temp_file, sep=',', index=True, header=False, na_rep="",
                  encoding=ENCODING)

    # zmiana znakow
    with open(temp_file, "r", encoding=ENCODING) as f:
        data = f.read()

    # print(repr(data[:500]))  # Podgląd pierwszych 500 znaków, w tym \n

    data = data.replace(",'',", ',"",')
    data = data.replace("','", '","')
    data = data.replace("',", '",')
    data = data.replace(",'", ',"')
    data = data.replace("'\n", '"\n')

    with open(plik_koncowy, "w", encoding=ENCODING, newline='') as f:
        f.write(data)

    # print(repr(data[:500]))  # Podgląd pierwszych 500 znaków, w tym \n

    print(f"Plik wynikowy CSV zapisany jako {plik_koncowy}")
    return str(plik_koncowy)

if __name__ == "__main__":
    # Ścieżka do pliku CSV
    plik_csv = Path('/Users/krzysztof/PycharmProjects/Optima_SOTAX/DaneMarka/2025.02 - sprzedaż MARKA JDG z kontrahentami.csv')

    # plik_posredni = 'DaneMarka/2025_01-MARKA_JDG_sprzedaż_z_kontrahentami_tmp.csv'
    # plik_posredni = Path('DaneMarka/2025_01-MARKA_JDG_sprzedaż_z_kontrahentami_tmp.csv')

    # TODO: dodać podpinanie plikow z kontrachentami w excel:cd /us
    plik_kontrahenci = Path('/Users/krzysztof/PycharmProjects/Optima_SOTAX/DaneMarka/kontrahenci_Marka_JDG_20250218.csv')

    plik_koncowy = Path('/Users/krzysztof/PycharmProjects/Optima_SOTAX/DaneMarka/2025_02-MARKA_JDG_do_Optima_utf-8-sig.txt')

    analiza_zestawienia_faktur(plik_csv, plik_kontrahenci, plik_koncowy)


