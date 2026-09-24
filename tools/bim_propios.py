"""Tipo BIM y medidas de los ÍTEMS PROPIOS de un país del generador (catalogo/fuentes/items_propios_XX.json),
con las reglas de tools/reglas_bim.py (Oscar, 24-sep-2026: «revisa qué otros ítems… y sus tipos BIM»).
El tipo por nombre sale de la regla del PC (`detectarTipoIfcPorNombre`), guardado en
catalogo/fuentes/tipoifc_XX.json. Después: node tools/derivar-desde-bolivia.mjs XX
Uso: python tools/bim_propios.py EC"""
import io, json, os, sys
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
import reglas_bim

PAIS = (sys.argv[1] if len(sys.argv) > 1 else "").upper()
BASE = os.path.dirname(AQUI)
ruta = os.path.join(BASE, "catalogo", "fuentes", f"items_propios_{PAIS}.json")
with io.open(ruta, encoding="utf-8") as f: d = json.load(f)
rt = os.path.join(BASE, "catalogo", "fuentes", f"tipoifc_{PAIS}.json")
tipos = json.load(io.open(rt, encoding="utf-8")) if os.path.exists(rt) else {}
n = 0
for k, i in enumerate(d["items"]):
    x = {**i, "tipoIfc": i.get("tipoIfc") or tipos.get(i["codigo"], "")}
    x, c = reglas_bim.corregir(x)
    if x != i:
        d["items"][k] = x; n += 1
        print(f"{i['codigo']:9} {i['nombre'][:55]:55} → {x.get('tipoIfc') or '—'}  {' ; '.join(c)}")
with io.open(ruta, "w", encoding="utf-8") as f: json.dump(d, f, ensure_ascii=False, indent=2)
print(f"{PAIS}: {n} ítems propios con tipo BIM o medidas corregidas")
