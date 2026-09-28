"""AJUSTE DE RENDIMIENTOS DE BRASIL (28-sep-2026). Oscar: «alterar ligeramente los rendimientos entre 2 % o 3 %,
excepto de hormigones, así como lo hicimos con Bolivia» → «haz los cuatro puntos, muéstrame el resumen primero,
aplica 3 igual que Bolivia».

Sólo toca `catalogo/v1.0/items_BR.json` (y la versión `catalogo_BR` del manifest). Bolivia y los demás, nada.

1. AJUSTE DE BOLIVIA (el del 11-sep-2026, `v20260911-rendimientos`): −10 % mano de obra, equipo/herramienta y
   materiales menores; +5 % cerámica y mampostería. Brasil nació de las recetas bolivianas ANTERIORES, así que
   no se adivina por nombre: cada ítem BR se empareja con su par boliviano (misma posición en el catálogo) y cada
   insumo con el suyo (`br_<id>` ↔ `<id>`); donde Bolivia quedó ×0,90 o ×1,05 respecto de Brasil, Brasil recibe
   ese mismo factor. Lo que Bolivia QUITÓ (la madera de construcción) no se toca acá.
2. VARIACIÓN DE 2 % A 3 % por línea, hacia arriba o hacia abajo, FIJA (sale de un hash del código del ítem y del
   insumo: repetible y auditable, no cambia en cada corrida). Se aplica DESPUÉS del punto 1.
3. EXCEPTO HORMIGONES: los ítems de hormigón (concreto) estructural o de relleno no se varían (ni en el punto 2).
   Los que sólo mencionan «concreto» por otra razón (bloques, tubos, piletas, pintura de concreto aparente,
   demoliciones…) sí.
4. TIPO BIM: «Fachada Pele de Vidro» = CURTAINWALL (muro cortina), como su par boliviano AC058.

Uso:  python tools/ajuste-rendimientos-br.py            → sólo el RESUMEN (no escribe)
      python tools/ajuste-rendimientos-br.py --aplicar  → escribe items_BR.json y el manifest
"""
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
F_BR = RAIZ / "catalogo/v1.0/items_BR.json"
F_BO = RAIZ / "catalogo/v1.0/items.json"
F_MAN = RAIZ / "manifest.json"
VERSION = "v20260928-br-rendimientos"

# Hormigón: el ítem ES un elemento/capa de CONCRETO (se excluye entero). Tiene que decir «concreto» (o ser una
# losa/radier/estaca/cinta, que sólo pueden ser de concreto); lo que nombra el concreto por otra razón, no.
HORMIGON = re.compile(r"(concreto|^laje |^radier|^estaca|^cinta de amarra)", re.I)
NO_HORMIGON = re.compile(r"(demoli|retirada|remo[cç][aã]o|corte de|bloco|bloquete|tubo de concreto|tanque de lavar|"
                         r"pintura|caixa|po[cç]o|a[cç]o |lumin[aá]ria|bancada|reboco|^piso de|pingadeira|alambrado)", re.I)


def es_hormigon(nombre: str) -> bool:
    return bool(HORMIGON.search(nombre or "")) and not NO_HORMIGON.search(nombre or "")


def variacion(codigo: str, insumo: str) -> float:
    """Factor fijo entre ±2 % y ±3 % (signo y magnitud salen del hash)."""
    h = hashlib.sha256(f"{codigo}|{insumo}".encode()).digest()
    mag = 0.02 + (h[0] / 255) * 0.01
    return 1 + mag if h[1] % 2 == 0 else 1 - mag


def redondeo(v: float):
    r = float(f"{v:.4g}") if v < 1 else round(v, 4)
    return int(r) if r == int(r) else r        # «6» queda «6», no «6.0» (sin cambios de forma en el diff)


def main(aplicar: bool) -> None:
    dbr = json.loads(F_BR.read_text(encoding="utf-8"))
    bo = json.loads(F_BO.read_text(encoding="utf-8"))["items"]
    br = dbr["items"]
    assert len(br) == len(bo), "BR y BO ya no tienen la misma cantidad de ítems: revisar el emparejamiento"
    cont = Counter()
    excluidos, ejemplos = [], []
    for a, b in zip(br, bo):
        bo_por_id = {x.get("idCanonico"): x for x in b.get("insumos", [])}
        horm = es_hormigon(a["nombre"])
        if horm:
            excluidos.append(a["nombre"])
        for x in a.get("insumos", []):
            r0 = float(x.get("rendimiento") or 0)
            if not r0:
                continue
            r = r0
            # 1. Ajuste de Bolivia.
            par = bo_por_id.get(re.sub(r"^br_", "", x.get("idCanonico") or ""))
            if par and float(par.get("rendimiento") or 0):
                f = float(par["rendimiento"]) / r0
                if abs(f - 0.9) < 0.006:
                    r *= 0.9; cont["bolivia −10 %"] += 1
                elif abs(f - 1.05) < 0.006:
                    r *= 1.05; cont["bolivia +5 %"] += 1
            # 2. Variación 2–3 % (no en hormigones).
            if horm:
                cont["hormigón (sin variar)"] += 1
            else:
                r *= variacion(a["codigo"], x.get("idCanonico") or x.get("nombre") or "")
                cont["variadas 2–3 %"] += 1
            if r == r0:
                continue                         # sin cambio: el valor queda tal cual estaba escrito
            r = redondeo(r)
            if r != r0:
                cont["líneas que cambian"] += 1
                if len(ejemplos) < 12:
                    ejemplos.append(f"{a['nombre'][:34]:34} | {x['nombre'][:24]:24} {r0:>9} → {r}")
            x["rendimiento"] = r
        # 4. Muro cortina.
        if b.get("tipoIfc") == "CURTAINWALL" and a.get("tipoIfc") != "CURTAINWALL":
            a["tipoIfc"] = "CURTAINWALL"; cont["tipo BIM → CURTAINWALL"] += 1
    print(f"Ítems BR: {len(br)} · excluidos por hormigón: {len(excluidos)}")
    for k, v in cont.most_common():
        print(f"  {k}: {v}")
    print("\nÍtems de hormigón que NO se varían:")
    for n in excluidos:
        print("  ·", n)
    print("\nEjemplos:")
    for e in ejemplos:
        print("  ", e)
    if not aplicar:
        print("\n(Simulación: no se escribió nada. Con --aplicar se publica como", VERSION + ")")
        return
    dbr["version"] = VERSION
    F_BR.write_text(json.dumps(dbr, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    man = json.loads(F_MAN.read_text(encoding="utf-8"))
    man["resources"]["catalogo_BR"]["version"] = VERSION
    F_MAN.write_text(json.dumps(man, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("\nEscrito:", F_BR.name, "y manifest →", VERSION)


if __name__ == "__main__":
    main("--aplicar" in sys.argv)
