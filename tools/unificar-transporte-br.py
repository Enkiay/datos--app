"""UNIFICAR LOS TRES ÍTEMS DE TRANSPORTE DE BRASIL (28-sep-2026). Oscar: «los tres de transporte unifícalos en uno solo».

Con la fase B (SINAPI) estos tres ítems quedaron con la MISMA receta y el mismo costo (SINAPI 100981 + 97914×5:
carga mecanizada + transporte en camión basculante, DMT 5 km):
    OT015BR Transporte de Material Excedente
    OT027BR Retirada e Transporte de Entulho com Carga
    OT038BR Limpeza e Retirada de Entulho
Queda UNO: OT015BR, con un nombre que cubre los tres. OT027BR y OT038BR salen del catálogo de Brasil.

  · Sólo `catalogo/v1.0/items_BR.json` y la versión `catalogo_BR` del manifest. Precios, mapa y demás países: nada.
  · Quien ya tiene OT027BR / OT038BR en su biblioteca los CONSERVA (el catálogo no borra ítems del usuario);
    simplemente dejan de ofrecerse.
  · Ninguno tiene tipo BIM ni figura en los IFC de ejemplo.
  · ⚠ Desde acá BR (373) y BO (375) ya NO se corresponden por posición: `tools/ajuste-rendimientos-br.py` (que
    emparejaba por posición) no se puede volver a correr tal cual.

Uso:  python tools/unificar-transporte-br.py            → muestra qué haría
      python tools/unificar-transporte-br.py --aplicar  → escribe
"""
import io
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
F_BR = RAIZ / "catalogo/v1.0/items_BR.json"
F_MAN = RAIZ / "manifest.json"
QUEDA = "OT015BR"
SALEN = ("OT027BR", "OT038BR")
NOMBRE = "Carga e Transporte de Entulho ou Material Excedente (DMT 5 km)"
VERSION = "v20260928e-br-transporte-unificado"


def leer(p):
    raw = io.open(p, encoding="utf-8", newline="").read()
    return raw, json.loads(raw)


def escribir(p, raw_antes, doc):
    txt = json.dumps(doc, ensure_ascii=False, indent=2) + "\n"
    if "\r\n" in raw_antes:
        txt = txt.replace("\n", "\r\n")
    io.open(p, "w", encoding="utf-8", newline="").write(txt)


def main(aplicar: bool) -> None:
    raw, doc = leer(F_BR)
    items = doc["items"]
    por = {i["codigo"]: i for i in items}
    if QUEDA in por and not any(c in por for c in SALEN) and por[QUEDA]["nombre"] == NOMBRE:
        print("Ya está unificado: nada que hacer.")
        return
    faltan = [c for c in (QUEDA, *SALEN) if c not in por]
    if faltan:
        sys.exit(f"No están en el catálogo: {faltan}. Paro.")
    receta = lambda i: [(l["idCanonico"], l["rendimiento"]) for l in i["insumos"]]
    distintos = [c for c in SALEN if receta(por[c]) != receta(por[QUEDA])]
    if distintos:
        sys.exit(f"{distintos} ya no tienen la misma receta que {QUEDA}: no unifico. Paro.")
    print(f"{QUEDA}: «{por[QUEDA]['nombre']}» → «{NOMBRE}»")
    for c in SALEN:
        print(f"sale {c}: «{por[c]['nombre']}»")
    print(f"ítems: {len(items)} → {len(items) - len(SALEN)} · versión → {VERSION}")
    if not aplicar:
        print("(Simulación: no se escribió nada.)")
        return
    por[QUEDA]["nombre"] = NOMBRE
    doc["items"] = [i for i in items if i["codigo"] not in SALEN]
    doc["version"] = VERSION
    escribir(F_BR, raw, doc)
    rawm, man = leer(F_MAN)
    man["resources"]["catalogo_BR"]["version"] = VERSION
    escribir(F_MAN, rawm, man)
    print("Escrito.")


if __name__ == "__main__":
    main("--aplicar" in sys.argv)
