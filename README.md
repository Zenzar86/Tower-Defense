# Tower Defense Hra

Jednoduchá Tower Defense hra vytvořená v Pythonu a Pygame.

## Funkce

*   Více typů věží s vylepšeními.
*   Různé typy nepřátel s odlišnými statistikami.
*   Více map/misí.
*   Zvukové efekty a hudba na pozadí.
*   Základní prvky uživatelského rozhraní (menu, tlačítka, zobrazení zdraví/měny).
*   Podpora lokalizace (Angličtina/Čeština).

## Požadavky

*   Python 3.x
*   Pygame (`pip install pygame`)
*   PyInstaller (`pip install pyinstaller`) - pro vytvoření spustitelného souboru

## Vytvoření spustitelného souboru

Pro vytvoření samostatného spustitelného souboru (`Tower Defense.exe`) spusťte následující příkaz z kořenového adresáře projektu (`Semestrálka`):

```bash
pyinstaller --onefile --windowed --add-data "Data;." --name "Tower Defense" --icon "Data/Icon/TowerDefenseIcon.ico" Data/main.py
```

Tento příkaz vytvoří spustitelný soubor ve složce `dist`.

## Spuštění hry

1.  **Ze zdrojového kódu:**
    Přejděte do složky `Data` ve vašem terminálu a spusťte:
    ```bash
    python main.py
    ```
2.  **Spustitelný soubor:**
    Spusťte soubor `Tower Defense.exe` nacházející se ve složce `dist` po vytvoření.

## Struktura projektu

*   `Data/`: Obsahuje všechny herní assety (obrázky, zvuky, fonty) a zdrojový kód v Pythonu (`.py` soubory).
*   `dist/`: Obsahuje vytvořený spustitelný soubor (`Tower Defense.exe`).
*   `.gitignore`: Specifikuje soubory, které má Git ignorovat.
*   `README.md`: Tento soubor.