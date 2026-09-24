"""TIPO BIM Y MEDIDAS DE LOS ÍTEMS: que midan bien sobre el objeto del IFC (Oscar, 24-sep-2026: «hay un ítem
que me salió negativo» → «revisa qué otros ítems de Perú, Ecuador y otros países tienen ese mismo problema; en
Bolivia estaba bien» → «y revisa sus tipos BIM»).

ArqOn PC mide con el tipo del OBJETO (muro, losa, columna…) y le pasa a cada parámetro del ítem la medida que
ese objeto tiene para ese rol (arqon-pc/src/core/ifc-dimmatriz.ts · dimensionDe):
  · MURO / VENTANA / PUERTA: Largo, Alto = la cara; «Ancho» = el ESPESOR. Un m2 Largo × Ancho sobre un muro
    da largo × espesor (0,08 m² en la capa de 2 cm) y, menos los vanos, NEGATIVO.
  · COLUMNA: Ancho y Largo = la SECCIÓN, Alto = la altura. Un «m» con Largo mide 0,30 en vez de 3 m.
  · VIGA / PERFIL: Ancho y Alto = la sección, Largo = el largo.
  · PILOTE: Largo y Alto son los DOS la profundidad → Largo × Ancho × Alto da profundidad².
Y el encofrado / tarrajeo / pintura de una columna, viga o zapata va ALREDEDOR, no en una cara.

El criterio de tipo BIM es el de Bolivia (que está bien): sin tipo lo que no es un objeto del modelo (puntos
de instalación, globales, movimiento de tierras, transporte, señalética, herrajes), los aparatos sanitarios
son TERMINAL, el acero en kg sin tipo.

`corregir(item)` → (item corregido, [qué cambió]). Idempotente: correrlo dos veces no cambia nada más.
"""
import re
import unicodedata

PARAM = lambda n: {"nombre": n, "valorDefault": 1, "unidad": "m", "visiblePorDefecto": True}


def _sa(s):
    return unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()


def _pnombres(i):
    ps = i.get("parametros") or []
    if isinstance(ps, str): return None                    # formato viejo en texto: no se toca
    return [p.get("nombre") for p in ps]


# Lo que NO es un objeto del modelo: no lleva tipo BIM (criterio de Bolivia).
NO_OBJETO = re.compile(
    r"^(acarreo|eliminaci|excavaci|relleno|nivelaci[oó]n de terreno|trazo|replanteo|limpieza|demolici|desmontaje|"
    r"rotura|derrocamiento|levantamiento de|picado|rampa|corte de|bomba|"
    r"transporte|flete|movilizaci|humedecimiento|establecimiento|cerco provisional|corte en|se[nñ]al|zona segura|"
    r"pozo a tierra|ensayo|prueba|curado)|"
    r"(bisagra|cerrojo|cerradura|chapa de (seguridad|puerta)|manija|anclaje de tabiqueria|pases? para tuber|soporte met[aá]lico|jabonera|toallero|"
    r"dispensador|apoyos? (fijo|movil)|estanteria|mueble|closet|anaquel|topes? para puertas?|extintor|platina de aluminio|tapa ?juntas? .*pisos?|junta de dilataci|"
    r"ang\.? ?\"?l\"? de apoyo|bancas? de madera|ladrillo de techo|manejo de la cobertura vegetal)")
SANITARIO = re.compile(r"(inodoro|urinario|lavatorio|ovalin|lavadero|ducha|bidet|lavamanos)")
ENVUELVE = re.compile(r"(encofrad|tarraje|pintura|solaquead|revoque|enlucid|empastad)")
OBRA = {"WALL", "CURTAINWALL", "SLAB", "ROOF", "COLUMN", "BEAM", "FOOTING", "DOOR", "WINDOW", "STAIR", "MEMBER",
        "PILE", "RAILING", "COVERING"}
CARA = {"WALL", "CURTAINWALL", "WINDOW", "DOOR", "MEMBER"}


