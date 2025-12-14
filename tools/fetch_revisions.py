import re
import httpx

REGEX = r"https:\/\/www\.gstatic\.com\/android\/keyboard\/emojikitchen\/.*\.png"


def extraer_fechas_emojikitchen(texto: str) -> set[str]:
    patron = re.compile(
        r'https://www\.gstatic\.com/android/keyboard/emojikitchen/(\d{8})/',
        re.IGNORECASE
    )
    return set(patron.findall(texto))


def main():
    r = httpx.get("https://emojikitchen.dev/assets/index-DzBkVMOd.js")
    r.raise_for_status()
    results = extraer_fechas_emojikitchen(r.text)
    results = sorted(results)
    for result in results:
        print(f"      - {result}")


if __name__ == '__main__':
    main()
