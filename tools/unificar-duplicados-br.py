"""UNIFICAR ÍTEMS DE BRASIL QUE QUEDARON CON LA MISMA RECETA (28-sep-2026).

Al seguir el SINAPI, ítems que en Bolivia eran distintos quedaron en Brasil con exactamente la misma receta (el SINAPI
no distingue «importado», placa de 0,90, clase E-40, terreno blando/semiduro…). Oscar aprobó (28-sep) unificar los
grupos que además tienen el MISMO tipo BIM y los MISMOS parámetros. Los que comparten receta pero miden otro objeto
del modelo (pintura de muro / de cubierta, piso / revoque…) NO se tocan.

Reglas:
  · queda el primero de cada grupo; los demás salen del catálogo de Brasil;
  · se vuelve a comprobar, al correr, que la receta, el tipo BIM y los parámetros son iguales: si no, no se toca el grupo;
  · ningún ítem que salga puede figurar en `recursos/ejemplo1_BR.ifc`;
  · quien ya tiene en su biblioteca un ítem que sale lo CONSERVA (el catálogo no borra ítems del usuario);
  · sólo `catalogo/v1.0/items_BR.json` y la versión `catalogo_BR`. Precios y demás países: nada.

Uso:  python tools/unificar-duplicados-br.py [--aplicar]
"""
import io
import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
F_BR = RAIZ / "catalogo/v1.0/items_BR.json"
F_MAN = RAIZ / "manifest.json"
F_IFC = RAIZ / "recursos/ejemplo1_BR.ifc"
VERSION = "v20260928i-br-unificados"

# queda → (salen, nombre nuevo del que queda o None)
GRUPOS = {
    "UC001BR": (["CU002BR", "CU003BR"], None),
    "UH002BR": (["OT003BR"], None),
    "OT016BR": (["OT017BR", "OG061BR"], "Escavação Manual 0-1.5 M"),     # ya no es sólo «terreno mole»
    "UH009BR": (["MP007BR"], None),
    "OT004BR": (["IS083BR"], None),
    "IS003BR": (["IS033BR"], None),
    "OG023BR": (["OG024BR"], None),
    "CU009BR": (["CU013BR"], None),
    "AC011BR": (["AC012BR"], None),
    "MP012BR": (["MP014BR"], None),
    "MP013BR": (["MP015BR"], None),
    "AC022BR": (["AC024BR"], None),
    "IS008BR": (["IS007BR"], None),
    "IS053BR": (["IS056BR"], None),
    "IS054BR": (["IS057BR"], None),
}


def leer(p):
    raw = io.open(p, encoding="utf-8", newline="").read()
    return raw, json.loads(raw)


def escribir(p, raw_antes, doc):
    txt = json.dumps(doc, ensure_ascii=False, indent=2) + "\n"
    if "\r\n" in raw_antes:
        txt = txt.replace("\n", "\r\n")
    io.open(p, "w", encoding="utf-8", newline="").write(txt)


def receta(i):
    return sorted((l["idCanonico"], l["rendimiento"]) for l in i["insumos"])


def medida(i):
    return ((i.get("tipoIfc") or ""), [str(p.get("nombre", "")).lower() for p in (i.get("parametros") or []) if isinstance(p, dict)],
            i.get("unidadResultado"))


def main(aplicar):
    raw, doc = leer(F_BR)
    por = {i["codigo"]: i for i in doc["items"]}
    ifc = io.open(F_IFC, encoding="utf-8", errors="ignore").read().upper() if F_IFC.exists() else ""
    salen, renombres, saltados = [], [], []
    for queda, (otros, nombre) in GRUPOS.items():
        if queda not in por:
            saltados.append((queda, "el que queda no está en el catálogo")); continue
        presentes = [c for c in otros if c in por]
        if not presentes:
            continue                                               # ya unificado
        malos = [c for c in presentes if receta(por[c]) != receta(por[queda]) or medida(por[c]) != medida(por[queda])]
        if malos:
            saltados.append((queda, f"{malos} ya no tienen la misma receta, tipo BIM o parámetros")); continue
        en_ifc = [c for c in presentes if re.search(r"\b" + re.escape(c[:-2]) + r"(BR)?\b", ifc)]
        if en_ifc:
            saltados.append((queda, f"{en_ifc} figuran en el IFC de ejemplo")); continue
        print(f"queda {queda} «{por[queda]['nombre']}»" + (f"  →  «{nombre}»" if nombre and nombre != por[queda]["nombre"] else ""))
        for c in presentes:
            print(f"      sale {c} «{por[c]['nombre']}»")
        salen += presentes
        if nombre and nombre != por[queda]["nombre"]:
            renombres.append((queda, nombre))
    for q, why in saltados:
        print(f"NO SE TOCA {q}: {why}")
    print(f"\nítems: {len(doc['items'])} → {len(doc['items']) - len(salen)} · salen {len(salen)} · versión → {VERSION}")
    if not salen and not renombres:
        print("Nada que hacer."); return
    if not aplicar:
        print("(Simulación: no se escribió nada.)"); return
    for q, n in renombres:
        por[q]["nombre"] = n
    doc["items"] = [i for i in doc["items"] if i["codigo"] not in set(salen)]
    doc["version"] = VERSION
    escribir(F_BR, raw, doc)
    rawm, man = leer(F_MAN)
    man["resources"]["catalogo_BR"]["version"] = VERSION
    escribir(F_MAN, rawm, man)
    print("Escrito.")


if __name__ == "__main__":
    main("--aplicar" in sys.argv)