def tipo_corregido(i):
    """El tipo BIM que corresponde (o el que ya tiene). "" = no es un objeto del modelo."""
    t = (i.get("tipoIfc") or "").strip().upper()
    n = _sa(i.get("nombre"))
    u = _sa(i.get("unidadResultado"))
    cod = (i.get("codigo") or "").upper()
    # Sólo se corrigen los tipos de OBRA (los que pone el detector por nombre). Los de instalaciones de
    # Bolivia (PIPE, VALVE, TERMINAL, GENERICO) quedan como están: Bolivia está bien.
    if t not in OBRA: return t
    if u in ("pto", "glb", "gbl", "global", "est", "mes", "hr", "hh", "dia"): return ""
    # El acero en kg va a las BARRAS del modelo (IfcReinforcingBar), como los 147 ítems originales de Perú.
    if u == "kg": return "REINFORCING_BAR" if re.search(r"(acero|fierro|varilla|malla)", n) else ""
    # Una PUERTA que «incluye cerrojo y candado» sigue siendo una puerta: el herraje suelto es lo que no va.
    if NO_OBJETO.search(n) and not re.match(r"^(suministro (e instalacion |y colocacion )?de )?puertas? ", n): return ""
    if cod.startswith(("IE", "IS")):                         # instalaciones: nunca un muro, techo o losa
        return "TERMINAL" if cod.startswith("IS") and SANITARIO.search(n) else ""
    if "cubierta aislante" in n: return ""
    if t == "STAIR" and re.search(r"(baranda|pasamano)", n): return "RAILING"
    if t in ("ROOF",) and re.search(r"(contrazocalo|encuentro pared)", n): return "WALL"
    return t


def corregir(i):
    """(item corregido, cambios). No toca nombre, código, unidad, insumos ni precios."""
    x, cambios = dict(i), []
    t0 = (x.get("tipoIfc") or "").strip().upper()
    t = tipo_corregido(x)
    if t != t0:
        x["tipoIfc"] = t; cambios.append(f"tipo BIM {t0 or '—'} → {t or '—'}")
    ps = _pnombres(x)
    if ps is None: return x, cambios
    u = _sa(x.get("unidadResultado"))
    n = _sa(x.get("nombre"))
    formula = (x.get("formulaResultado") or "").strip()
    envuelve = bool(ENVUELVE.search(n)) and "arista" not in n

    def poner(params, f, porque):
        if [p for p in params] == ps and (f or "") == formula: return
        x["parametros"] = [PARAM(p) for p in params]
        x["formulaResultado"] = f
        cambios.append(f"medidas {'×'.join(ps) or '—'}{' (' + formula + ')' if formula else ''} → "
                       f"{'×'.join(params) or 'volumen real'}{' (' + f + ')' if f else ''} · {porque}")

    if u == "m2" and t == "COLUMN" and envuelve:
        poner(["Ancho", "Largo", "Alto"], "2*(Ancho+Largo)*Alto", "alrededor de la columna")
    elif u == "m2" and t == "BEAM" and envuelve:
        poner(["Ancho", "Alto", "Largo"], "(Ancho+2*Alto)*Largo", "fondo y costados de la viga")
    elif u == "m2" and t == "FOOTING" and envuelve:
        poner(["Largo", "Ancho", "Alto"], "2*(Largo+Ancho)*Alto", "los cuatro lados de la zapata")
    elif u == "m2" and t in CARA and ps == ["Largo", "Ancho"] and not formula:
        poner(["Largo", "Alto"], "", "en muro/ventana/puerta el m2 es la cara; «Ancho» es el espesor")
    elif u == "m" and t == "COLUMN" and ps == ["Largo"] and not formula:
        poner(["Alto"], "", "en una columna el largo es su altura")
    elif u == "m3" and t == "PILE" and ps:
        poner([], "", "en un pilote Largo y Alto son la profundidad: se mide su volumen real")
    return x, cambios
