# ✅ Plan testów — Konwersja raportów do ERP Optima BR

## Cel testów
Zweryfikowanie poprawności działania konwertera plików CSV ➔ TXT zgodnych z formatem ERP Optima.

---

## Zakres testów

### 1. Testy parsera plików sprzedaży (`sprzedaz.csv`)
- [x] Wczytywanie pełnej listy faktur (91 pozycji)
- [x] Prawidłowy odczyt numeru faktury
- [x] Prawidłowy odczyt daty wystawienia i daty sprzedaży
- [x] Prawidłowy odczyt kwot brutto i netto
- [x] Wykrywanie i przypisanie stawki VAT
- [x] Obsługa wielu stawek VAT dla jednej faktury
- [x] Obsługa faktur zwolnionych (VAT = 0%)

### 2. Testy integracji kontrahentów (`listaFirm.csv`)
- [x] Poprawne dopasowanie kontrahenta po NIP
- [x] Obsługa błędnych lub brakujących NIP
- [x] Obsługa nietypowych nazw kontrahentów (np. cudzysłowy, przecinki)

### 3. Testy walidacji danych
- [x] Suma VAT z pozycji faktury = VAT z faktury (do 0.01 PLN różnicy)
- [x] Brak faktur z pustym numerem (numer_faktury != None)
- [x] Każda faktura zawiera minimum jedną pozycję VAT (`stawki_vat` niepusta)

### 4. Testy zapisu pliku wyjściowego (`TXT`)
- [x] Formatowanie zgodne z ERP Optima: kolumny, separatory, kodowanie
- [x] Zapis wszystkich wczytanych faktur
- [x] Obsługa znaków specjalnych w nazwach kontrahentów

---

## Narzędzia testowe
- `unittest` (moduł wbudowany w Pythona)
- `pytest` (opcjonalnie w przyszłości)
- Ręczna weryfikacja plików TXT przez import do środowiska testowego ERP Optima

---

## Planowana automatyzacja testów
- [ ] Automatyczne generowanie raportu testów HTML
- [ ] Testy regresji przy każdej większej aktualizacji kodu
- [ ] Testy wsadowe dla wielu plików wejściowych naraz

---

> **Ostatnia aktualizacja:** kwiecień 2025
>  
> **Osoba odpowiedzialna:** Krzysztof Olejnik  
>  
> **Repozytorium:** `konwersja-erp-optima`