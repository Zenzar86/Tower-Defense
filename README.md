# Tower Defense Hra

Jednoduchá Tower Defense hra vytvořená v Pythonu pomocí knihovny Pygame.

## Popis

Cílem hry je zabránit nepřátelům v dosažení konce cesty stavěním obranných věží podél ní. Hra obsahuje různé typy věží a nepřátel s odlišnými schopnostmi.

## Spuštění hry

Pro spuštění hry spusťte soubor `Tower Defense.exe`, který se nachází ve složce `dist`.

## Struktura projektu

*   **Data/**: Obsahuje všechny herní assety (obrázky, zvuky) a zdrojové kódy (`.py` soubory).
*   **dist/**: Obsahuje spustitelný soubor hry (`Tower Defense.exe`).
*   **.gitignore**: Specifikuje soubory a složky, které mají být ignorovány Gitem.
*   **README.md**: Tento soubor.
*   **Tower Defense.spec**: Konfigurační soubor pro PyInstaller (použitý k vytvoření `.exe`).

## Požadavky

Hra byla vytvořena a zkompilována pomocí Pythonu a Pygame. Pro spuštění `.exe` souboru nejsou potřeba žádné další závislosti. Pokud byste chtěli spustit hru ze zdrojových kódů, budete potřebovat nainstalovat Python a Pygame.

```bash
pip install pygame
```

## Jak hrát

1.  Spusťte `Tower Defense.exe`.
2.  Vyberte si mapu a obtížnost.
3.  Stavějte věže na vyznačených platformách kliknutím na platformu a výběrem věže z menu.
4.  Spusťte vlnu nepřátel.
5.  Vylepšujte nebo prodávejte věže podle potřeby.
6.  Braňte své území!
