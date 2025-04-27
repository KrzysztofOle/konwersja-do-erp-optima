# === optima_formatter.py ===
import pandas as pd

class OptimaFormatter:
    @staticmethod
    def format_full(df: pd.DataFrame) -> str:
        """
        Tworzy pełny eksport danych zgodnie ze wzorcem ERP Optima,
        dynamicznie uwzględniając stawki VAT.
        """
        formatted_lines = []
        counter = 0

        for _, row in df.iterrows():
            numer_faktury = row.get('numer_faktury', '')
            nazwa_kontrahenta = row.get('nazwa_kontrahenta', '')
            kod_kontrahenta = ""
            nip = row.get('nip', '')
            ulica = ""
            kod_pocztowy = ""
            miasto = ""
            data_wystawienia = row.get('data_wystawienia')
            data_sprzedazy = row.get('data_sprzedazy')
            wartosc_netto = row.get('wartosc_netto', 0.0)
            wartosc_brutto = row.get('wartosc_brutto', 0.0)

            # Dane VAT
            netto0 = row.get('netto0', 0.0)
            netto1 = row.get('netto1', 0.0)
            netto2 = row.get('netto2', 0.0)
            netto3 = row.get('netto3', 0.0)
            netto4 = row.get('netto4', 0.0)
            kwvat2 = row.get('kwvat2', 0.0)
            kwvat3 = row.get('kwvat3', 0.0)
            kwvat4 = row.get('kwvat4', 0.0)

            sekcja_vat = OptimaFormatter.analiza_stawek_vat(
                netto0, netto1, netto2, netto3, netto4,
                kwvat2, kwvat3, kwvat4
            )

            # Stała część eksportu
            line = [
                counter,  # 0 lp
                "IMPORT",  # 1 GRUPA
                data_wystawienia.strftime('%y/%m/%d') if pd.notna(data_wystawienia) else '',  # 2 data wystawienia
                data_sprzedazy.strftime('%y/%m/%d') if pd.notna(data_sprzedazy) else '',  # 3 data sprzedaży
                "SPRZEDAŻ",  # 4 IK
                numer_faktury,  # 5 dokument
                "",  # 6 korekta do
                2, 0, 4, 2, 2,  # 7-11 TYP, KOREKTA, ZAKUP, ODLICZENIA, KASA
                kod_kontrahenta,  # 12 kontrahent
                nazwa_kontrahenta,  # 13 k_nazwa1
                "",  # 14 k_nazwa2
                ulica,  # 15 ulica
                kod_pocztowy,  # 16 kod
                miasto,  # 17 miasto
                nip,  # 18 nip
                "",  # 19 konto
                64,  # 20 FIN
                0, 0,  # 21-22 EXPORT, ID_O
                "ADMINISTROWANIE",  # 23 opis
                "ADMINISTROWANIE POWIERZCHNI MIESZKALNYCH",  # 24 usługi
                0.0, 0.0, 0.0, 0.0,  # 25-28 netto0, netto1, netto2, netto3
                0.0, 0.0, 0.0, 0.0,  # 29-32 netto4, kwvat2, kwvat3, kwvat4
                "",  # 33 st5
                0.0, 0.0,  # 34-35 usługi, produkcja
                0, 3,  # 36-37 rozliczono, płatność
                data_sprzedazy.strftime('%y/%m/%d') if pd.notna(data_sprzedazy) else '',  # 38 termin płatności
                wartosc_brutto,  # 39 brutto
                0.0,  # 40 zaplata
                0, 0,  # 41-42 ID_FPP, NR_FPP
                0.0, 0.0, 0.0, 0.0,  # 43-46 wartosc_z, clo, akcyza, pod_imp
                "SO",  # 47 USER
                0.0, 0.0, 0.0, 0.0,  # 48-51 kaucja netto6
                0.0, 0.0, 0.0, 0.0,  # 52-55 vat6, vat7
                0.0, 0.0, 0.0, 0.0,  # 56-59 x1, x2
            ]

            # 🔥 Dopełnij do 64 kolumn
            while len(line) < 64:
                line.append("")

            # Dynamiczne sekcje VAT
            for flaga, stawka, netto, vat in sekcja_vat:
                line.append(flaga)
                line.append(stawka)
                line.append(netto)
                line.append(vat)

            # Dopełnij do min. 67 kolumn
            while len(line) < 67:
                line.append("")

            # Formatowanie pól
            def format_field(x):
                if isinstance(x, float):
                    return f"{x:.2f}"
                if isinstance(x, int):
                    return str(x)
                if isinstance(x, str) and x.strip() != "":
                    return f'"{x}"'
                return ""

            formatted_line = ",".join(format_field(item) for item in line)
            formatted_lines.append(formatted_line)

            counter += 1

        return "\n".join(formatted_lines)

    @staticmethod
    def analiza_stawek_vat(n0, n1, n2, n3, n4, kv2, kv3, kv4):
        """
        Analizuje stawki VAT i zwraca sekcję VAT do pliku wynikowego.
        """
        # Typy VAT
        TYP_VAT_ZW = 0
        TYP_VAT_00 = 1
        TYP_VAT_08 = 2
        TYP_VAT_23 = 3

        # Flagi VAT
        FLAGA_VAT_ZW = 1
        FLAGA_VAT_00 = 0
        FLAGA_VAT_08 = 0
        FLAGA_VAT_23 = 0

        vat_type_list = []
        netto_all_list = [n0, n1, n2, n3, n4]
        kwvat_all_list = [0.0, 0.0, kv2, kv3, kv4]
        netto_list = []
        kwvat_list = []

        for idx, netto in enumerate(netto_all_list):
            if netto is not None and pd.notna(netto) and netto != 0.0:
                vat_type_list.append(idx)
                netto_list.append(netto)
                kwvat_list.append(kwvat_all_list[idx])

        wyniki = []

        for vat_typ, netto, vat in zip(vat_type_list, netto_list, kwvat_list):
            if vat_typ == TYP_VAT_ZW:
                flaga = FLAGA_VAT_ZW
                stawka = 0.00
            elif vat_typ == TYP_VAT_00:
                flaga = FLAGA_VAT_00
                stawka = 0.00
            elif vat_typ == TYP_VAT_08:
                flaga = FLAGA_VAT_08
                stawka = 8.00
            elif vat_typ == TYP_VAT_23:
                flaga = FLAGA_VAT_23
                stawka = 23.00
            else:
                flaga = 0
                stawka = 0.00

            wyniki.append((flaga, stawka, netto, vat))

        if not wyniki:
            wyniki = [(0, 0.00, 0.00, 0.00)]

        return wyniki
