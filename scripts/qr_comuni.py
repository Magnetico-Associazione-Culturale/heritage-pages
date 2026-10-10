#!/usr/bin/env python3
"""
QR dei comuni: uno per comune, da stampare su cartelli, brochure e adesivi. Punta alla
landing del comune, https://heritage.magnetico.cloud/<Nome>/:
  - senza l'app si apre la landing, con i pulsanti degli store;
  - con l'app installata il telefono apre direttamente l'app su quel comune (universal link
    su iOS, App Link su Android: file in .well-known/).

Per ogni comune pubblicato nel catalogo dell'app, con la landing già presente (cartella
<Nome>/), crea qr/<Nome>.svg (vettoriale, per la stampa) e qr/<Nome>.png (1200 px).

Uso (nella radice del repo):
  pip install "qrcode[pil]"
  python3 scripts/qr_comuni.py              # comuni "published"
  python3 scripts/qr_comuni.py --preview    # anche quelli in "preview"

L'URL della landing non cambia: rigenerare i QR non rende inutili quelli già stampati.
"""
import json
import os
import sys
import urllib.request

CATALOG_URL = "https://contenuti.magnetico.cloud/catalog.json"
SITE = "https://heritage.magnetico.cloud"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_catalog():
    # Senza User-Agent la protezione bot di Cloudflare risponde 403.
    request = urllib.request.Request(CATALOG_URL, headers={"User-Agent": "heritage-pages-qr/1.0"})
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.load(response)


def write_qr(url, name):
    import qrcode
    import qrcode.image.svg

    os.makedirs(os.path.join(ROOT, "qr"), exist_ok=True)
    svg = qrcode.make(url, image_factory=qrcode.image.svg.SvgPathImage, border=4)
    with open(os.path.join(ROOT, "qr", f"{name}.svg"), "wb") as f:
        svg.save(f)
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, border=4, box_size=40)
    qr.add_data(url)
    qr.make(fit=True)
    image = qr.make_image(fill_color="black", back_color="white").resize((1200, 1200))
    image.save(os.path.join(ROOT, "qr", f"{name}.png"))


def main():
    try:
        import qrcode  # noqa: F401
    except ImportError:
        sys.exit('Manca il pacchetto qrcode: pip install "qrcode[pil]"')
    include_preview = "--preview" in sys.argv
    for comune in load_catalog().get("comuni", []):
        status = comune.get("status")
        if status != "published" and not (include_preview and status == "preview"):
            continue
        name = comune["name"].strip()
        if not os.path.isfile(os.path.join(ROOT, name, "index.html")):
            print(f"- {name}: saltato, manca la landing {name}/index.html")
            continue
        url = f"{SITE}/{name}/"
        write_qr(url, name)
        print(f"- {name}: {url} → qr/{name}.svg, qr/{name}.png")


if __name__ == "__main__":
    main()
