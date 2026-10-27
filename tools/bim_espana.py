"""TIPO BIM PARA LA BASE DE ESPAÑA (27-oct-2026, Oscar: «prepará el tipo BIM para España»). 6.507 ítems, 0 con tipo.

Reglas con el VOCABULARIO de España (fábrica, forjado, solera, alicatado, enfoscado, pilar, zuncho…) y el CAPÍTULO
de cada ítem; sin tipo lo que no es un objeto del modelo (instalaciones, control de calidad, seguridad y salud,
residuos, demoliciones, movimiento de tierras, urbanización, mantenimiento). Después, las MEDIDAS con
`reglas_bim.corregir` (la misma de Perú y Ecuador): el m2 de un muro es Largo × Alto, el revoque de un pilar va
alrededor, etc. Sólo toca tipoIfc / parametros / formulaResultado. NO publica: escribe el JSON y la lista.
"""
import json, re, sys, csv, unicodedata
from collections import Counter
sys.path.insert(0, sys.argv[1])
import reglas_bim

sa = lambda s: unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()

CAP_FUERA = re.compile(r"^(instalaciones|control de calidad|seguridad y salud|gestion de residuos|mantenimiento|"
                       r"acondicionamiento de terrenos|demoliciones|urbanizaciones|equipamiento|gravas|sin capitulo)")
NO_OBJETO = re.compile(r"^(desmont|demolic|levantad|arranque|retirada|apeo|apuntalam|cajeado|rebaje|repaso|limpieza|"
                       r"picado|recrecido de juntas|sellado de juntas|transporte|carga |excavac|relleno|terraplen|"
                       r"replanteo|ensayo|prueba|reparaci|tratamiento de fisuras|inyecci)")
UNID_NO = {"pto", "glb", "gbl", "h", "hr", "mes", "dia", "pa", "kg", "t"}

REGLAS = [  # (patrón sobre el nombre, tipo) — el primero que calce
    (r"muro cortina", "CURTAINWALL"),
    (r"(barandilla|pasamanos|antepecho metal)", "RAILING"),
    (r"(escalera|peldan|zanca|meseta)", "STAIR"),
    (r"(micropilote|pilote)", "PILE"),
    (r"(zapata|encepado|losa de cimentaci|cimentaci|cimiento)", "FOOTING"),
    (r"(pilar|columna|soporte de hormig)", "COLUMN"),
    (r"(viga|zuncho|jacena|dintel|cargadero|riostra|correa)", "BEAM"),
    (r"(puerta|portal|block de puerta|portón|porton)", "DOOR"),
    (r"(ventana|balconera|claraboya|lucernario|mampara|ojo de buey)", "WINDOW"),
    (r"(cubierta|tejado|teja|faldon|azotea|canalon|limahoya|cumbrera|alero)", "ROOF"),
    (r"(forjado|losa|solera|placa alveolar|bovedilla|prelosa)", "SLAB"),
    (r"(falso techo|techo|cielo raso|plafon)", "SLAB"),
    (r"(pavimento|solado|baldosa|tarima|parquet|terrazo|rodapie|recrecido|mortero autonivel)", "SLAB"),
    (r"(fabrica|tabique|tabicon|muro|cerram|trasdosado|citara|hoja de ladrillo|mampost|"
     r"panel sandwich|bloque de hormig|fachada)", "WALL"),
    (r"(alicatado|enfoscado|guarnecido|enlucido|aplacado|chapado|revestimiento|monocapa|estuco|"
     r"pintura|paramento|zocalo)", "WALL"),
]

def tipo_es(i):
    n, cap, u = sa(i.get("nombre")), sa(i.get("categoria")), sa(i.get("unidadResultado"))
    if CAP_FUERA.search(cap) or NO_OBJETO.search(n) or u in UNID_NO: return ""
    # Aislamiento e impermeabilización: según dónde va.
    if re.search(r"(aislamiento|impermeab|lamina)", n):
        if re.search(r"(cubierta|azotea)", n): return "ROOF"
        if re.search(r"(suelo|forjado|solera)", n): return "SLAB"
        if re.search(r"(fachada|muro|tabique|camara)", n): return "WALL"
        return ""
    for pat, t in REGLAS:
        if re.search(pat, n):
            if t in ("DOOR", "WINDOW") and u not in ("u", "ud", "m2", "pza"): return ""
            return t
    return ""

d = json.load(open(sys.argv[2], encoding="utf-8"))
items = d["items"]
filas, cuenta, cambios_med = [], Counter(), 0
for k, it in enumerate(items):
    t = tipo_es(it)
    if not t: cuenta["—"] += 1; filas.append((it.get("codigo"), it.get("nombre"), it.get("categoria"), it.get("unidadResultado"), "", "", "")); continue
    x = dict(it); x["tipoIfc"] = t
    # LAS MEDIDAS ESCRITAS por tipo y unidad (sin ellas el motor sembraría las del tipo aunque la unidad sea «m»:
    # un rodapié de losa en m daría Largo×Ancho). m → Largo (pilar: Alto); m2 → cara o planta; m3 → volumen.
    if not x.get("parametros"):
        u2 = sa(x.get("unidadResultado"))
        cara = t in ("WALL", "CURTAINWALL", "DOOR", "WINDOW")
        dims = {"m": ["Alto"] if t == "COLUMN" else ["Largo"],
                "m2": ["Largo", "Alto"] if cara else ["Largo", "Ancho"],
                "m3": (["Largo", "Alto", "Ancho"] if cara else ["Largo", "Ancho", "Alto"] if t in ("COLUMN", "BEAM", "FOOTING", "STAIR") else ["Largo", "Ancho", "Espesor"])}.get(u2)
        if t == "PILE" and u2 == "m3": dims = []
        if dims:
            x["parametros"] = [reglas_bim.PARAM(d) for d in dims]
            x["formulaResultado"] = "*".join(dims)
    y, ch = reglas_bim.corregir(x)
    if any(c.startswith("medidas") for c in ch): cambios_med += 1
    items[k] = y
    cuenta[y.get("tipoIfc") or "—"] += 1
    filas.append((it.get("codigo"), it.get("nombre"), it.get("categoria"), it.get("unidadResultado"), y.get("tipoIfc") or "",
                  "×".join(p.get("nombre", "") for p in (y.get("parametros") or []) if isinstance(p, dict)), y.get("formulaResultado") or ""))
d["version"] = "v20261027-tipos-bim"
open(sys.argv[3], "w", encoding="utf-8").write(json.dumps(d, ensure_ascii=False, indent=1) + "\n")
with open(sys.argv[4], "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f, delimiter=";"); w.writerow(["Código", "Ítem", "Capítulo", "Ud", "Tipo BIM propuesto", "Medidas", "Fórmula"])
    for r in sorted(filas, key=lambda r: (r[4] == "", r[4], r[2] or "", r[0] or "")): w.writerow(r)
print("total", len(items), dict(cuenta.most_common()), "medidas corregidas", cambios_med)
