"""BRASIL: QUITAR DE LA LISTA DE PRECIOS LOS INSUMOS «ESTIMADOS» QUE YA NO USA NINGUNA RECETA (28-sep-2026).

Oscar: «sólo SINAPI, nada estimado». Al pasar las recetas al SINAPI, cientos de insumos heredados de Bolivia —con precio
«ESTIMADO por relación con Bolivia»— quedaron sin ningún ítem que los use. Se sacan de `precios/v1.0/oficiales_BR.json`.

  · Sale un insumo sólo si su precio es ESTIMADO en las 10 ciudades Y ninguna receta de `items_BR.json` lo usa.
  · Los estimados que TODAVÍA usa alguna receta se quedan (salen cuando esos ítems se resuelvan).
  · Los insumos con precio SINAPI no se tocan, se usen o no.
  · Ningún precio cambia. Quien ya tiene el insumo en su lista lo conserva: sólo deja de ofrecerse.
  · Sólo Brasil: `oficiales_BR.json` y la versión `precios_BR` del manifest.

Uso:  python tools/quitar-estimados-sin-uso-br.py [--aplicar]
"""
import io
import json
import sys
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
F_BR = RAIZ / "catalogo/v1.0/items_BR.json"
F_PR = RAIZ / "precios/v1.0/oficiales_BR.json"
F_MAN = RAIZ / "manifest.json"
VERSION = "v20260928h-br-sinapi-202608"


def leer(p):
    raw = io.open(p, encoding="utf-8", newline="").read()
    return raw, json.loads(raw)


def escribir(p, raw_antes, doc):
    txt = json.dumps(doc, ensure_ascii=False, indent=2) + "\n"
    if "\r\n" in raw_antes:
        txt = txt.replace("\n", "\r\n")
    io.open(p, "w", encoding="utf-8", newline="").write(txt)


def es_estimado(p):
    return "ESTIMADO" in (p.get("nota") or "")


def main(aplicar):
    _, cat = leer(F_BR)
    raw, pre = leer(F_PR)
    usados = {l["idCanonico"] for i in cat["items"] for l in i["insumos"]}
    por_ciudad = [{p["idCanonico"] for p in c["precios"] if es_estimado(p)} for c in pre["ciudades"]]
    estimados = set.intersection(*por_ciudad)                  # estimado en TODAS las ciudades
    salen = estimados - usados
    sp = {p["idCanonico"]: p for p in pre["ciudades"][0]["precios"]}
    total = len(pre["ciudades"][0]["precios"])
    print(f"insumos en la lista: {total} · estimados: {len(estimados)} · los usa alguna receta: {len(estimados & usados)} · salen: {len(salen)}")
    print("por categoría:", dict(Counter(sp[k]["categoria"] for k in salen).most_common()))
    faltan = sorted(usados - set(sp))
    if faltan:
        sys.exit(f"Hay recetas con insumos que no están en la lista de precios: {faltan[:5]}. Paro.")
    if not salen:
        print("Nada que quitar."); return
    if not aplicar:
        print("(Simulación: no se escribió nada.)"); return
    for c in pre["ciudades"]:
        c["precios"] = [p for p in c["precios"] if p["idCanonico"] not in salen]
    pre["version"] = VERSION
    escribir(F_PR, raw, pre)
    rawm, man = leer(F_MAN)
    man["resources"]["precios_BR"]["version"] = VERSION
    escribir(F_MAN, rawm, man)
    print(f"Escrito: quedan {len(pre['ciudades'][0]['precios'])} insumos por ciudad · {VERSION}")


if __name__ == "__main__":
    main("--aplicar" in sys.argv)
