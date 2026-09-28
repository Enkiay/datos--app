"""
BRASIL, FASE C: LOS 153 ÍTEMS «ADAPTADA» + LOS 12 SALTEADOS DE LA FASE A (28-sep-2026).

Uso:
  python tools/fase-c-composicoes-br.py [--libro <SINAPI_Referencia_AAAA_MM.xlsx>] [--aplicar]
                                        [--raiz <copia del repo>] [--resumen <archivo.md>]

Sin --aplicar (lo normal): NO toca los datos. Calcula todo y escribe el resumen
`catalogo/fuentes/fase_c_BR_20260928.md` (una sección «## Validación» agregada a mano al final se conserva).
Con --aplicar: escribe items_BR.json, oficiales_BR.json, mapa_sinapi_BR.csv y manifest.json, SÓLO para los
ítems LISTO (y los de NECESITA_DECISION que tengan opción elegida en `ELEGIDAS`). No hace commit ni publica.
`--raiz` permite probarlo sobre una copia del repo.

QUÉ HACE
  Los ítems ADAPTADA del análisis (`catalogo/fuentes/analisis_composicoes_BR_20260928.md`, tabla «## ADAPTADA»)
  no tienen una composição SINAPI de su mismo alcance, pero sí una de la misma familia con otra medida,
  espesor, material o unidad. Acá cada ítem toma la composição MÁS CERCANA y se adapta al alcance del ítem
  con una regla explícita, escrita en la tabla de abajo (`regla`), y queda marcado
  `referencia: "adaptado de SINAPI NNNN… · MM/AAAA"`. También entran los 12 ítems que la fase A salteó
  (10 cuya composição no tiene costo CCD en SP en 08/2026 y 2 con factor de unidad).

  La receta (`spec`) de cada ítem se escribe con las mismas piezas de la fase B y cuatro más:
  · `partes`  [P(composição, cantidad, de dónde sale, mat=1, mo=1, eq=1)]: composições SINAPI sumadas, con
              cantidad por unidad del ítem (conversión de unidad incluida: m² de cara por m, m³ por m² con
              el espesor…). `mat`, `mo`, `eq` escalan SÓLO los materiales, la mano de obra o el equipo de esa
              parte (p. ej. espesor doble: mat = 2 y mo = 1 cuando el SINAPI no escala la mano de obra con el
              espesor).
  · `cambios` {insumo: (hoja, nuevo, factor, motivo)}: el insumo de la composição se cambia por otro insumo
              SINAPI (hoja "ICD"), por una composição (hoja "COMP", se aplana) o por otra M.O./equipo (hoja
              "CCD"); cantidad nueva = cantidad vieja × factor (piezas por m² recalculadas por geometría,
              masa por metro, conversión de unidad…).
  · `escala`  {insumo: (factor, motivo)}: escala una hoja sola.
  · `fijar`   {insumo: (cantidad, motivo)}: pone la cantidad del ítem (kg de acero, m de tubo de SU receta).
  · `quitar`  {insumo: motivo}: saca una hoja que el alcance del ítem no tiene.
  · `extras`  [(hoja, código, cantidad, motivo)]: insumo SINAPI suelto ("ICD"), M.O./equipo suelto ("CCD")
              o insumo BR existente con precio SINAPI ("BR").
  · `sin_ccd` {composição: motivo}: partes cuya composição NO tiene costo CCD en SP en el mes (le falta un
              insumo en el ICD): se arma desde sus líneas; la hoja que falta tiene que cambiarse o quitarse
              con `cambios`/`quitar`.
  Un insumo se nombra por su código ICD ("1287"); una hoja de M.O. o equipo, con "C:" delante ("C:88309").

  Cada composição se aplana con las MISMAS reglas de las fases A y B (se reusan sus funciones): M.O. «com
  encargos complementares» y equipo CHP/CHI = UNA línea con costo CCD; auxiliares abiertas recursivamente;
  insumos ya mapeados se reusan; los que faltan se crean como `br_sinapi_<hoja>_<código>`, se agregan a las
  10 ciudades y al mapa y `tools/precios-sinapi-br.py` les pone el precio SINAPI por UF (si falta, SP con la
  nota). Sólo cambian `insumos` y `referencia`. Código, nombre, categoría, unidad, parámetros, fórmula,
  tipoIfc, etiqueta y «verificado» no se tocan.

CLASES
  · LISTO: la adaptación tiene fundamento (regla escrita); se aplica con --aplicar.
  · NECESITA_DECISION: la adaptación cambia lo que el ítem ES (un ladrillo que en Brasil no existe, un
    tanque de otro tamaño…): opciones A/B con su costo SP y una recomendada. Se aplica sólo lo que esté en
    `ELEGIDAS`. Una opción None = receta actual.
  · NO_CONVIENE: queda la receta actual; se dice por qué.

CONTROLES (si falla uno, el ítem no se aplica y se informa)
  · toda composição usada está en el Analítico; si tiene costo CCD en SP, su aplanado SIN adaptar lo
    reproduce dentro del 5 %; si no lo tiene, tiene que estar declarada en `sin_ccd`;
  · toda hoja que queda en la receta tiene precio SINAPI > 0 en SP (los insumos nuevos toman el precio de su
    UF o, si falta, el de SP) y todo insumo BR ya existente tiene precio «REFERENCIA: SINAPI …» > 0 en las
    10 ciudades; ningún ESTIMADO;
  · con --aplicar: antes de escribir se comprueba que correr `precios-sinapi-br.py` NO cambia ningún precio
    ya publicado y que sólo cambian ítems de esta fase; si no, no se escribe nada.

VERSIONES al aplicar: catalogo_BR `v20260928f-br-sinapi-fase-c` (si la publicada ya es igual o mayor, la letra
siguiente a la publicada: nunca baja); precios_BR sube una letra sobre la publicada
(`v20260928d-…` → `v20260928e-br-sinapi-202608`) sólo si entran insumos nuevos.
"""
import argparse, csv, datetime, importlib.util, io, json, math, os, re, statistics, sys

AQUI = os.path.dirname(os.path.abspath(__file__))


def _modulo(nombre, archivo):
    spec = importlib.util.spec_from_file_location(nombre, os.path.join(AQUI, archivo))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


fb = _modulo("fase_b", "fase-b-composicoes-br.py")  # (la fase A ya deja sys.stdout en UTF-8)
fa = fb.fa

VERSION_CATALOGO = "v20260928f-br-sinapi-fase-c"
TOL = 0.05
# Los 12 que la fase A salteó (tabla EQUIVALENTE del análisis): 10 sin costo CCD en SP y 2 con factor de unidad.
SALTEADOS_A = ["AC034BR", "AC058BR", "AC063BR", "AC064BR", "CR018BR", "IE004BR", "IE026BR", "IS063BR", "IS065BR",
               "OT021BR", "OG056BR", "OG075BR"]


def P(comp, q, como, mat=1.0, mo=1.0, eq=1.0):
    return (str(comp), float(q), como, float(mat), float(mo), float(eq))


# ═════════════════════════════ RECETAS (28-sep-2026) ═════════════════════════════
#<TABLAS>
# Una función por familia: cada una devuelve (LISTO, DECISION, NO_CONVIENE) de sus ítems. Las recetas son
# constantes escritas a mano (28-sep-2026); la regla de cada una va en `regla` y sale en el resumen.


# ── Acabados (1) ──
def _tablas_acabados1():
    LISTO, DECISION, NO_CONVIENE = {}, {}, {}
    # frag_acabados1.py — fase C, grupo «acabados1» (17 ítems). Se ejecuta con P ya definido.
    # Antecedentes de la fase B que se respetan:
    #   revoque = chapisco (87879 interno, 87905 fachada) + emboço/massa única; piso sobre mortero (≈ 0,05 m³ de arena) =
    #   contrapiso 87630 (3 cm) + piso con colante; pintura/textura exterior = composição + fundo selador 88415.
    # Ladrillo 6 × 12 × 24 (ICD 7260, el que ya trae la receta): 1 ÷ [(0,24 + 0,01) × (0,06 + 0,01)] = 57,14 pzas/m².

    _FORRO_CEDRINHO = ("ICD", "3286", 1,
                       "forro macho/fêmea 10 × 1 cm de cedrinho ou equivalente (madera de densidad media) en vez de pinus")
    _BUCHAS = ("ICD", "7583", 6, "6 buchas S8 con parafuso 4,8 × 50 por m²: los 6 tornillos + 6 tacos de la receta (piezas al entero)")

    LISTO = {
        "AC001BR": {
            "partes": [P("96112", 1, "forro de madeira macho/fêmea 10 × 1 cm con estructura unidirecional (caibros + sarrafos)")],
            "cambios": {"3283": _FORRO_CEDRINHO},
            "extras": [_BUCHAS],
            "regla": ("96112 (forro de pinus con estructura unidirecional) con la tabla cambiada por el forro macho/fêmea de "
                      "cedrinho ou equivalente 3286 (el SINAPI publica pinus, cedrinho y cumaru/ipê: el guanandi es de "
                      "densidad media, como el cedrinho); estructura y M.O. SINAPI; + 6 buchas con parafuso de la receta"),
            "nota": "baja porque la M.O. SINAPI es 1,43 h carpinteiro + 0,86 h ajudante contra 2,77 + 3,24 h de la receta"},
        "AC014BR": {
            "partes": [P("96112", 1, "forro de madeira macho/fêmea 10 × 1 cm: la misma tabla, colocada en pared")],
            "quitar": {"20212": "caibros 6 × 8 de la estructura de techo: en pared los sarrafos van fijados al muro con bucha y parafuso"},
            "cambios": {"3283": _FORRO_CEDRINHO},
            "extras": [_BUCHAS],
            "regla": ("96112 (forro macho/fêmea, lo más cercano: el SINAPI no publica lambri de pared) llevado a pared: sin "
                      "los caibros de techo, sarrafos 2,5 × 5 fijados con 6 buchas con parafuso (receta), tabla de cedrinho "
                      "3286 en vez de pinus; M.O. SINAPI de forro sin cambio (no hay otra publicada)")},
        "AC004BR": {
            "partes": [P("105029", 1, "contraverga moldada in loco, sección 15 × 20 cm = 0,03 m³/m, igual volumen que 30 × 10 cm")],
            "fijar": {"33": (2.3617, "acero CA-50 de la receta: 2,36 kg/m")},
            "escala": {"C:88245": (2.693, "corte y doblado va por kg: 2,3617 ÷ 0,8769 kg"),
                       "C:88238": (2.693, "idem ayudante de armador")},
            "extras": [("BR", "br_cemento_blanco_kg", 1.2725, "cemento blanco del acabado, de la receta: 1,27 kg/m")],
            "regla": ("105029 (contraverga de concreto moldada in loco, sección 15 × 20 = 0,03 m³/m: fôrma, concreto fck 20 "
                      "y colocación) para la sección 30 × 10 = 0,03 m³/m (mismo volumen); acero fijado a 2,36 kg/m de la "
                      "receta con su M.O. de armador × 2,69 (va por kg); + cemento blanco de la receta"),
            "nota": ("baja porque la receta traía 30,8 kg de cemento para 0,03 m³ y 1,41 + 1,40 h de M.O.; el SINAPI pone "
                     "10,3 kg de cemento y 0,27 h pedreiro + 0,22 h servente")},
        "AC005BR": {
            "partes": [P("101159", 0.3325, "19 tijolos 6 × 12 × 24 de la receta ÷ 57,14 pzas/m² (junta 1 cm) = 0,3325 m² de alvenaria")],
            "cambios": {"7258": ("ICD", "7260", 1, "tijolo maciço aparente 6 × 12 × 24 (el insumo que ya trae la receta) en vez del 5 × 10 × 20")},
            "fijar": {"7260": (19, "19,34 piezas de la receta → 19 (piezas al entero)")},
            "regla": ("101159 (alvenaria de tijolo maciço, por m²) × 0,3325 m²/m: 19 tijolos de la receta ÷ 57,14 pzas/m²; "
                      "tijolo cambiado al maciço aparente 6 × 12 × 24 (7260) y fijado en 19 pzas/m; mortero y M.O. SINAPI por "
                      "m² (el mortero por m² es prácticamente el mismo: 0,021 m³/m² en los dos ladrillos)")},
        "AC018BR": {
            "partes": [P("87879", 1, "chapisco interno con colher (base del revoque, como en la fase B)"),
                       P("98562", 1, "argamassa de cimento e areia 1:3 con aditivo impermeabilizante, e = 1,5 cm, llevada al espesor de la receta",
                         mat=1.913)],
            "regla": ("87879 (chapisco) + 98562 (mortero cemento-arena con aditivo impermeabilizante, e = 1,5 cm) llevado al "
                      "espesor de la receta: materiales × 1,913 = arena 0,0489 m³ de la receta ÷ 0,02555 m³ (e ≈ 2,9 cm), "
                      "aditivo en la misma proporción; M.O. SINAPI sin cambio (el SINAPI no publica otro espesor)"),
            "nota": ("baja porque la M.O. SINAPI es 1,06 h pedreiro + 0,25 h servente contra 2,31 + 2,19 h de la receta, y el "
                     "aditivo SINAPI cuesta 6,93/L contra 13,81/kg estimado")},
        "AC029BR": {
            "partes": [P("87263", 1, "piso de porcelanato 60 × 60, ambientes de más de 10 m²")],
            "quitar": {"37595": "argamassa colante AC III: el ítem asienta con mortero de cemento y arena (el de colante es AC030BR)"},
            "extras": [("BR", "br_cemento_portland_kg", 15.39, "cemento del mortero de asiento, de la receta: 15,39 kg/m²"),
                       ("BR", "br_arena_fina_m3", 0.009765, "arena fina del mortero de asiento, de la receta: 0,0098 m³/m²")],
            "regla": ("87263 (porcelanato 60 × 60 con colante AC III) con el colante (9,13 kg) cambiado por el mortero de "
                      "asiento de la receta: 15,39 kg de cemento + 0,0098 m³ de arena fina; porcelanato, rejunte y M.O. SINAPI "
                      "(el rejunte SINAPI reemplaza al cemento blanco)"),
            "nota": ("baja a la mitad porque la M.O. SINAPI es 0,52 h ladrilheiro + 0,17 h servente contra 1,76 + 1,84 h de "
                     "la receta")},
        "AC031BR": {
            "partes": [P("101727", 1, "piso vinílico semiflexível em placas 30 × 30 fijado con cola")],
            "cambios": {"4792": ("ICD", "4790", 1, "placa vinílica semiflexível e = 2 mm (la más cercana a 1,6 mm) en vez de la de 3,2 mm")},
            "regla": ("101727 (placas vinílicas 30 × 30 de 3,2 mm con cola) con la placa cambiada por la de 2 mm (4790), la más "
                      "cercana a 1,6 mm que publica el SINAPI; cola y M.O. SINAPI sin cambio")},
    }

    DECISION = {
        "AC008BR": {
            "pregunta": ("El rodapié cerámico no dice la altura y la receta trae 0,376 m² de cerámica por metro (≈ 33 cm de "
                         "alto, no es un rodapié). El SINAPI sólo publica 7 cm. ¿Qué altura se toma?"),
            "grupo": "Rodapié cerámico: altura",
            "opciones": {
                "A": {"partes": [P("88648", 1, "rodapé cerâmico h = 7 cm, placas 35 × 35")],
                      "regla": "88648 tal cual: rodapé cerâmico de 7 cm con placas 35 × 35 (la altura que publica el SINAPI)",
                      "nota": "baja porque la receta traía 0,376 m² de cerámica por metro (h ≈ 33 cm) y 0,26 h de pedreiro"},
                "B": {"partes": [P("88648", 1, "rodapé cerâmico h = 7 cm, placas 35 × 35")],
                      "escala": {"1287": (1.4286, "altura 10 cm ÷ 7 cm"), "1381": (1.4286, "idem colante"),
                                 "34357": (1.4286, "idem rejunte")},
                      "regla": ("88648 (h = 7 cm) llevado a h = 10 cm: cerámica, colante y rejunte × 10/7; M.O. SINAPI sin "
                                "cambio (el SINAPI no publica otra altura)"),
                      "nota": "baja porque la receta traía 0,376 m² de cerámica por metro (h ≈ 33 cm) y 0,26 h de pedreiro"}},
            "etiquetas": {"A": "rodapié de 7 cm (SINAPI tal cual)", "B": "rodapié de 10 cm (materiales × 10/7)"},
            "recomendada": "A"},
        "AC009BR": {
            "pregunta": ("El nombre dice «Forro de Gesso» (en Brasil, cielo falso de placas), pero la receta es yeso aplicado "
                         "a mano bajo losa (5,5 kg/m², sin placas ni alambre: el «cielo raso de yeso» boliviano), casi lo "
                         "mismo que AC002BR (gesso desempenado em teto, 87415). ¿Qué es el ítem? (si es yeso aplicado, el "
                         "nombre en portugués confunde)"),
            "grupo": "Forro de gesso: ¿placas o yeso aplicado?",
            "opciones": {
                "A": {"partes": [P("87412", 1, "gesso desempenado em teto, e = 0,5 cm, ambientes de 5 a 10 m²")],
                      "regla": ("87412 tal cual: yeso aplicado en techo e = 0,5 cm (el menor espesor SINAPI, 9,66 kg/m²; la "
                                "receta trae 5,5 kg), misma clase de ambiente que AC002BR (87415, e = 1 cm)")},
                "B": {"partes": [P("96109", 1, "forro em placas de gesso 60 × 60, ambientes residenciais")],
                      "regla": "96109 tal cual: cielo falso de placas de gesso 60 × 60 colgadas con alambre, ambientes residenciales"}},
            "etiquetas": {"A": "yeso aplicado en techo 0,5 cm (lo que dice la receta)",
                          "B": "cielo falso de placas de gesso (lo que dice el nombre)"},
            "recomendada": "A"},
        "AC010BR": {
            "pregunta": ("«Revestimento Texturizado Externo»: la receta es incoherente (0,26 kg de cemento para 0,02 m³ de "
                         "arena, sin pintura ni textura). ¿Es la textura acrílica de fachada o un revoque de mortero?"),
            "grupo": "Texturizado exterior: ¿textura acrílica o revoque?",
            "opciones": {
                "A": {"partes": [P("88415", 1, "fundo selador acrílico em paredes externas de casas"),
                                 P("88423", 1, "tinta texturizada acrílica em paredes externas de casas, uma cor")],
                      "regla": ("88415 + 88423: fundo selador + textura acrílica en paredes externas de casas, un color "
                                "(misma regla que la pintura exterior AC067BR)")},
                "B": {"partes": [P("87905", 1, "chapisco de fachada con colher"),
                                 P("87775", 1, "massa única 1:2:8 en fachada con vãos, e = 25 mm (el menor espesor SINAPI)")],
                      "regla": ("87905 + 87775: chapisco + massa única 1:2:8 de fachada e = 25 mm (el SINAPI no publica menos; "
                                "la receta trae 0,02 m³ de arena ≈ 15-20 mm); queda igual que un revoque exterior"),
                      "nota": "sube porque el SINAPI pone 25 mm de mortero con cal y tela en los encuentros"}},
            "etiquetas": {"A": "fundo selador + textura acrílica (88415 + 88423)",
                          "B": "chapisco + massa única de fachada 25 mm (87905 + 87775)"},
            "recomendada": "A"},
        "AC013BR": {
            "pregunta": ("El SINAPI sólo publica la ardósia en PISO (101732) y el ítem es revestimiento de PARED: ¿qué mano "
                         "de obra se toma?"),
            "grupo": "Piedra en pared: mano de obra",
            "opciones": {
                "A": {"partes": [P("87879", 1, "chapisco interno con colher (base en pared)"),
                                 P("101732", 1, "pedra ardósia asentada sobre argamassa 1:3 + colante AC III")],
                      "cambios": {"10731": ("ICD", "4704", 1, "ardósia 20 × 40 (la más cercana a 15 × 30) en vez de 40 × 40")},
                      "regla": ("87879 (chapisco) + 101732 (ardósia sobre argamassa 1:3 y colante AC III) con la piedra "
                                "cambiada a 20 × 40 (4704); M.O. SINAPI de piso sin cambio (0,66 h pedreiro + 0,66 h servente)")},
                "B": {"partes": [P("87879", 1, "chapisco interno con colher (base en pared)"),
                                 P("101732", 1, "pedra ardósia asentada sobre argamassa 1:3 + colante AC III")],
                      "cambios": {"10731": ("ICD", "4704", 1, "ardósia 20 × 40 (la más cercana a 15 × 30) en vez de 40 × 40")},
                      "extras": [("CCD", "88309", 1.116, "M.O. de pared: 0,66 h × (2,691 − 1), relación pared/piso de la cerámica SINAPI (87269 ÷ 87248: 0,6488 ÷ 0,2411)"),
                                 ("CCD", "88316", 0.877, "idem servente: 0,66 h × (2,329 − 1) (0,3004 ÷ 0,129)")],
                      "regla": ("87879 (chapisco) + 101732 (ardósia sobre argamassa 1:3 y colante AC III) con la piedra "
                                "cambiada a 20 × 40 (4704); M.O. de colocación llevada a pared con la relación pared/piso de la "
                                "cerámica SINAPI (87269 ÷ 87248): pedreiro × 2,69, servente × 2,33")}},
            "etiquetas": {"A": "M.O. SINAPI de piso tal cual", "B": "M.O. × relación pared/piso de la cerámica SINAPI"},
            "recomendada": "B"},
        "AC015BR": {
            "pregunta": ("«Reboco externo com massa fina pronta»: la receta sólo trae 1,37 kg/m² de masa fina (≈ 1 mm) con la "
                         "M.O. de un revoque completo (1,85 + 1,76 h). ¿Qué revoque es? (el SINAPI no publica la capa fina sola "
                         "en fachada; con mortero listo sólo publica la aplicación con proyector)"),
            "grupo": "Revoque exterior con mortero listo",
            "opciones": {
                "A": {"partes": [P("87905", 1, "chapisco de fachada con colher"),
                                 P("87775", 1, "massa única de fachada con vãos e = 25 mm, aplicación manual: se toma M.O. y betoneira", mat=0)],
                      "extras": [("ICD", "371", 58.3117, "argamassa industrializada para 25 mm de fachada: el consumo de 87778 (58,31 kg/m²)"),
                                 ("ICD", "37411", 0.1388, "tela de los encuentros, la de 87775")],
                      "regla": ("87905 (chapisco) + 87775 (massa única de fachada 25 mm, manual) con el mortero 1:2:8 cambiado "
                                "por argamassa industrializada: 58,31 kg/m², el consumo de 87778 (mismo espesor, proyectada); "
                                "M.O. SINAPI de aplicación manual")},
                "B": {"partes": [P("87905", 1, "chapisco de fachada con colher"),
                                 P("87775", 1, "massa única 1:2:8 en fachada con vãos, e = 25 mm, preparo en betoneira")],
                      "regla": ("87905 + 87775 tal cual: chapisco + massa única 1:2:8 hecha en obra, e = 25 mm (como AC016BR, "
                                "que lleva 35 mm)")}},
            "etiquetas": {"A": "chapisco + massa única 25 mm con mortero listo (industrializada)",
                          "B": "chapisco + massa única 25 mm con mortero 1:2:8 hecho en obra"},
            "recomendada": "A"},
        "AC023BR": {
            "pregunta": ("El SINAPI no tiene baldosa de granilite (ni 40 × 40 ni otra): publica el ladrilho hidráulico en "
                         "placas (hasta 30 × 30) y el granilite moldado in loco (8 mm, pulido). ¿Con cuál se representa?"),
            "grupo": "Baldosa de granilite",
            "opciones": {
                "A": {"partes": [P("87630", 1, "contrapiso 1:4 de 3 cm (el mortero de base de la receta: 0,051 m³ de arena)"),
                                 P("101726", 1, "piso em ladrilho hidráulico con colante AC III y rejunte")],
                      "cambios": {"3733": ("ICD", "38138", 1, "ladrilho hidráulico 30 × 30 (el formato más cercano a 40 × 40) en vez de 20 × 20")},
                      "quitar": {"7353": "resina acrílica: la baldosa de granilite viene pulida"},
                      "regla": ("87630 (contrapiso 3 cm) + 101726 (ladrilho hidráulico) con la placa 30 × 30 (38138) y sin "
                                "resina; M.O. SINAPI de 101726 (placas 20 × 20); queda como AC028BR menos la resina"),
                      "nota": "sube por la M.O. SINAPI de ladrilho (2,07 h ladrilheiro) y la placa a 134,69/m²"},
                "B": {"partes": [P("87630", 1, "contrapiso 1:4 de 3 cm (el mortero de base de la receta: 0,051 m³ de arena)"),
                                 P("104162", 1, "piso em granilite moldado in loco e = 8 mm, con juntas plásticas y 4 pulidos")],
                      "regla": "87630 (contrapiso 3 cm) + 104162 tal cual: granilite hecho en obra de 8 mm con juntas y pulido"}},
            "etiquetas": {"A": "baldosa: ladrilho hidráulico 30 × 30 sobre contrapiso",
                          "B": "granilite moldado in loco 8 mm sobre contrapiso"},
            "recomendada": "A"},
        "AC034BR": {
            "pregunta": ("La composição exacta 98683 (piso laminado) no tiene costo porque su insumo 44227 (piso laminado de "
                         "madeira) no tiene precio en ninguna UF, y el ICD no trae otro laminado. El insumo flotante más "
                         "cercano con precio es la régua vinílica clicada de 4 mm, que es otro producto. ¿Se usa?"),
            "grupo": "Composição exacta sin precio del insumo",
            "opciones": {
                "A": {"partes": [P("98683", 1, "piso laminado flutuante sobre manta de polietileno: M.O. y manta")],
                      "sin_ccd": {"98683": "falta el precio del insumo 44227 (piso laminado), que no está en el ICD 08/2026"},
                      "cambios": {"44227": ("ICD", "38180", 1, "régua vinílica semiflexível de encaixe clicado e = 4 mm en vez del laminado de madeira")},
                      "regla": ("98683 armada desde sus líneas (M.O. y manta de polietileno 5 mm) con el laminado 44227, que no "
                                "tiene precio, cambiado por la régua vinílica clicada de 4 mm (38180): es OTRO producto")},
                "B": None},
            "etiquetas": {"A": "piso flotante de régua vinílica clicada 4 mm",
                          "B": "dejar la receta actual hasta que el SINAPI publique el precio del laminado"},
            "recomendada": "B"},
        "AC058BR": {
            "pregunta": ("La composição exacta 104099 (fachada cortina stick) no tiene costo porque su insumo 44970 no tiene "
                         "precio en ninguna UF (tampoco 104100 a 104103). Lo más cercano con costo es el caixilho fijo de "
                         "aluminio con vidrio de 4 mm (100674), que es una ventana fija, no una piel de vidrio. ¿Se usa?"),
            "grupo": "Composição exacta sin precio del insumo",
            "opciones": {
                "A": {"partes": [P("100674", 1, "caixilho fixo de alumínio con vidrio 4 mm incluido, fijado con parafusos y silicone")],
                      "regla": ("100674 tal cual por m²: caixilho fijo de aluminio con vidrio liso de 4 mm; NO es fachada cortina "
                                "ni vidrio reflectivo (el ICD no trae vidrio reflectivo)")},
                "B": None},
            "etiquetas": {"A": "caixilho fijo de aluminio con vidrio 4 mm (100674)",
                          "B": "dejar la receta actual hasta que el SINAPI publique el precio de la fachada cortina"},
            "recomendada": "B"},
        "AC063BR": {
            "pregunta": ("La composição exacta 106784 usa el carpete de nylon de 9-10 mm «sin instalación» (45560), sin "
                         "precio en ninguna UF. El ICD sí trae el mismo carpete «instalado» (10709) y carpetes más baratos. "
                         "¿Qué carpete es el ítem?"),
            "grupo": "Carpete: qué producto",
            "opciones": {
                "A": {"partes": [P("106784", 1, "carpete em manta e = 9 a 10 mm")],
                      "sin_ccd": {"106784": "falta el precio del insumo 45560 (carpete de nylon 9-10 mm sin instalación)"},
                      "cambios": {"45560": ("ICD", "10709", 0.862069, "el mismo carpete de nylon 9-10 mm con precio «instalado»: 1 m² por m² (1,16 ÷ 1,16)")},
                      "quitar": {"4791": "cola: el precio del insumo es instalado", "C:88309": "M.O.: el precio del insumo es instalado",
                                 "C:88316": "M.O.: el precio del insumo es instalado"},
                      "regla": ("106784 armada desde sus líneas con el carpete 45560 (sin precio) cambiado por el mismo carpete "
                                "de nylon 9-10 mm «instalado» (10709): 1 m²/m², sin cola ni M.O. porque el precio ya las incluye"),
                      "nota": "sube porque el carpete de nylon de tráfico pesado instalado cuesta 252,16/m² contra 37,66 estimado"},
                "B": {"partes": [P("106784", 1, "carpete em manta")],
                      "sin_ccd": {"106784": "falta el precio del insumo 45560 (carpete de nylon 9-10 mm sin instalación)"},
                      "cambios": {"45560": ("ICD", "39635", 0.862069, "carpete de polipropileno 5-6 mm, tráfico medio, precio «instalado»: 1 m² por m²")},
                      "quitar": {"4791": "cola: el precio del insumo es instalado", "C:88309": "M.O.: el precio del insumo es instalado",
                                 "C:88316": "M.O.: el precio del insumo es instalado"},
                      "regla": ("106784 con el carpete cambiado por el de polipropileno 5-6 mm de tráfico medio «instalado» "
                                "(39635): 1 m²/m², sin cola ni M.O. porque el precio ya las incluye")}},
            "etiquetas": {"A": "nylon 9-10 mm tráfico pesado (el de la composição)", "B": "polipropileno 5-6 mm tráfico medio"},
            "recomendada": "A"},
        "AC064BR": {
            "pregunta": ("La composição exacta 106783 usa el carpete de nylon de 6-7 mm «sin instalación» (45561), sin "
                         "precio en ninguna UF. El ítem es carpete agulhado en rollo (producto económico): ¿qué carpete se toma?"),
            "grupo": "Carpete: qué producto",
            "opciones": {
                "A": {"partes": [P("106783", 1, "carpete em manta e = 6 a 7 mm")],
                      "sin_ccd": {"106783": "falta el precio del insumo 45561 (carpete de nylon 6-7 mm sin instalación)"},
                      "cambios": {"45561": ("ICD", "10710", 0.862069, "el mismo carpete de nylon 6-7 mm con precio «instalado»: 1 m² por m² (1,16 ÷ 1,16)")},
                      "quitar": {"4791": "cola: el precio del insumo es instalado", "C:88309": "M.O.: el precio del insumo es instalado",
                                 "C:88316": "M.O.: el precio del insumo es instalado"},
                      "regla": ("106783 armada desde sus líneas con el carpete 45561 (sin precio) cambiado por el mismo carpete "
                                "de nylon 6-7 mm «instalado» (10710): 1 m²/m², sin cola ni M.O. porque el precio ya las incluye"),
                      "nota": "sube porque el carpete de nylon de tráfico pesado instalado cuesta 205,25/m² contra 23,85 estimado"},
                "B": {"partes": [P("106783", 1, "carpete em manta")],
                      "sin_ccd": {"106783": "falta el precio del insumo 45561 (carpete de nylon 6-7 mm sin instalación)"},
                      "cambios": {"45561": ("ICD", "10708", 0.862069, "carpete de poliéster em manta 4-5 mm, precio «instalado»: 1 m² por m²")},
                      "quitar": {"4791": "cola: el precio del insumo es instalado", "C:88309": "M.O.: el precio del insumo es instalado",
                                 "C:88316": "M.O.: el precio del insumo es instalado"},
                      "regla": ("106783 con el carpete cambiado por el de poliéster em manta 4-5 mm «instalado» (10708), el más "
                                "cercano al agulhado: 1 m²/m², sin cola ni M.O. porque el precio ya las incluye")}},
            "etiquetas": {"A": "nylon 6-7 mm tráfico pesado (el de la composição)", "B": "poliéster 4-5 mm (el más cercano al agulhado)"},
            "recomendada": "B"},
    }

    NO_CONVIENE = {
    }
    return LISTO, DECISION, NO_CONVIENE


# ── Acabados (2) e Inst. Eléctricas ──
def _tablas_acabados2():
    LISTO, DECISION, NO_CONVIENE = {}, {}, {}
    # frag_acabados2.py — fase C (Brasil), grupo «acabados2» — se ejecuta con P ya definido
    # 17 ítems: AC032 AC038 AC039 AC040 AC041 AC043 AC044 AC046 AC047 AC052 AC054 AC060 AC068 IE005 IE025 IE004 IE026

    # Grelha de ferro fundido: el SINAPI escala mortero y M.O. con el PERÍMETRO de la pieza
    # (103001 150×1000 → 103002 200×1000 → 103003 300×1000: cemento 2,377 / 2,480 / 2,687 kg y pedreiro
    #  0,2473 / 0,2575 / 0,2780 h = 1,0335 kg y 0,1075 h por metro de perímetro en las tres).
    _PERIM_20x20 = round(0.80 / 2.30, 4)      # perímetro 0,80 m (20×20) ÷ 2,30 m (150×1000) = 0,3478

    LISTO = {
        "AC032BR": {
            "partes": [P("106788", 1, "piso cimentado liso 1:3, e = 1,5 cm (m² ↔ m²)")],
            "regla": "106788 tal cual (piso cimentado liso, traço 1:3, e = 1,5 cm, con junta plástica); "
                     "el pigmento ocre (0,175 kg/m²) se omite: el SINAPI no tiene pigmento ni «pó xadrez» en el ICD",
            "nota": "baja porque la M.O. SINAPI es 0,36 h de pedreiro + 0,18 h de servente por m² (la receta traía 0,93 + 0,93 h)"},

        "AC039BR": {
            "partes": [P("89491", 1, "caixa sifonada PVC 150×185×75 mm en ramal pluvial (Pza ↔ UN)")],
            "regla": "89491 tal cual (caixa sifonada PVC DN 150 = 6″, con su grelha de PVC, en ramal pluvial); "
                     "la rejilla de bronce 6″ de la receta se omite: el SINAPI no tiene rejillas de bronce y la caixa ya trae grelha",
            "nota": "baja por la rejilla de bronce que se omite y por la M.O. SINAPI (0,34 + 0,34 h contra 1,85 + 0,88 h)"},

        "AC041BR": {
            "partes": [P("88648", 1, "rodapé cerâmico h = 7 cm cortado de placas 35×35 (m ↔ m)")],
            "regla": "88648 tal cual (rodapé cerâmico h = 7 cm, única altura del SINAPI): la pieza sale de placa esmaltada 35×35 "
                     "y se asienta con argamassa colante AC I + rejunte, igual que el piso cerámico aprobado en la fase B "
                     "(mortero de cemento y arena → colante)",
            "nota": "baja porque la M.O. SINAPI es 0,07 h de azulejista + 0,03 h de servente por metro (la receta traía 0,44 + 0,46 h) "
                    "y la receta traía 0,0098 m³ de arena por metro"},

        "AC046BR": {
            "partes": [P("98546", 1, "manta asfáltica 1 capa con primer (m² ↔ m²)")],
            "cambios": {"4015": ("ICD", "11621", 1, "manta poliéster 4 mm acabado PP → manta poliéster ALUMINIZADA 3 mm "
                                                       "(única aluminizada del SINAPI); mismo consumo 1,1319 m²/m²")},
            "regla": "98546 (manta asfáltica 1 capa + primer + gas) con la manta 4 mm PP cambiada por la aluminizada 3 mm (11621), "
                     "mismo consumo; M.O. SINAPI sin cambio (el SINAPI no publica composição de 3 mm en una capa)"},

        "AC047BR": {
            "partes": [P("98546", 1, "manta asfáltica 1 capa con primer (m² ↔ m²)")],
            "cambios": {"4015": ("ICD", "11621", round(3.5 / 3.0, 4),
                                 "manta poliéster 4 mm PP → manta poliéster aluminizada 3 mm × 3,5/3 (espesor 3,5 mm del ítem)")},
            "regla": "98546 con la manta cambiada por la aluminizada 3 mm (11621) × 3,5/3 = 1,1667 por el espesor 3,5 mm "
                     "(el SINAPI sólo tiene 3 mm aluminizada); se mantiene el primer de la composição aunque la receta no lo traía "
                     "(la manta adherida lo exige); M.O. SINAPI sin cambio",
            "nota": "baja porque la M.O. SINAPI es 0,93 h de impermeabilizador + 0,21 h de ayudante (la receta traía 2,03 + 2,03 h)"},

        "AC052BR": {
            "partes": [P("88489", 1, "pintura látex acrílica premium en paredes, 2 demãos (m² ↔ m²)")],
            "regla": "88489 tal cual (látex acrílica premium, 2 demãos, 0,2285 L/m²): el SINAPI no tiene látex acetinada, "
                     "la premium blanca es su referencia de precio más cercana; la lija suelta de la receta se omite "
                     "(el SINAPI lija dentro del emassamento, que este ítem no tiene)",
            "nota": "baja porque la M.O. SINAPI es 0,16 h de pintor + 0,05 h de servente por m² (la receta traía 0,40 + 0,42 h)"},

        "AC054BR": {
            "partes": [P("102217", 1, "tinta a óleo de acabado, 2 demãos (m² ↔ m²)"),
                       P("88485", 1, "fundo selador en pared, 1 demão: la receta trae selador para parede"),
                       P("88495", 0.144, "masilla de retoque: 0,105 kg de massa corrida de la receta ÷ 0,7288 kg/m² del emassamento")],
            "regla": "102217 (tinta a óleo 2 demãos, 0,213 L/m² + aguarrás; el SINAPI sólo la publica sobre madeira, no hay óleo "
                     "ni esmalte en pared) + 88485 (fundo selador en pared) + 88495 × 0,144 (emassamento y lijado de retoque, "
                     "por los 0,105 kg de massa de la receta)"},

        "AC060BR": {
            "partes": [P("102160", 1, "vidro impresso e = 4 mm en esquadria de madeira con baguete (m² ↔ m²)")],
            "escala": {"10499": (0.75, "espesor 3 mm ÷ 4 mm (el SINAPI sólo tiene vidro impresso de 4 mm)")},
            "regla": "102160 (vidro impresso 4 mm en madeira, con silicona y clavos sin cabeza) con el vidrio × 3/4 por el "
                     "espesor 3 mm; M.O. SINAPI sin cambio (102151 liso 3 mm y 102160 impresso 4 mm traen la misma M.O.)",
            "nota": "sube porque el vidrio impreso SINAPI vale R$ 125,41/m² en 4 mm (la receta estimaba 36,41 el de 3 mm)"},

        "IE025BR": {
            "partes": [P("97607", 1, "arandela tartaruga de sobrepor con 1 lámpara LED (Pza ↔ UN)")],
            "cambios": {"38193": ("ICD", "38194", 1, "lámpara LED 6 W → LED 10 W E27, la mayor del SINAPI (no hay 18 W)")},
            "regla": "97607 (luminária tartaruga de sobrepor para área externa, 1 lámpara E27) con la lámpara LED 6 W cambiada "
                     "por la LED 10 W (38194), la mayor E27 del SINAPI; no existe lámpara de 18 W en el ICD"},
    }

    DECISION = {
        "AC038BR": {
            "pregunta": "La rejilla de piso de BRONCE 20×20 no existe en el SINAPI (ni bronce ni latón): "
                        "¿se cambia por el ralo de ferro fundido 200×200 con requadro?",
            "grupo": "Rejilla de bronce → ferro fundido",
            "opciones": {
                "A": {"partes": [P("103001", 1, "grelha de ferro fundido asentada con argamassa 1:3 (Pza ↔ UN)",
                                   mat=_PERIM_20x20, mo=_PERIM_20x20, eq=_PERIM_20x20)],
                      "cambios": {"11235": ("ICD", "11234", 1, "grelha FoFo 150×1000 → ralo FoFo 200×200 con requadro")},
                      "fijar": {"11234": (1, "1 rejilla por pieza")},
                      "regla": "103001 (grelha FoFo 150×1000 asentada con argamassa 1:3) llevada a 20×20: mortero y M.O. × 0,3478 "
                               "= perímetro 0,80 m ÷ 2,30 m (el SINAPI los escala con el perímetro: 103001/103002/103003) "
                               "y la pieza cambiada por el ralo FoFo 200×200 con requadro (11234)"},
                "B": None},
            "etiquetas": {"A": "ralo de ferro fundido 200×200 con requadro, asentado con argamassa (SINAPI)",
                          "B": "dejar la receta actual (rejilla de bronce con precio estimado)"},
            "recomendada": "A"},

        "AC040BR": {
            "pregunta": "Rodapé de cimento: la receta trae 0,039 m³ de arena y 6,8 kg de cemento por METRO (el mortero de "
                        "≈ 1,4 m² de piso). El SINAPI no tiene rodapé de mortero: ¿se arma por geometría (h = 10 cm, e = 1,5 cm)? "
                        "¿y con qué mano de obra?",
            "grupo": "Rodapés de mortero (receta incoherente)",
            "opciones": {
                "A": {"partes": [P("106788", 0.10, "piso cimentado liso e = 1,5 cm: 0,10 m² por metro (h = 10 cm)")],
                      "quitar": {"3671": "junta plástica de dilatación: un rodapé no la lleva"},
                      "fijar": {"C:88309": (0.4387, "pedreiro: horas por metro de la receta del ítem"),
                                "C:88316": (0.4599, "servente: horas por metro de la receta del ítem")},
                      "regla": "materiales de 106788 (cimentado liso 1:3, e = 1,5 cm) × 0,10 m²/m por h = 10 cm, sin la junta "
                               "plástica; pedreiro 0,4387 h y servente 0,4599 h de la receta del ítem (el SINAPI no publica rodapé "
                               "de mortero y la M.O. del piso por m² no representa una faja de 10 cm)"},
                "B": {"partes": [P("106788", 0.10, "piso cimentado liso e = 1,5 cm: 0,10 m² por metro (h = 10 cm)")],
                      "quitar": {"3671": "junta plástica de dilatación: un rodapé no la lleva"},
                      "regla": "106788 (cimentado liso 1:3, e = 1,5 cm) × 0,10 m²/m por h = 10 cm, sin la junta plástica; "
                               "M.O. SINAPI del piso cimentado × 0,10",
                      "nota": "baja mucho: la receta traía mortero para ≈ 1,4 m² de piso por metro y 0,44 + 0,46 h de M.O.; "
                              "la M.O. del piso da 0,036 h de pedreiro por metro, poco para una faja vertical"},
                "C": None},
            "etiquetas": {"A": "mortero por geometría (h = 10 cm, e = 1,5 cm) + M.O. de la receta actual",
                          "B": "todo de 106788 × 0,10 (mortero y M.O. del piso cimentado)",
                          "C": "dejar la receta actual (todos sus precios ya son SINAPI)"},
            "recomendada": "A"},

        "AC044BR": {
            "pregunta": "Rodapé de argamassa desempenada: la receta trae 0,041 m³ de arena y 7,2 kg de cemento por METRO. "
                        "¿Se arma por geometría (h = 10 cm, e = 1,5 cm, acabado desempenado)? ¿y con qué mano de obra? "
                        "El pigmento no existe en el SINAPI y se omite.",
            "grupo": "Rodapés de mortero (receta incoherente)",
            "opciones": {
                "A": {"partes": [P("106789", 0.10, "piso cimentado rugoso (desempenado) e = 1,5 cm: 0,10 m² por metro (h = 10 cm)")],
                      "quitar": {"3671": "junta plástica de dilatación: un rodapé no la lleva"},
                      "fijar": {"C:88309": (0.4367, "pedreiro: horas por metro de la receta del ítem"),
                                "C:88316": (0.4608, "servente: horas por metro de la receta del ítem")},
                      "regla": "materiales de 106789 (cimentado 1:3 acabado rugoso = desempenado, e = 1,5 cm) × 0,10 m²/m por "
                               "h = 10 cm, sin la junta plástica ni el pigmento (no existe en el ICD); pedreiro 0,4367 h y "
                               "servente 0,4608 h de la receta del ítem"},
                "B": {"partes": [P("106789", 0.10, "piso cimentado rugoso (desempenado) e = 1,5 cm: 0,10 m² por metro (h = 10 cm)")],
                      "quitar": {"3671": "junta plástica de dilatación: un rodapé no la lleva"},
                      "regla": "106789 (cimentado 1:3 acabado rugoso = desempenado, e = 1,5 cm) × 0,10 m²/m por h = 10 cm, sin la "
                               "junta plástica ni el pigmento; M.O. SINAPI del piso cimentado × 0,10",
                      "nota": "baja mucho: la receta traía mortero para ≈ 1,5 m² de piso por metro y 0,44 + 0,46 h de M.O.; "
                              "la M.O. del piso da 0,031 h de pedreiro por metro, poco para una faja vertical"},
                "C": None},
            "etiquetas": {"A": "mortero por geometría (h = 10 cm, e = 1,5 cm) + M.O. de la receta actual, sin pigmento",
                          "B": "todo de 106789 × 0,10 (mortero y M.O. del piso cimentado), sin pigmento",
                          "C": "dejar la receta actual (pigmento con precio estimado)"},
            "recomendada": "A"},

        "AC043BR": {
            "pregunta": "Rodapé de granilite: la receta es una PIEZA premoldeada 25×10 asentada con mortero; el SINAPI tiene "
                        "el rodapé de marmorite/granilite h = 10 cm HECHO EN SITIO (101741). ¿Cuál queda?",
            "grupo": "Rodapé de granilite: en sitio o premoldeado",
            "opciones": {
                "A": {"partes": [P("101741", 1, "rodapé em marmorite (granilite) h = 10 cm moldeado en sitio (m ↔ m)")],
                      "regla": "101741 tal cual: rodapé de marmorite/granilite h = 10 cm hecho en sitio (granilha + cemento blanco, "
                               "pulido, selador y cera), precio en las 27 UF"},
                "B": {"partes": [P("101740", 1, "rodapé de piedra h = 10 cm asentado con argamassa + colante (m ↔ m)")],
                      "cambios": {"10857": ("ICD", "34680", 1, "rodapé de ardósia 10 cm → rodapé premoldeado de granilite L = 10 cm; "
                                                                  "mismo consumo 1,04 m/m")},
                      "regla": "101740 (rodapé de ardósia h = 10 cm, asentado con argamassa y colante) con la pieza cambiada por el "
                               "rodapé premoldeado de granilite L = 10 cm (34680, con precio sólo en 2 UF); M.O. SINAPI sin cambio",
                      "nota": "sube porque la pieza SINAPI vale R$ 44,95/m (la receta la estimaba en 9,42) y la M.O. es 0,63 + 0,63 h"}},
            "etiquetas": {"A": "hecho en sitio, composição SINAPI 101741 sin adaptar",
                          "B": "pieza premoldeada (insumo 34680) asentada como el rodapé de ardósia 101740"},
            "recomendada": "A"},

        "AC068BR": {
            "pregunta": "Revestimiento cerámico externo: la composição de fachada (104588) usa cerámica de fachada 7×26 a "
                        "R$ 144/m²; la receta trae el «ladrilho esmaltado 11×23» con precio de piso esmaltado (R$ 29,62/m²). "
                        "¿Qué cerámica queda?",
            "grupo": "Cerámica de fachada",
            "opciones": {
                "A": {"partes": [P("104588", 1, "revestimiento cerámico de paredes externas, piezas ≤ 200 cm², a prumo (m² ↔ m²)"),
                                 P("87775", 1, "emboço de fachada e = 25 mm: reemplaza el lecho de mortero de la receta (0,039 m³ de arena)"),
                                 P("87905", 1, "chapisco de fachada, base del emboço")],
                      "regla": "104588 (cerámica de fachada con colante AC III + rejunte) + 87775 (emboço 25 mm) + 87905 (chapisco): "
                               "el lecho de mortero de la receta pasa a base + colante, como el piso cerámico de la fase B; "
                               "pieza 11×23 (253 cm²) ≈ pieza SINAPI 7×26 (≤ 200 cm²)"},
                "B": {"partes": [P("104588", 1, "revestimiento cerámico de paredes externas, piezas ≤ 200 cm², a prumo (m² ↔ m²)"),
                                 P("87775", 1, "emboço de fachada e = 25 mm: reemplaza el lecho de mortero de la receta (0,039 m³ de arena)"),
                                 P("87905", 1, "chapisco de fachada, base del emboço")],
                      "cambios": {"44955": ("ICD", "1287", 1, "cerámica de fachada 7×26 → cerámica esmaltada de la receta (1287); "
                                                                "mismo consumo 1,05 m²/m²")},
                      "regla": "igual que A pero con la cerámica de fachada cambiada por la esmaltada 1287 que ya usa la receta "
                               "(mismo consumo 1,05 m²/m²)"}},
            "etiquetas": {"A": "cerámica de fachada SINAPI 7×26 (R$ 144/m²)",
                          "B": "cerámica esmaltada de la receta, insumo 1287 (R$ 29,62/m²)"},
            "recomendada": "A"},

        "IE004BR": {
            "pregunta": "Luminaria calha 2×20 W LED: la composição exacta 100910 no tiene costo porque su luminaria (43992) no "
                        "tiene precio en ninguna UF. ¿Se pone la luminaria de sobreponer de chapa de acero para 2 lámparas (38784)?",
            "grupo": "Luminarias sin precio SINAPI",
            "opciones": {
                "A": {"partes": [P("100910", 1, "luminária calha de sobrepor con 2 lámparas tubulares LED 18/20 W (Pza ↔ UN)")],
                      "sin_ccd": {"100910": "la luminaria 43992 no está en el ICD 08/2026"},
                      "cambios": {"43992": ("ICD", "38784", 1, "cuerpo de la calha → luminária de sobrepor de chapa de aço para "
                                                                 "2 lámparas (38784), la más cercana con precio")},
                      "regla": "100910 armada desde sus líneas (M.O. + 2 lámparas tubulares LED 18/20 W) con la luminaria sin precio "
                               "cambiada por la de sobrepor de chapa de aço para 2 lámparas (38784, base E27)"},
                "B": None},
            "etiquetas": {"A": "100910 con el cuerpo 38784 (chapa de aço, 2 lámparas) + 2 tubos LED 18/20 W",
                          "B": "dejar la receta actual (luminaria con precio estimado)"},
            "recomendada": "A"},

        "IE005BR": {
            "pregunta": "Spot de embutir 16 W LED: la composição 105546 no tiene costo (ni el spot de embutir 45218 ni la lámpara "
                        "PAR20 tienen precio). El SINAPI no tiene ningún spot de embutir con precio: ¿qué luminaria lo reemplaza?",
            "grupo": "Luminarias sin precio SINAPI",
            "opciones": {
                "A": {"partes": [P("105546", 1, "spot de embutir con 1 lámpara: M.O. de la composição (Pza ↔ UN)")],
                      "sin_ccd": {"105546": "el spot 45218 y la lámpara PAR20 45183 no están en el ICD 08/2026"},
                      "cambios": {"45218": ("ICD", "12266", 1, "spot de embutir → spot de SOBREPONER de aluminio para 1 lámpara E27"),
                                  "45183": ("ICD", "38194", 1, "lámpara PAR20 6/7 W → LED 10 W E27, la mayor del SINAPI")},
                      "regla": "105546 armada desde sus líneas: M.O. SINAPI + spot de sobrepor de aluminio (12266) + lámpara LED 10 W "
                               "(38194) en lugar del spot de embutir y la PAR20 sin precio"},
                "B": {"partes": [P("105546", 1, "spot de embutir con 1 lámpara: M.O. de la composição (Pza ↔ UN)")],
                      "sin_ccd": {"105546": "el spot 45218 y la lámpara PAR20 45183 no están en el ICD 08/2026"},
                      "cambios": {"45218": ("ICD", "39385", 1, "spot de embutir → luminária LED plafon redondo 12/13 W (LED integrado)")},
                      "quitar": {"45183": "la luminaria LED integrada no lleva lámpara"},
                      "regla": "105546 armada desde sus líneas: M.O. SINAPI + luminária LED plafon redondo 12/13 W (39385, LED "
                               "integrado, de sobrepor) en lugar del spot de embutir; sin lámpara",
                      "nota": "baja porque la luminaria LED del SINAPI vale R$ 9,10 (la receta estimaba 50,22) y la M.O. es 0,54 + 0,17 h"},
                "C": None},
            "etiquetas": {"A": "spot de sobrepor de aluminio (R$ 82,53) + lámpara LED 10 W",
                          "B": "luminaria LED integrada 12/13 W tipo plafon (R$ 9,10)",
                          "C": "dejar la receta actual (luminaria con precio estimado)"},
            "recomendada": "B"},

        "IE026BR": {
            "pregunta": "Painel LED 24 W de sobrepor: la composição exacta 103785 no tiene costo (la luminaria 44795 no tiene "
                        "precio). La única luminaria LED de sobrepor con precio es el plafon redondo de 12/13 W: ¿se usa?",
            "grupo": "Luminarias sin precio SINAPI",
            "opciones": {
                "A": {"partes": [P("103785", 1, "plafon cuadrado de sobrepor LED 24 W: M.O. de la composição (Pza ↔ UN)")],
                      "sin_ccd": {"103785": "la luminaria 44795 no está en el ICD 08/2026"},
                      "cambios": {"44795": ("ICD", "39385", 1, "painel cuadrado 30×30 de 24 W → luminária LED plafon redondo "
                                                                 "12/13 W, la única LED de sobrepor con precio")},
                      "regla": "103785 armada desde sus líneas: M.O. SINAPI + luminária LED plafon redondo de sobrepor 12/13 W (39385) "
                               "en lugar del painel 30×30 de 24 W sin precio",
                      "nota": "baja porque la luminaria LED del SINAPI vale R$ 9,10 (la receta estimaba 37,66) y la M.O. es 0,61 + 0,19 h"},
                "B": None},
            "etiquetas": {"A": "103785 con la luminaria LED redonda 12/13 W (R$ 9,10)",
                          "B": "dejar la receta actual (luminaria con precio estimado)"},
            "recomendada": "A"},
    }

    NO_CONVIENE = {}
    return LISTO, DECISION, NO_CONVIENE


# ── Carpintería ──
def _tablas_carpinteria():
    LISTO, DECISION, NO_CONVIENE = {}, {}, {}
    # frag_carpinteria.py — fase C, grupo «carpinteria» (18 ítems). Se ejecuta con P ya definido.
    # Barniz de puerta (regla aprobada en la fase B): 2 caras + marco (perímetro × 0,14 m).
    #   1,00 × 2,10 → 2 × 2,10 m² + 5,2 m × 0,14 = 4,93 m²;  0,90 × 2,10 → 4,51 m²;  0,80 × 2,10 → 4,06 m².
    # M.O. de colgar la hoja según el ancho (SINAPI la escala en línea recta):
    #   semi-oca leve/média 90820/90822/90823 (60/80/90 cm): carpinteiro 1,85898 / 2,24198 / 2,43348 h → +0,1915 h cada 10 cm;
    #     servente 0,525363 / 0,633602 / 0,687722 h → +0,05412 h cada 10 cm.
    #   pesada/maciça 90824/90825 (80/90 cm): carpinteiro 3,1114 / 3,37716 h → +0,26576 h cada 10 cm;
    #     servente 0,879308 / 0,954414 h → +0,075106 h cada 10 cm.

    _VERNIZ_100 = "verniz 2 demãos: 2 caras × 1,00 × 2,10 = 4,20 m² + batente (5,2 m × 0,14 m = 0,73) = 4,93 m²"
    _VERNIZ_90 = "verniz 2 demãos: 2 caras × 0,90 × 2,10 = 3,78 m² + batente (5,1 m × 0,14 m = 0,73) = 4,51 m²"
    _VERNIZ_80 = "verniz 2 demãos: 2 caras × 0,80 × 2,10 = 3,36 m² + batente (5,0 m × 0,14 m = 0,70) = 4,06 m²"

    # Mesón de hormigón armado, por partes (por m² de mesón): losa e = 5 cm + pilares de ladrillo
    _MESON_BASE = [
        P("94965", 0.05515, "concreto fck 25 feito em obra: losa e = 5 cm → 0,05 m³/m² × 1,103"),
        P("103670", 0.05, "lançamento com baldes, adensamento e acabamento: 0,05 m³/m²"),
        P("92769", 2.56, "armação de laje CA-50 6,3 mm: 2,56 kg/m² de la receta"),
        P("92271", 1, "fôrma de laje em madeira serrada (la receta trae madera): 1 m² de fondo por m² de mesón"),
        P("101159", 0.80, "apoyos de ladrillo: 41 ladrillos 25×12×6,5 de la receta ÷ 51,28 pzas/m² (junta 1 cm) = 0,80 m² de muro"),
    ]

    LISTO = {
        "CR003BR": {
            "partes": [P("102188", 1, "mola hidráulica para porta (Pza = UN); el SINAPI sólo publica la de piso")],
            "cambios": {"11499": ("ICD", "43604", 1,
                                  "mola aérea (brazo) para portas de até 850 mm / 50 kg, que es lo que trae la receta ArqOn, en vez de la mola de piso")},
            "regla": "102188 (mola de piso) con el insumo cambiado por la mola hidráulica aérea 43604 (puerta de baño ≤ 85 cm, 50 kg); M.O. SINAPI de 102188 sin cambio (el SINAPI no publica la colocación de la mola aérea)",
            "nota": "baja porque la mola aérea SINAPI cuesta 129,33 contra 250 estimado"},
        "CR008BR": {
            "partes": [P("100667", 1, "janela de madeira cedro/imbuia, folhas de abrir, marco 10 cm, con guarnição y ferragens, vidrio no incluido")],
            "regla": "100667 tal cual por m²: es la única ventana de abrir de cedro del SINAPI (2 hojas venezianas + 2 guilhotinas para vidrio); incluye marco, guarnición y herrajes; el vidrio no entra (igual que en ArqOn)",
            "nota": "sube porque la ventana de cedro SINAPI cuesta 891,67/m² contra 232 estimado"},
        "CR010BR": {
            "partes": [P("102182", 0.5291, "porta de vidro temperado 10 mm de 90×210 (UN) → 1 ÷ 1,89 m² = 0,5291 UN/m²")],
            "extras": [("ICD", "11552", 1.96, "perfil U de alumínio: 1,96 m/m² de la receta")],
            "regla": "102182 (hoja 90×210 = 1,89 m², vidrio 10 mm + juego de herrajes) convertida a m²: × 1/1,89; se agrega el perfil U de aluminio de la receta (1,96 m/m²)"},
        "CR013BR": {
            "partes": [P("99861", 1, "gradil em aço fixado em vãos de janelas, con requadro de cantoneira")],
            "extras": [("BR", "br_pintura_anticorrosiva_l", 0.1755, "tinta anticorrosiva de la receta: 0,1755 L/m²")],
            "regla": "99861 tal cual por m² (reja de ventana con marco de cantoneira; barras chatas 25×4,8 en vez del tubo 20×20, que no está en el ICD) + la pintura anticorrosiva de la receta",
            "nota": "sube por la M.O. SINAPI (7,5 h serralheiro + 5,4 h auxiliar por m² contra 2,6 + 3,1 h de la receta)"},
        "CR014BR": {
            "partes": [P("94570", 1, "janela de alumínio de correr para vidro, vidrio 4 mm incluido, por m²")],
            "regla": "94570 tal cual por m² (corrediza de aluminio con vidrio 4 mm incluido); el SINAPI publica 2 y 4 hojas, no 3: se toma la de 2 hojas sin bandeira",
            "nota": "baja porque la ventana SINAPI ya trae el vidrio y cuesta 413,14 la pieza de 1,20 m²"},
        "CR020BR": {
            "partes": [P("106221", 1, "guarda-corpo de aço h = 0,65 m: se toma la M.O. de serralheiro por metro")],
            "quitar": {"21012": "tubos galvanizados: el protector es de barras lisas", "21011": "idem", "21009": "idem",
                       "44184": "la receta no trae chumbador", "156": "la receta no trae adhesivo epoxi"},
            "fijar": {"11002": (0.2438, "electrodos de la receta: 0,2438 kg/m")},
            "extras": [("BR", "br_fierro_liso_3_8_10mm_l_12m_barra", 0.6808, "barra lisa CA-25 10 mm de la receta (0,6808 barra = 5,04 kg/m)"),
                       ("BR", "br_fierro_liso_1_4_6mm_barra", 0.2924, "barra lisa CA-25 6,3 mm de la receta (0,2924 barra = 0,86 kg/m)"),
                       ("BR", "br_pintura_sintetica_color_azul_gal", 0.0689, "esmalte sintético de la receta")],
            "regla": "M.O. de 106221 (guarda-corpo de aço h 0,65 m, 1,05 h serralheiro + 0,75 h auxiliar por m) con el acero de la receta: barras lisas CA-25 10 mm (5,04 kg/m) y 6,3 mm (0,86 kg/m), electrodos y esmalte; se omiten dobladora y camión (menores)"},
    }

    DECISION = {
        "CA001BR": {
            "pregunta": "«Porta» genérica por pieza, sin medida ni tipo (la receta es sólo madera bruta y clavos): ¿hoja sola o puerta completa?",
            "grupo": "Pieza tipo: puerta/ventana sin medida",
            "opciones": {
                "A": {"partes": [P("90822", 1, "hoja semi-oca 80×210 para pintura con bisagras, colocada (Pza = UN)")],
                      "regla": "90822: hoja 80×210 con bisagras, sin marco ni cerradura (mismo alcance que la receta ArqOn: sólo la hoja)"},
                "B": {"partes": [P("90843", 1, "kit 80×210: hoja semi-oca + batente + alizar + fechadura (Pza = UN)")],
                      "regla": "90843: kit completo 80×210 (hoja, marco, guarnición, bisagras y cerradura)",
                      "nota": "sube porque agrega marco, guarnición y cerradura, que la receta ArqOn no trae"}},
            "etiquetas": {"A": "sólo la hoja 80×210 con bisagras", "B": "puerta completa 80×210 (kit con marco y cerradura)"},
            "recomendada": "A"},
        "CA002BR": {
            "pregunta": "«Janela» genérica por pieza, sin medida: ¿qué tamaño de ventana de madera se toma?",
            "grupo": "Pieza tipo: puerta/ventana sin medida",
            "opciones": {
                "A": {"partes": [P("100666", 1.20, "janela de madeira pinus/eucalipto (m²) × ventana tipo 1,00 × 1,20 m = 1,20 m²")],
                      "regla": "100666 (ventana de madera económica, de abrir, vidrio no incluido) × 1,20 m² (pieza tipo 1,00 × 1,20)",
                      "nota": "sube porque la receta ArqOn era sólo madera bruta y clavos; la ventana SINAPI viene hecha con marco, guarnición y herrajes"},
                "B": {"partes": [P("100666", 1.00, "janela de madeira pinus/eucalipto (m²) × ventana 1,00 × 1,00 m (parámetros por defecto del ítem)")],
                      "regla": "100666 × 1,00 m² (pieza 1,00 × 1,00, los parámetros por defecto del ítem)",
                      "nota": "sube porque la receta ArqOn era sólo madera bruta y clavos; la ventana SINAPI viene hecha con marco, guarnición y herrajes"}},
            "etiquetas": {"A": "ventana tipo 1,00 × 1,20 m", "B": "ventana 1,00 × 1,00 m"},
            "recomendada": "A"},
        "CR001BR": {
            "pregunta": "«Retirada de porta - janela» por pieza: el SINAPI la mide por m² y separa puerta de ventana. ¿Qué pieza tipo se toma?",
            "grupo": "Pieza tipo: puerta/ventana sin medida",
            "opciones": {
                "A": {"partes": [P("97644", 1.68, "remoção de portas (m²) × puerta 0,80 × 2,10 = 1,68 m²")],
                      "regla": "97644 (remoção de portas, manual) × 1,68 m² (puerta 0,80 × 2,10)",
                      "nota": "baja porque el SINAPI da 0,42 h/m² (0,70 h por puerta) contra 1,66 h de la receta"},
                "B": {"partes": [P("97645", 1.20, "remoção de janelas (m²) × ventana 1,00 × 1,20 = 1,20 m²")],
                      "regla": "97645 (remoção de janelas, manual) × 1,20 m² (ventana 1,00 × 1,20)"}},
            "etiquetas": {"A": "puerta 0,80 × 2,10 (97644)", "B": "ventana 1,00 × 1,20 (97645)"},
            "recomendada": "A"},
        "CR005BR": {
            "pregunta": "Puerta almofadada de 1,00 × 2,10: el kit SINAPI de puerta maciza llega a 0,80. ¿Se lleva a 1,00 m o se deja el kit de 0,80?",
            "grupo": "Puerta de 1,00 m",
            "opciones": {
                "A": {"partes": [P("100693", 1, "kit porta maciça tipo mexicana (almofadada) 80×210 con fechadura, dobradiças y batente"),
                                 P("102214", 4.93, _VERNIZ_100)],
                      "escala": {"4998": (1.25, "hoja maciza (insumo por m²): 1,00 × 2,10 = 2,10 m² en vez de 1,68 m²"),
                                 "20017": (1.04, "alizar: 2 × (2 × 2,10 + 1,00) = 10,4 m en vez de 10,0 m")},
                      "fijar": {"C:88261": (10.41552, "carpinteiro: 9,884 h del kit + 2 × 0,26576 h (hoja pesada, +0,26576 h cada 10 cm: 90824 vs 90825)"),
                                "C:88316": (3.690802, "servente: 3,54059 h del kit + 2 × 0,075106 h (idem)")},
                      "regla": "100693 (80×210) llevado a 1,00 m: hoja maciza 4998 × 2,10/1,68 (insumo por m²), alizar × 1,04, M.O. de la hoja extrapolada con la relación SINAPI 90824→90825; el batente 183 sirve de 60 a 120 cm; + verniz 102214 × 4,93 m²"},
                "B": {"partes": [P("100693", 1, "kit porta maciça tipo mexicana (almofadada) 80×210 con fechadura, dobradiças y batente"),
                                 P("102214", 4.06, _VERNIZ_80)],
                      "regla": "100693 tal cual (80×210) + verniz 102214 × 4,06 m²: igual que CR004BR (0,80 × 2,10)"}},
            "etiquetas": {"A": "kit llevado a 1,00 m (hoja por m², M.O. extrapolada)", "B": "kit SINAPI 0,80 × 2,10 sin tocar (= CR004BR)"},
            "recomendada": "A"},
        "CR006BR": {
            "pregunta": "Puerta externa moldurada de 1,00 × 2,10: el SINAPI tiene hoja de HDF de 1,00 m sólo en folha média; la folha pesada (núcleo sólido) llega a 0,90. ¿Cuál se toma?",
            "grupo": "Puerta de 1,00 m",
            "opciones": {
                "A": {"partes": [P("100685", 1, "kit porta para verniz semi-oca média 90×210 con fechadura externa, dobradiças y batente"),
                                 P("102213", 4.93, _VERNIZ_100 + " (verniz de uso interno e externo: la puerta es exterior)")],
                      "cambios": {"4987": ("ICD", "4989", 1, "la misma hoja (folha média, capa de HDF, para verniz) en 1000 × 2100 mm")},
                      "escala": {"20017": (1.0196, "alizar: 10,4 m en vez de 10,2 m")},
                      "fijar": {"C:88261": (9.41169, "carpinteiro: 9,22019 h del kit + 0,1915 h (hoja média, +0,1915 h cada 10 cm: 90820/90822/90823)"),
                                "C:88316": (3.40711, "servente: 3,35299 h del kit + 0,05412 h (idem)")},
                      "regla": "100685 (90×210, con fechadura externa) con la hoja cambiada por la de 1000×2100 del mismo producto (ICD 4989), alizar × 1,02 y M.O. de la hoja extrapolada con la relación SINAPI 60/80/90 cm; + verniz exterior 102213 × 4,93 m²"},
                "B": {"partes": [P("90846", 1, "kit porta maciça/pesada 90×210 (núcleo sólido) con fechadura externa, dobradiças y batente"),
                                 P("102213", 4.51, _VERNIZ_90 + " (verniz de uso interno e externo)")],
                      "regla": "90846 tal cual (hoja pesada de núcleo sólido 90×210, con fechadura externa) + verniz exterior 102213 × 4,51 m²; queda en 0,90 m de ancho"}},
            "etiquetas": {"A": "hoja de HDF 1,00 m, folha média", "B": "hoja pesada núcleo sólido, 0,90 m"},
            "recomendada": "A"},
        "CA003BR": {
            "pregunta": "«Guarda-corpo metálico» por metro, sin altura ni tipo (la receta es varilla CA-50 soldada, 5,15 kg/m, con madera): ¿qué baranda SINAPI se toma?",
            "grupo": "Barandas y portones metálicos",
            "opciones": {
                "A": {"partes": [P("106221", 1, "guarda-corpo de aço galvanizado h = 0,65 m sobre antepecho de albañilería, tubos 1 1/2, 1 1/4 y 3/4 pulg.")],
                      "regla": "106221 tal cual: baranda de tubo galvanizado de 0,65 m que completa un antepecho (8,7 kg/m de tubo; es la más liviana del SINAPI y la más parecida en peso y M.O. a la receta)"},
                "B": {"partes": [P("99844", 1, "guarda-corpo de aço galvanizado h = 1,10 m, montantes 1 1/2 pulg., travessa 2 pulg., barras chatas 32×4,8")],
                      "regla": "99844 tal cual: baranda completa de 1,10 m (altura de norma), la más económica de las de 1,10 m con costo en SP",
                      "nota": "sube porque es una baranda de 1,10 m con 18 kg/m de acero galvanizado y 4,3 h de serralheiro, contra 5,15 kg/m de varilla de la receta"},
                "C": {"partes": [P("106221", 1, "guarda-corpo de aço h = 0,65 m: se toma la M.O. de serralheiro y la fijación por metro")],
                      "quitar": {"21012": "tubos galvanizados: la receta es de varilla", "21011": "idem", "21009": "idem"},
                      "extras": [("BR", "br_fierro_corrugado_kg", 5.1478, "varilla CA-50 de la receta: 5,1478 kg/m"),
                                 ("BR", "br_madera_de_construccion_p2", 2.0555, "madera de la receta (pasamanos): 2,0555 p2/m")],
                      "regla": "M.O. y fijación de 106221 con el acero de la receta (5,15 kg/m de varilla CA-50 soldada) y su madera, en lugar de los tubos galvanizados"}},
            "etiquetas": {"A": "tubo galvanizado h 0,65 m sobre antepecho (106221)", "B": "tubo galvanizado h 1,10 m completa (99844)",
                          "C": "varilla CA-50 de la receta + M.O. SINAPI"},
            "recomendada": "B"},
        "CR011BR": {
            "pregunta": "Puerta de chapa metálica por m²: el SINAPI no tiene puerta de chapa lisa hecha en obra. ¿Cuál la reemplaza?",
            "grupo": "Puertas y ventanas metálicas: tipología",
            "opciones": {
                "A": {"partes": [P("100701", 1, "porta de ferro de abrir tipo grade com chapa, com guarnições, por m²")],
                      "regla": "100701 tal cual por m²: puerta de hierro de abrir con chapa, provista completa con requadro y guarnición, colocada con argamassa"},
                "B": {"partes": [P("94807", 0.5291, "porta em aço de abrir tipo veneziana 90×210 (UN) → 1 ÷ 1,89 m² = 0,5291 UN/m²")],
                      "regla": "94807 (puerta de acero tipo veneziana 90×210, con cerradura) convertida a m²: × 1/1,89"}},
            "etiquetas": {"A": "porta de ferro com chapa, por m² (100701)", "B": "porta de aço veneziana 90×210 (94807)"},
            "recomendada": "A"},
        "CR012BR": {
            "pregunta": "Portón de garaje de chapa 3,0 × 2,4 por m²: el SINAPI no tiene composição de portón de chapa; sí insumos de portón basculante y corredizo. ¿Cuál se toma?",
            "grupo": "Puertas y ventanas metálicas: tipología",
            "opciones": {
                "A": {"partes": [P("100701", 1, "porta de ferro de abrir tipo grade com chapa, por m² (la receta ArqOn es de abrir: bisagras y picaportes)")],
                      "regla": "100701 tal cual por m² (hoja de hierro de abrir con chapa); queda con la misma receta que CR011BR"},
                "B": {"partes": [P("100701", 1, "colocación de la hoja de hierro por m²")],
                      "cambios": {"4930": ("ICD", "37563", 1, "portão basculante em aço galvanizado, chapa 26, com requadro (m² por m²)")},
                      "regla": "100701 con la hoja cambiada por el portón basculante de chapa (ICD 37563), m² por m²; M.O. y argamassa de 100701"},
                "C": {"partes": [P("100701", 1, "colocación de la hoja de hierro por m²")],
                      "cambios": {"4930": ("ICD", "37561", 1, "portão de correr em chapa tipo painel lambril, com trilhos e roldanas (m² por m²)")},
                      "regla": "100701 con la hoja cambiada por el portón corredizo de chapa (ICD 37561, con rieles y roldanas), m² por m²; M.O. y argamassa de 100701"}},
            "etiquetas": {"A": "de abrir, hierro con chapa (= CR011BR)", "B": "basculante de chapa", "C": "corredizo de chapa"},
            "recomendada": "A"},
        "CR015BR": {
            "pregunta": "Ventana metálica de cantoneira y perfil T (de abrir, hecha en obra): el SINAPI tiene de acero la basculante y la corrediza. ¿Cuál se toma?",
            "grupo": "Puertas y ventanas metálicas: tipología",
            "opciones": {
                "A": {"partes": [P("94559", 1, "janela de aço tipo basculante para vidros, com batente y ferragens, pintura anticorrosiva, vidrio no incluido, por m²")],
                      "regla": "94559 tal cual por m²: ventana de acero basculante (cantoneira y perfil T, como la receta), vidrio no incluido; el SINAPI la calcula con piezas de 60×60",
                      "nota": "sube por la M.O. de colocación SINAPI (5,1 h pedreiro + 2,8 h servente por m², piezas chicas de 60×60)"},
                "B": {"partes": [P("94562", 1, "janela de aço de correr 4 folhas para vidro, com batente y ferragens, pintura anticorrosiva, vidrio no incluido, por m²")],
                      "regla": "94562 tal cual por m²: ventana de acero corrediza de 4 hojas, vidrio no incluido"}},
            "etiquetas": {"A": "basculante de acero (94559)", "B": "corrediza de acero 4 hojas (94562)"},
            "recomendada": "A"},
        "CR016BR": {
            "pregunta": "Mesón de hormigón armado con azulejo: el SINAPI no lo tiene; se puede armar por partes, pero el espesor de la losa no está en el ítem (la receta cierra con 5 cm). ¿Se arma así?",
            "grupo": "Mesón de hormigón armado",
            "opciones": {
                "A": {"partes": _MESON_BASE + [P("87265", 1, "revestimento cerâmico esmaltado 20×20 con argamassa colante y rejunte: 1 m²/m²")],
                      "regla": "por partes: losa e = 5 cm (94965 × 0,05515 + 103670 × 0,05), acero 2,56 kg/m² (92769), fôrma 1 m² (92271), apoyos de ladrillo 0,80 m² (101159, tijolo maciço 5×10×20) y azulejo 87265 × 1 m²"},
                "B": None},
            "etiquetas": {"A": "por partes, losa de 5 cm", "B": "dejar la receta actual"},
            "recomendada": "A"},
        "CR017BR": {
            "pregunta": "Mesón de hormigón armado revestido en mármol: ¿se arma por partes (losa + apoyos + mármol) o se toma la bancada de mármol SINAPI, que no lleva hormigón?",
            "grupo": "Mesón de hormigón armado",
            "opciones": {
                "A": {"partes": _MESON_BASE + [P("98672", 1, "mármore branco polido e = 2 cm asentado (piso em mármore): 1 m²/m²")],
                      "regla": "por partes: losa e = 5 cm (94965 × 0,05515 + 103670 × 0,05), acero 2,56 kg/m² (92769), fôrma 1 m² (92271), apoyos de ladrillo 0,80 m² (101159) y mármol 98672 × 1 m²; la faixa decorativa no tiene insumo SINAPI (se omite)"},
                "B": {"partes": [P("86893", 1.1111, "bancada de mármore branco 1,50 × 0,60 m (UN) → 1 ÷ 0,90 m² = 1,1111 UN/m²")],
                      "regla": "86893 (tampo de mármol de 3 cm sobre mão-francesa, 1,50 × 0,60 = 0,90 m²) convertida a m²: × 1/0,90; sin losa ni apoyos de ladrillo"}},
            "etiquetas": {"A": "por partes: losa 5 cm + apoyos + mármol", "B": "bancada de mármol SINAPI (sin hormigón)"},
            "recomendada": "A"},
        "CR018BR": {
            "pregunta": "Portón con malla: la composição exacta (106463) no tiene costo porque su portón de fábrica (45553) no está en el ICD. ¿Se arma con tubo y malla como el alambrado, o se cambia por el portón de gradil?",
            "grupo": "Barandas y portones metálicos",
            "opciones": {
                "A": {"partes": [P("102363", 1, "alambrado de tubos de aço galvanizado con tela fio 12 BWG, por m² (misma construcción que el portón)")],
                      "quitar": {"4721": "base de concreto de los postes: el portón no la lleva", "1379": "idem", "370": "idem",
                                 "C:88831": "idem (betoneira)", "C:88830": "idem (betoneira)", "C:88377": "idem (operador de betoneira)",
                                 "7698": "la receta arma el bastidor sólo con tubo de 2 pulg."},
                      "cambios": {"7158": ("ICD", "10927", 1, "tela fio 12 BWG malha 8×8 cm: la más cercana a la 7×7 #12 de la receta (m² por m²)")},
                      "fijar": {"7696": (2.5739, "tubo galvanizado 2 pulg. de la receta: 2,5739 m/m²"),
                                "11002": (0.6802, "electrodos de la receta: 0,6802 kg/m²"),
                                "43130": (0.3067, "arame galvanizado de la receta: 0,3067 kg/m²")},
                      "extras": [("ICD", "2432", 1.5, "bisagras: 1,47/m² de la receta → 3 por hoja de 2 m² = 1,5/m²")],
                      "regla": "102363 (alambrado de tubo galvanizado y tela #12) sin la base de concreto, con el tubo de 2 pulg. (2,57 m/m²), alambre y electrodos de la receta, tela 8×8 #12 (la 7×7 no existe) y 1,5 bisagras/m²; M.O. SINAPI del alambrado; tubo galvanizado, sin pintura",
                      "nota": "baja por la M.O.: 0,75 h serralheiro + 0,39 h servente SINAPI contra 7,0 + 5,5 h de la receta"},
                "B": {"partes": [P("106463", 1, "portão de abrir estruturado por tubos galvanizados com tela, completo (composição exacta)")],
                      "sin_ccd": {"106463": "el insumo 45553 (portão de abrir para alambrados) no está en el ICD 08/2026"},
                      "cambios": {"45553": ("ICD", "4948", 1.89, "portão de abrir em gradil de metalon com requadro, completo (m²): la pieza 45553 es de 1,89 m²")},
                      "regla": "106463 armada desde sus líneas, con el portón de fábrica 45553 (sin precio) cambiado por el portón de abrir de gradil de metalon 4948 (m²) × 1,89: deja de ser de malla"}},
            "etiquetas": {"A": "tubo 2 pulg. + malla, como el alambrado (102363)", "B": "portón de gradil de metalon (106463 con 4948)"},
            "recomendada": "A"},
    }

    NO_CONVIENE = {
    }

    # ── Revisión del coordinador ──
    # CR005BR y CR006BR: la puerta de 1,00 m NO cambia lo que el ítem es: el SINAPI tiene la hoja en la medida (4998 por m²,
    # 4989 de 1000 × 2100), el batente 183 cubre de 60 a 120 cm y la M.O. sigue la relación que el propio SINAPI publica entre
    # sus kits de 60/80/90 cm. La opción A pasa a LISTO; la otra opción (kit de 0,80 / 0,90 sin tocar) se descarta.
    for _c in ("CR005BR", "CR006BR"):
        LISTO[_c] = DECISION.pop(_c)["opciones"]["A"]
    LISTO["CR005BR"]["nota"] = "sube por el kit SINAPI de puerta maciza almofadada (hoja 4998 a R$ 584/m²) y el barniz de las dos caras y el marco"
    return LISTO, DECISION, NO_CONVIENE


# ── Cubiertas ──
def _tablas_cubiertas():
    LISTO, DECISION, NO_CONVIENE = {}, {}, {}
    # frag_cubiertas.py — fase C (Brasil), grupo «cubiertas». Se ejecuta con P ya definido.
    # Antecedentes de la fase B que se respetan: telhamento SINAPI + trama; calamina N.º 28 = aço zincado 0,5 mm
    # (telha ondulada 25007 en lugar de la trapezoidal 7243); lona de polietileno de la receta como insumo 3777 (CU011BR).

    LISTO = {
        "CU012BR": {
            "partes": [P("94195", 1, "telhamento con telha cerâmica de encaixe (insumo 7175, 16 telhas/m²)"),
                       P("92539", 1, "trama de madeira: ripas, caibros e terças para telha cerâmica")],
            "extras": [("ICD", "3777", 1.132, "lona de polietileno bajo la teja: 1,132 m²/m² de la receta del ítem (igual que CU011BR)")],
            "regla": "94195 (telha de encaixe tipo portuguesa, insumo 7175 que cubre romana/americana/portuguesa/francesa, 16 telhas/m²) "
                     "tomada como teja española: la receta ArqOn traía 15,4 pza/m², mismo rendimiento; + trama de madeira 92539 "
                     "+ lona 3777 de la receta (1,132 m²). Cantidad de tejas y M.O. SINAPI sin cambio",
            "nota": "baja porque la receta ArqOn traía 6,7 h de mano de obra y la teja a precio estimado; SINAPI: 1,58 h entre telhado y trama"},

        "CU014BR": {
            "partes": [P("94216", 1, "telhamento con telha metálica termoacústica")],
            "cambios": {"40740": ("ICD", "39522", 1, "telha termoisolante núcleo EPS 50 mm, dos caras trapezoidales de aço 0,5 mm, m² por m²")},
            "regla": "94216 (termoacústica PU 30 mm) con la telha cambiada por la de núcleo EPS 50 mm (insumo 39522, dos caras "
                     "trapezoidales como la 40740): 1,1457 m²/m² del SINAPI; fijación y M.O. SINAPI sin cambio (el SINAPI publica un "
                     "solo espesor). La receta ArqOn traía la teja en m: queda en m²",
            "nota": "la 39521 (cara inferior plana, EPS 50 mm) cuesta 5,37 R$/m² menos; sin estructura, igual que la receta ArqOn"},

        "CU016BR": {
            "partes": [P("94216", 1, "telhamento con telha metálica termoacústica")],
            "cambios": {"40740": ("ICD", "43071", 1, "telha termoisolante núcleo PIR 50 mm (espuma rígida de la familia del poliuretano), m² por m²")},
            "regla": "94216 (termoacústica PU 30 mm) con la telha cambiada por la de 50 mm que publica el SINAPI: insumo 43071, "
                     "núcleo de poliisocianurato (PIR) 50 mm, aço galvalume 0,5 mm; no se escala por espesor porque existe la medida; "
                     "fijación y M.O. SINAPI sin cambio",
            "nota": "el SINAPI no tiene telha de PU de 50 mm: el PIR es la espuma de poliuretano modificada que sí publica en 50 mm"},

        "CU017BR": {
            "partes": [P("100327", 1, "rufo de chapa galvanizada N.º 26, corte 33 cm", mat=1.5152)],
            "cambios": {"1113": ("ICD", "1114", 1, "pieza de chapa N.º 26 (0,5 mm) corte 50 cm en lugar de corte 33 cm")},
            "fijar": {"1114": (1.1716, "0,5858 m² de chapa por metro de la receta ÷ 0,50 m de corte"),
                      "C:88323": (0.233186, "telhadista extrapolado a corte 50 cm con la relación 94231 (25 cm) ↔ 100327 (33 cm): +0,002424 h por cm"),
                      "C:88316": (0.361494, "servente extrapolado a corte 50 cm con la misma relación")},
            "regla": "cumbrera de chapa lisa = rufo 100327 (chapa N.º 26 = 0,5 mm, como se tomó la N.º 28 en la fase B) llevado de "
                     "corte 33 a corte 50 cm: pieza 1114 (N.º 26 corte 50) en cantidad 0,5858 m² de la receta ÷ 0,50 = 1,1716 m; solda, "
                     "rebite, prego y selante × 50/33 (el SINAPI los lleva proporcionales al corte); M.O. extrapolada con la relación "
                     "94231 ↔ 100327"},

        "CU022BR": {
            "partes": [P("94228", 1, "calha de chapa galvanizada, desarrollo 50 cm")],
            "cambios": {"40783": ("ICD", "1118", 1, "pieza de chapa N.º 26 (0,5 mm) corte 50 cm en lugar de N.º 24, mismo corte")},
            "extras": [("ICD", "566", 0.5125, "barra chata 3/4\" × 1/8\" de soporte: 0,5125 m/m de la receta del ítem")],
            "regla": "94228 (calha chapa N.º 24, desarrollo 50 cm) con la pieza cambiada por la de chapa N.º 26 corte 50 cm (insumo "
                     "1118; N.º 28 tomada como 0,5 mm igual que en la fase B), 1,05 m/m; + barra chata 566 de la receta (0,5125 m); "
                     "solda, fijaciones y M.O. SINAPI sin cambio"},

        "CU025BR": {
            "partes": [P("98554", 1, "membrana acrílica, 3 demãos, por m² de cubierta")],
            "regla": "98554 (impermeabilización con membrana a base de resina acrílica, 3 demãos, 1,2 kg/m²) aplicada sobre la cubierta "
                     "de teja: sin cambio de cantidades; el SINAPI no publica un consumo mayor para superficie de teja, así que no se "
                     "agrega. La receta ArqOn traía 0,68 L/m² de membrana líquida"},

        "CU027BR": {
            "partes": [P("95626", 1, "látex acrílica en superficie externa, dos demãos")],
            "regla": "95626 (tinta látex acrílica en paredes externas de casas, dos demãos, 0,206 L/m²) aplicada sobre la cubierta: el "
                     "SINAPI no tiene pintura látex de cubierta; cantidades y M.O. SINAPI sin cambio",
            "nota": "baja porque la receta ArqOn traía 0,83 h de mano de obra; SINAPI: 0,33 h"},
    }

    DECISION = {
        "CU008BR": {
            "pregunta": "El SINAPI no tiene cubierta en steel frame (perfiles galvanizados livianos con cerchas). ¿Se toma como "
                        "estructura la trama de aço del SINAPI (terças de perfil U de chapa doblada, sin cerchas) o se deja la receta actual?",
            "grupo": "Cubierta en steel frame",
            "opciones": {
                "A": {"partes": [P("94213", 1, "telhamento con telha de aço e = 0,5 mm"),
                                 P("92580", 1, "trama de aço (terças) para telha metálica")],
                      "cambios": {"7243": ("ICD", "25007", 1, "telha ondulada de aço zincado 0,5 mm en lugar de la trapezoidal (igual que CU002BR)")},
                      "regla": "94213 con la telha ondulada 25007 (N.º 28 = 0,5 mm, fase B) + trama de aço 92580 (terças de perfil U "
                               "enrijecido, 4,33 kg/m²) en lugar de los perfiles de steel frame; sin cerchas ni anclajes (el SINAPI los "
                               "cotiza aparte, por unidad o por kg)",
                      "nota": "baja porque la receta ArqOn traía 7 m de perfiles con cerchas a precio estimado y 2,7 h de mano de obra"},
                "B": None},
            "etiquetas": {"A": "telhamento SINAPI + trama de aço SINAPI (sin cerchas)", "B": "dejar la receta actual (perfiles a precio estimado)"},
            "recomendada": "A"},

        "CU010BR": {
            "pregunta": "El SINAPI no tiene cubierta en steel frame (perfiles galvanizados livianos con cerchas). ¿Se toma como "
                        "estructura la trama de aço del SINAPI (ripas, caibros y terças, sin cerchas) o se deja la receta actual?",
            "grupo": "Cubierta en steel frame",
            "opciones": {
                "A": {"partes": [P("94201", 1, "telhamento con telha cerâmica capa-canal tipo colonial"),
                                 P("92574", 1, "trama de aço: ripas, caibros e terças para telha capa-canal")],
                      "regla": "94201 (telha colonial 7173, 27,5 telhas/m²) + trama de aço 92574 (ripas de perfil cartola, caibros y "
                               "terças de perfil U) en lugar de los perfiles de steel frame; sin cerchas ni anclajes. La receta ArqOn "
                               "traía 18,4 tejas/m²: manda el rendimiento de la teja SINAPI"},
                "B": None},
            "etiquetas": {"A": "telhamento SINAPI + trama de aço SINAPI (sin cerchas)", "B": "dejar la receta actual (perfiles a precio estimado)"},
            "recomendada": "A"},

        "CU013BR": {
            "pregunta": "El SINAPI no tiene la teja española de color de fibrocemento: sólo la placa ondulada gris de 6 mm. "
                        "¿Se pasa a la ondulada (queda igual que CU009BR) o se deja la receta actual?",
            "grupo": "Teja que el SINAPI no tiene",
            "opciones": {
                "A": {"partes": [P("94207", 1, "telhamento con telha ondulada de fibrocimento 6 mm"),
                                 P("92543", 1, "trama de madeira (terças) para telha ondulada")],
                      "regla": "94207 (telha ondulada de fibrocimento 6 mm, insumo 7194) + trama de madeira 92543, sin cambio: la teja "
                               "española de color no existe en el SINAPI y se toma la placa de fibrocemento más cercana",
                      "nota": "baja porque la teja española de color estaba a 72,82 R$/m² (estimado) y la ondulada SINAPI vale 26,54; "
                              "además la receta ArqOn traía 5,3 h de mano de obra"},
                "B": None},
            "etiquetas": {"A": "placa ondulada de fibrocimento 6 mm + trama de madeira (igual que CU009BR)",
                          "B": "dejar la receta actual (teja a precio estimado)"},
            "recomendada": "A"},

        "CU021BR": {
            "pregunta": "El SINAPI no tiene bajante (condutor) de chapa galvanizada: sólo calha de chapa y condutor de PVC. "
                        "¿Se adapta la calha de chapa al desarrollo del bajante o se pasa al tubo de PVC pluvial DN 100?",
            "grupo": "Bajante de chapa galvanizada",
            "opciones": {
                "A": {"partes": [P("94227", 1, "calha de chapa galvanizada, desarrollo 33 cm", mat=1.2424)],
                      "cambios": {"40782": ("ICD", "1110", 1, "pieza de chapa N.º 26 (0,5 mm) corte 45 cm, el corte SINAPI más cercano al desarrollo del bajante")},
                      "fijar": {"1110": (0.9522, "0,4285 m² de chapa por metro de la receta ÷ 0,45 m de corte"),
                                "C:88323": (0.274273, "telhadista interpolado a desarrollo 41 cm entre 94227 (33 cm) y 94228 (50 cm): +0,003146 h por cm"),
                                "C:88316": (0.40258, "servente interpolado a desarrollo 41 cm entre 94227 y 94228")},
                      "regla": "94227 (calha chapa N.º 24, desarrollo 33 cm) llevada al desarrollo del bajante: 0,4285 m² de la receta ÷ "
                               "1,05 = 41 cm; pieza 1110 (chapa N.º 26 = 0,5 mm, corte 45) en cantidad 0,4285 ÷ 0,45 = 0,9522 m; solda, "
                               "rebite, prego y selante × 41/33; M.O. interpolada entre 94227 y 94228"},
                "B": {"partes": [P("89578", 1, "tubo PVC série R DN 100 en condutor vertical de aguas pluviales")],
                      "regla": "89578 (tubo PVC série R, agua pluvial, DN 100, en condutores verticales) sin cambio: cambia el material "
                               "del bajante de chapa a PVC"}},
            "etiquetas": {"A": "calha de chapa SINAPI adaptada al bajante (sigue siendo de chapa galvanizada)",
                          "B": "tubo PVC pluvial DN 100 (cambia el material)"},
            "recomendada": "A"},

        "CU026BR": {
            "pregunta": "La pintura anticorrosiva del SINAPI se cotiza por mano (0,11 L/m²) y la receta ArqOn trae 0,166 L/m² "
                        "(1,5 manos). ¿Cuántas manos lleva el ítem?",
            "grupo": "Pintura anticorrosiva: número de manos",
            "opciones": {
                "A": {"partes": [P("100717", 1, "lijado manual de la superficie metálica"),
                                 P("100722", 1, "fondo anticorrosivo (zarcão) a rodillo o pincel, 1 mano")],
                      "regla": "lijado 100717 (0,3 lija/m², la receta ArqOn traía 0,35) + 100722 (zarcão a rodillo sobre superficie "
                               "metálica, por mano) × 1 mano; cantidades y M.O. SINAPI sin cambio"},
                "B": {"partes": [P("100717", 1, "lijado manual de la superficie metálica"),
                                 P("100722", 2, "fondo anticorrosivo (zarcão) a rodillo o pincel, 2 manos")],
                      "regla": "lijado 100717 + 100722 (zarcão a rodillo sobre superficie metálica, por mano) × 2 manos; cantidades y "
                               "M.O. SINAPI sin cambio",
                      "nota": "sube porque el SINAPI pone 0,68 h de pintor por mano y la receta ArqOn traía 0,72 h en total"}},
            "etiquetas": {"A": "lijado + 1 mano de zarcão", "B": "lijado + 2 manos de zarcão"},
            "recomendada": "A"},
    }

    NO_CONVIENE = {
        "CU024BR": "la composição del SINAPI para policarbonato (107143, e = 6 mm) y sus remates (107144, 107145) no tienen costo en "
                   "ninguna UF: la chapa 45743, el perfil de unión 45744, el perfil U 45746, las gaxetas 45750/45751 y el tornillo "
                   "45749 todavía no están en el ICD 08/2026, y no hay otro insumo de policarbonato alveolar con precio; armarla sería "
                   "inventar el material principal. Queda la receta actual hasta que el SINAPI publique esos precios",
    }
    return LISTO, DECISION, NO_CONVIENE


# ── Mampostería ──
def _tablas_mamposteria():
    LISTO, DECISION, NO_CONVIENE = {}, {}, {}
    # frag_mamposteria.py — fase C (Brasil), grupo «mamposteria» (12 ítems)
    # Se ejecuta con P ya definido: P(composição, cantidad, "de dónde sale", mat=1, mo=1, eq=1)

    # ---------------------------------------------------------------------------------------------------------------
    # Piezas comunes
    # ---------------------------------------------------------------------------------------------------------------

    # Mortero 87292 (1:2:8 en betoneira) abierto en el aplanado: lo que se saca cuando el ítem pega el ladrillo con adhesivo
    SIN_MORTERO = {
        "1379": "cemento del mortero 87292: el ítem pega el ladrillo con adhesivo en capa fina",
        "1106": "cal del mortero 87292: idem",
        "370": "arena del mortero 87292: idem",
        "C:88377": "operador de betoneira del mortero 87292: el adhesivo no se prepara en betoneira",
        "C:88830": "betoneira (CHP) del mortero 87292: idem",
        "C:88831": "betoneira (CHI) del mortero 87292: idem",
    }

    # Junta fina (3 mm) en vez de 1 cm, cara del bloque 24 × 14 cm: (0,25 × 0,15) ÷ (0,243 × 0,143)
    J_24X14 = round((0.25 * 0.15) / (0.243 * 0.143), 4)      # 1,0792
    # Idem, cara del bloque 29 × 19 cm: (0,30 × 0,20) ÷ (0,293 × 0,193)
    J_29X19 = round((0.30 * 0.20) / (0.293 * 0.193), 4)      # 1,0610
    # Metros de junta por m² (1/alto + 1/largo, con junta de 3 mm): cara 24 × 15 del ítem = 10,65; cara 29 × 19 = 8,59
    ADH_29X19 = round((1 / 0.193 + 1 / 0.293) / (1 / 0.153 + 1 / 0.243), 4)   # 0,8066

    PERFIL_90 = {
        "39422": ("ICD", "39423", 1, "montante de 70 mm → 90 mm (el ítem lleva perfil de 92 mm; el SINAPI tiene 48, 70 y 90)"),
        "39419": ("ICD", "39420", 1, "guia de 70 mm → 90 mm (idem)"),
    }


    def drywall(comp, caras, placa_hoy):
        return {
            "partes": [P(comp, 1, f"parede drywall {caras}, guias simples, sem vãos (m² de pared)")],
            "cambios": dict(PERFIL_90),
            "regla": (f"{comp} (drywall {caras}, perfiles de 70 mm) con montante y guia de 90 mm (39423 y 39420, mismos metros); "
                      "placa ST 12,5 mm, tornillos, cinta y masa del SINAPI; M.O. SINAPI sin cambio (todas las composições de "
                      "drywall del SINAPI usan perfil de 70: no publica otra anchura). Se omite la canaleta cold rolled "
                      "(0,02 pza/m², menor)"),
            "nota": ("baja por la productividad SINAPI del drywall (montador + servente ≈ 0,46 a 0,69 h/m² contra 3,2 a 3,7 h/m² "
                     f"de la receta boliviana) y la placa a precio SINAPI por m²; la receta traía {placa_hoy} m² de placa por m²"),
        }


    def cimenticia(comp, caras, placa, esp):
        return {
            "partes": [P(comp, 1, f"estructura, fijación y M.O. de la parede drywall {caras}, sem vãos (m² de pared)")],
            "cambios": {
                "39413": ("ICD", placa, 1, f"chapa de gesso → placa cimentícia lisa {esp} mm (mismos m² con su pérdida)"),
                "39435": ("ICD", "39439", 1, "tornillo punta aguja → punta broca 25 mm (la placa cimentícia se perfora)"),
                "39434": ("ICD", "43651", 1, "masa de yeso para juntas → massa acrílica de uso externo (mismos kg)"),
                "39431": ("ICD", "36887", 0.05, "cinta de papel → tela de fibra de vidrio antiálcali, tira de 5 cm (0,05 m² por m)"),
                "39432": ("ICD", "36887", 0.05, "cinta de esquina → tela de fibra de vidrio antiálcali, tira de 5 cm (0,05 m² por m)"),
            },
            "regla": (f"{comp} (drywall {caras}, perfiles de 70 mm) con la chapa de gesso cambiada por placa cimentícia {esp} mm "
                      f"({placa}), tornillo punta broca (39439), juntas con massa acrílica (43651) y tela de fibra de vidrio "
                      "(36887, tira de 5 cm); perfiles y M.O. SINAPI de drywall sin cambio (el SINAPI no publica pared de placa "
                      "cimentícia ni la placa de 8 mm)"),
            "nota": ("baja por la productividad SINAPI del drywall (0,46 a 0,69 h/m² contra 2,6 a 3,6 h/m² de la receta boliviana) "
                     "y porque la placa pasa de un precio estimado por pieza al precio SINAPI por m²"),
        }


    def con_adhesivo(comp, bloque, desc_bloque, f_junta, cara, kg, de_donde_kg):
        return {
            "partes": [P(comp, 1, f"alvenaria de vedação de {desc_bloque} (m² de pared)")],
            "quitar": dict(SIN_MORTERO),
            "escala": {bloque: (f_junta, f"junta de 3 mm en vez de 1 cm, cara {cara} cm")},
            "extras": [("ICD", "37595", kg, f"argamassa colante AC III en lugar del adhesivo del ítem: {de_donde_kg}")],
            "regla": (f"{comp} ({desc_bloque}) sin el mortero 87292 (cemento, cal, arena y betoneira) + {str(kg).replace('.', ',')} kg/m² "
                      f"de argamassa colante AC III (37595), el producto SINAPI más cercano al adhesivo del ítem; bloques × "
                      f"{str(f_junta).replace('.', ',')} por junta de 3 mm; tela y pinos de amarre SINAPI; M.O. de pedreiro y servente SINAPI "
                      "sin cambio (el SINAPI no publica alvenaria con adhesivo)"),
            "nota": ("sube porque queda la M.O. SINAPI de la pared con mortero (la receta del ítem tenía la mitad de horas) "
                     "y entran tela y pinos de amarre"),
        }


    def tal_cual(comp, desc, extra=""):
        return {
            "partes": [P(comp, 1, f"{desc} (m² de pared)")],
            "regla": f"{comp} tal cual: {desc}; mortero 1:2:8 en betoneira{extra}",
        }


    def demolicion(comp, e, que):
        return {
            "partes": [P(comp, e, f"m³ de pared por m² = espesor {str(e).replace('.', ',')} m")],
            "regla": (f"{comp} (demolición manual de alvenaria de {que}, sin reaprovechamiento, por m³) × "
                      f"{str(e).replace('.', ',')} m³/m² (pared de {round(e * 100)} cm); sin retiro de escombros, como el ítem"),
            "nota": ("baja porque la receta actual cargaba por m² el coeficiente de 1 m³ (2,1957 h de servente es el "
                     "coeficiente de la 97622 por m³)"),
        }


    # ---------------------------------------------------------------------------------------------------------------
    LISTO = {
        "MP012BR": drywall("96370", "1 face simples", "0,93"),
        "MP013BR": drywall("96358", "2 faces simples", "1,76"),
    }

    # ---------------------------------------------------------------------------------------------------------------
    DECISION = {
        # ---- demolición por m²: falta el espesor -------------------------------------------------------------------
        "MP001BR": {
            "pregunta": ("El SINAPI demuele la alvenaria por m³ y el ítem es por m²: ¿qué pared se toma (espesor y tipo de "
                         "ladrillo)? El nombre sólo dice «alvenaria de tijolo»"),
            "grupo": "Demolición de pared por m²: espesor",
            "opciones": {
                "A": demolicion("97622", 0.15, "bloco furado"),
                "B": demolicion("97624", 0.15, "tijolo maciço"),
                "C": demolicion("97622", 0.20, "bloco furado"),
            },
            "etiquetas": {"A": "bloco furado, pared de 15 cm", "B": "tijolo maciço, pared de 15 cm",
                          "C": "bloco furado, pared de 20 cm"},
            "recomendada": "A"},

        # ---- ladrillo boliviano → bloque brasileño -----------------------------------------------------------------
        "MP007BR": {
            "pregunta": ("El ladrillo 6 huecos 24×15×11 echado (pared de 16 cm) no existe en Brasil: ¿qué pared SINAPI de "
                         "14 cm lo reemplaza?"),
            "grupo": "Ladrillo boliviano → bloque brasileño",
            "opciones": {
                "A": tal_cual("103334", "bloco cerâmico 6 furos 9×14×19 echado (deitado), pared de 14 cm, 54,13 un/m²",
                              ", tela y pinos de amarre incluidos"),
                "B": tal_cual("103360", "bloco cerâmico 14×19×29 (9 furos), pared de 14 cm, 18,04 un/m²",
                              ", tela y pinos de amarre incluidos"),
                "C": tal_cual("103368", "bloco cerâmico 14×19×39 (9 furos), pared de 14 cm, 13,53 un/m²",
                              ", tela y pinos de amarre incluidos"),
            },
            "etiquetas": {"A": "bloco 6 furos 9×14×19 echado, pared de 14 cm", "B": "bloco 14×19×29, pared de 14 cm",
                          "C": "bloco 14×19×39, pared de 14 cm"},
            "recomendada": "A"},
        "UH009BR": {
            "pregunta": ("El nombre no dice el espesor y la receta trae 54 ladrillos 6 huecos por m² (en Bolivia, pared de "
                         "24 cm con el 24×15×11 atravesado): ¿qué pared SINAPI lo reemplaza?"),
            "grupo": "Ladrillo boliviano → bloque brasileño",
            "opciones": {
                "A": tal_cual("103334", "bloco cerâmico 6 furos 9×14×19 echado (deitado), pared de 14 cm, 54,13 un/m²",
                              ", tela y pinos de amarre incluidos"),
                "B": tal_cual("103362", "bloco cerâmico 19×19×29 (9 furos), pared de 19 cm, 18,04 un/m²",
                              ", tela y pinos de amarre incluidos"),
                "C": tal_cual("103332", "bloco cerâmico 6 furos 9×14×19 de canto, pared de 9 cm, 36,09 un/m²",
                              ", tela y pinos de amarre incluidos"),
            },
            "etiquetas": {"A": "bloco 6 furos 9×14×19 echado, pared de 14 cm (54 un/m², como la receta)",
                          "B": "bloco 19×19×29, pared de 19 cm (la más gruesa del SINAPI)",
                          "C": "bloco 6 furos 9×14×19 de canto, pared de 9 cm"},
            "recomendada": "A"},
        "MP009BR": {
            "pregunta": ("El nombre dice pared de 15 cm, pero la receta trae 70 ladrillos macizos 5×10×20 por m², que es la "
                         "pared de 10 cm del SINAPI (el SINAPI no tiene ladrillo macizo de 15 cm de ancho): ¿cuál vale?"),
            "grupo": "Ladrillo boliviano → bloque brasileño",
            "opciones": {
                "A": tal_cual("101159", "tijolo cerâmico maciço 5×10×20, pared de 10 cm, 73,49 un/m² (la receta trae 70)"),
                "B": {
                    "partes": [P("101159", 1, "alvenaria de tijolo maciço 5×10×20, pared de 10 cm, llevada a 15 cm (m² de pared)",
                                 mat=1.5, mo=1.2345, eq=1.5)],
                    "escala": {"C:88377": (round(1.5 / 1.2345, 4), "el operador de betoneira sigue al mortero (× 1,5 en total)")},
                    "regla": ("101159 (tijolo maciço 5×10×20, pared de 10 cm) llevada a 15 cm: ladrillos y mortero × 15/10; "
                              "pedreiro y servente × 1,2345, la relación del propio SINAPI entre 103334 y 103332 (mismo bloque, "
                              "1,5 veces las piezas por m²: 2,003 h ÷ 1,6225 h); betoneira y su operador × 1,5 con el mortero"),
                },
            },
            "etiquetas": {"A": "pared de 10 cm de tijolo maciço 5×10×20 (SINAPI tal cual)",
                          "B": "pared de 15 cm: la de 10 cm con materiales × 1,5 y M.O. × 1,23"},
            "recomendada": "A"},

        # ---- ladrillo pegado con adhesivo: el SINAPI no tiene el adhesivo -------------------------------------------
        "MP006BR": {
            "pregunta": ("El SINAPI no tiene argamassa polimérica para asentar ladrillo ni alvenaria con adhesivo, y el "
                         "ladrillo 24×15×11 no existe en Brasil: ¿con qué bloque y qué pegamento queda el ítem?"),
            "grupo": "Ladrillo pegado con adhesivo (sin mortero)",
            "opciones": {
                "A": con_adhesivo("103354", "44459", "bloco cerâmico 11,5×14×24 (9 furos), pared de 11,5 cm", J_24X14, "24 × 14",
                                  2.0531, "los kg por m² de la receta del ítem"),
                "B": con_adhesivo("103358", "44460", "bloco cerâmico 6 furos 11,5×19×29, pared de 11,5 cm", J_29X19, "29 × 19",
                                  round(2.0531 * ADH_29X19, 4),
                                  "los 2,0531 kg de la receta × 0,8066 (metros de junta por m²: 8,59 con el bloque 29 × 19 contra 10,65)"),
                "C": tal_cual("103354", "bloco cerâmico 11,5×14×24 (9 furos), pared de 11,5 cm, 28,87 un/m²",
                              " en vez del adhesivo (el ítem pasa a ser una pared común), tela y pinos de amarre incluidos"),
                "D": None,
            },
            "etiquetas": {"A": "bloco 11,5×14×24 (las medidas del 24×15×11; 9 furos) + argamassa colante AC III",
                          "B": "bloco 6 furos 11,5×19×29 + argamassa colante AC III",
                          "C": "bloco 11,5×14×24 con mortero común (SINAPI tal cual)",
                          "D": "dejar la receta actual (adhesivo con precio estimado)"},
            "recomendada": "A"},
        "MP008BR": {
            "pregunta": ("El SINAPI no tiene argamassa colante para ladrillo ni alvenaria con adhesivo; el ladrillo rayado "
                         "24×15×9,8 equivale al bloco 6 furos 9×14×24: ¿con qué pegamento queda el ítem?"),
            "grupo": "Ladrillo pegado con adhesivo (sin mortero)",
            "opciones": {
                "A": con_adhesivo("103352", "44458", "bloco cerâmico 6 furos 9×14×24, pared de 9 cm", J_24X14, "24 × 14",
                                  2.0523, "los kg por m² de la receta del ítem"),
                "B": tal_cual("103352", "bloco cerâmico 6 furos 9×14×24, pared de 9 cm, 28,87 un/m²",
                              " en vez del adhesivo (el ítem pasa a ser una pared común), tela y pinos de amarre incluidos"),
                "C": None,
            },
            "etiquetas": {"A": "bloco 6 furos 9×14×24 + argamassa colante AC III",
                          "B": "bloco 6 furos 9×14×24 con mortero común (SINAPI tal cual)",
                          "C": "dejar la receta actual (ladrillo y adhesivo con precio estimado)"},
            "recomendada": "A"},

        # ---- drywall con placa de 0,90 × 2,40 ----------------------------------------------------------------------
        "MP014BR": {
            "pregunta": ("La placa de yeso de 0,90 × 2,40 m no está en el SINAPI (sólo 1,20 × 2,40 y 1,20 × 1,80, por m²): "
                         "¿se usa la de 1,20 × 2,40? El ítem queda con la misma receta que MP012BR"),
            "grupo": "Drywall con placa de 0,90 × 2,40",
            "opciones": {"A": drywall("96370", "1 face simples", "1,16"), "B": None},
            "etiquetas": {"A": "placa ST 12,5 mm de 1,20 × 2,40 por m² (igual que MP012BR)",
                          "B": "dejar la receta actual (placa con precio estimado)"},
            "recomendada": "A"},
        "MP015BR": {
            "pregunta": ("La placa de yeso de 0,90 × 2,40 m no está en el SINAPI (sólo 1,20 × 2,40 y 1,20 × 1,80, por m²): "
                         "¿se usa la de 1,20 × 2,40? El ítem queda con la misma receta que MP013BR"),
            "grupo": "Drywall con placa de 0,90 × 2,40",
            "opciones": {"A": drywall("96358", "2 faces simples", "1,48"), "B": None},
            "etiquetas": {"A": "placa ST 12,5 mm de 1,20 × 2,40 por m² (igual que MP013BR)",
                          "B": "dejar la receta actual (placa con precio estimado)"},
            "recomendada": "A"},

        # ---- pared de placa cimentícia -----------------------------------------------------------------------------
        "MP020BR": {
            "pregunta": ("El SINAPI no publica pared de placa cimentícia y la placa de 8 mm de la receta no está (hay de 6 y "
                         "de 10 mm): ¿se arma sobre la pared de drywall con placa de 10 o de 6 mm?"),
            "grupo": "Pared de placa cimentícia",
            "opciones": {"A": cimenticia("96370", "1 face simples", "11062", 10),
                         "B": cimenticia("96370", "1 face simples", "11063", 6),
                         "C": None},
            "etiquetas": {"A": "placa cimentícia de 10 mm sobre estructura de drywall",
                          "B": "placa cimentícia de 6 mm sobre estructura de drywall",
                          "C": "dejar la receta actual (precios estimados)"},
            "recomendada": "A"},
        "MP021BR": {
            "pregunta": ("El SINAPI no publica pared de placa cimentícia y la placa de 8 mm de la receta no está (hay de 6 y "
                         "de 10 mm): ¿se arma sobre la pared de drywall con placa de 10 o de 6 mm en las dos caras?"),
            "grupo": "Pared de placa cimentícia",
            "opciones": {"A": cimenticia("96358", "2 faces simples", "11062", 10),
                         "B": cimenticia("96358", "2 faces simples", "11063", 6),
                         "C": None},
            "etiquetas": {"A": "placa cimentícia de 10 mm en las dos caras, estructura de drywall",
                          "B": "placa cimentícia de 6 mm en las dos caras, estructura de drywall",
                          "C": "dejar la receta actual (precios estimados)"},
            "recomendada": "A"},
    }

    NO_CONVIENE = {}
    return LISTO, DECISION, NO_CONVIENE


# ── Inst. Sanitarias (1) ──
def _tablas_sanitarias1():
    LISTO, DECISION, NO_CONVIENE = {}, {}, {}
    # frag_sanitarias1.py — fase C (Brasil), grupo sanitarias1. Se ejecuta con P ya definido.
    # 20 ítems: IS003 IS004 IS007 IS008 IS009 IS010 IS018 IS019 IS023 IS024 IS025 IS026 IS027 IS030 IS032 IS035 IS037
    #           IS040 IS041 IS042


    # ── Ayudas ──────────────────────────────────────────────────────────────────────────────────────────────────────
    def _pvc_roscavel(tubo_comp, joelho_comp, dn_mm, pulg, n_con, tubo_sold, tubo_rosc, joelho_sold, joelho_rosc, fita, comp_fita):
        """Tubo PVC roscável por metro: composição del tubo soldável del mismo calibre con el tubo y el joelho cambiados por
        los roscáveis del ICD; la unión roscada no lleva adhesivo, solución ni lija, y sí fita veda-rosca."""
        return {
            "partes": [P(tubo_comp, 1, f"tubo PVC {dn_mm} mm ({pulg}) en ramal de agua, por metro"),
                       P(joelho_comp, n_con, f"{n_con} conexiones/m de la receta ArqOn, como joelho 90° {dn_mm} mm")],
            "quitar": {"122": "adhesivo: la unión del ítem es roscada",
                       "20083": "solución limpiadora: la unión del ítem es roscada",
                       "38383": "lija: la unión del ítem es roscada"},
            "cambios": {tubo_sold: ("ICD", tubo_rosc, 1, f"tubo PVC roscável {pulg} en lugar del soldável {dn_mm} mm (metro por metro, misma pérdida 4,93 %)"),
                        joelho_sold: ("ICD", joelho_rosc, 1, f"joelho 90° PVC roscável {pulg} en lugar del soldável {dn_mm} mm")},
            "extras": [("ICD", "3148", round(n_con * fita, 5),
                        f"fita veda-rosca: {fita} rollo por conexión roscada {pulg} (coeficiente SINAPI {comp_fita}) × {n_con}")],
            "regla": (f"{tubo_comp} (tubo PVC soldável {dn_mm} mm) + {joelho_comp} × {n_con} (conexiones/m de la receta): tubo y joelho "
                      f"cambiados por los PVC roscáveis {pulg} del ICD ({tubo_rosc}, {joelho_rosc}); sin adhesivo/solución/lija y con "
                      f"fita veda-rosca del SINAPI ({comp_fita}); M.O. SINAPI sin cambio (el SINAPI no publica tubo roscável por metro)"),
            "nota": "sube por el tubo roscável (pared gruesa), más caro que el soldável; la M.O. es la del SINAPI",
        }


    def _acc_caixa(saida_ad, saida_furo, saida_txt):
        """Accesorios de la caixa d'água como en el kit SINAPI 102622/102623, sin tubos, conexiones ni registros."""
        return [P("94796", 1, "torneira de boia 3/4\" (la boia de la receta)"),
                P("94703", 3, "3 adaptadores com flange 25 mm × 3/4\" (entrada, extravasor y limpieza), como el kit SINAPI"),
                P(saida_ad, 1, f"1 adaptador com flange {saida_txt} (salida), como el kit SINAPI"),
                P("102591", 3, "3 furos Ø 25 mm"),
                P(saida_furo, 1, f"1 furo para la salida {saida_txt}")]


    def _caixa(comp, litros, litros_item, saida_ad, saida_furo, saida_txt):
        return {
            "partes": [P(comp, 1, f"caixa d'água de polietileno {litros} L con tapa, instalada")] + _acc_caixa(saida_ad, saida_furo, saida_txt),
            "regla": (f"{comp} (caixa {litros} L; el SINAPI no tiene {litros_item} L) + accesorios como el kit SINAPI 102622/102623: "
                      f"torneira de boia 94796, 4 adaptadores com flange (94703 × 3 + {saida_ad}) y sus 4 furos; sin tubos, conexiones "
                      f"ni registros (son de la instalación, IS039); M.O. la de cada composição"),
            "nota": "la caixa y la boia pasan de precio estimado a precio SINAPI; la M.O. SINAPI es menor que la de la receta",
        }


    def _base_alv(m2, bloques):
        return P("103332", m2, f"base de alvenaria: {bloques} bloques 24×15 de la receta = {m2} m² de muro (25 piezas/m², junta 1 cm), "
                               f"hecha con bloco cerâmico 9×14×19 (el insumo con que ya se cotiza ese bloque)")


    _ACC_BOMBA = [P("99620", 1, "válvula de retenção 1\""), P("89353", 1, "registro de gaveta 3/4\""),
                  P("92906", 1, "união galvanizada 1\""), P("92905", 1, "união galvanizada 3/4\""),
                  P("102137", 1, "chave de boia automática")]
    _EXT_BOMBA = [("ICD", "765", 1, "bucha de redução galvanizada 1\" × 3/4\" (receta: 1)"),
                  ("ICD", "4179", 3, "niple galvanizado 1\" (receta: 3,08 → 3)"),
                  ("ICD", "4178", 1, "niple galvanizado 3/4\" (receta: 1)")]


    def _bomba(comp, cv):
        return {
            "partes": [P(comp, 1, f"bomba centrífuga trifásica {cv} CV, instalada")] + _ACC_BOMBA,
            "extras": list(_EXT_BOMBA),
            "regla": (f"{comp} (bomba centrífuga {cv} CV; el SINAPI no tiene 2 HP ni hidroneumática) + accesorios de la receta al "
                      f"entero: 99620 + 89353 + 92906 + 92905 + 102137 + bucha y niples galvanizados (ICD 765, 4179 × 3, 4178)"),
            "nota": "baja a menos de la mitad: la bomba hidroneumática estimada (4237) pasa a una centrífuga SINAPI sin tanque de presión",
        }


    # ── LISTO ───────────────────────────────────────────────────────────────────────────────────────────────────────
    LISTO = {
        "IS008BR": {
            "partes": [P("106772", 1, "pia de aço inox instalada (composição de 1 cuba 0,55×1,20)"),
                       P("86908", 1, "misturador de mesa para pia de cozinha")],
            "cambios": {"1746": ("ICD", "1750", 1, "pia inox 2 cubas con válvulas y escorredor duplo 0,55×2,00 m en lugar de la de 1 cuba 0,55×1,20 m")},
            "regla": ("106772 con la pia cambiada por la de 2 cubas y escorredor duplo 0,55×2,00 m (ICD 1750) + 86908 (misturador); "
                      "M.O. SINAPI sin cambio (el SINAPI no publica otra medida de pia); el cemento blanco queda dentro de la instalación"),
            "nota": "la pia de 2 cubas ya se cotizaba a 691 (= ICD 1750); sube por el misturador SINAPI (466) frente al estimado (309)"},

        "IS018BR": {
            "partes": [P("92687", 1, "tubo galvanizado 1/2\" clase media, unión roscada, por metro"),
                       P("92699", 0.51, "conexiones: 0,51 piezas/m de la receta ArqOn, como joelho 90° 1/2\"")],
            "regla": ("92687 + 92699 × 0,51: el SINAPI sólo publica el galvanizado 1/2\" instalado en ramal de gas; es el mismo tubo "
                      "(ICD 7691) con la misma unión roscada, usado acá para agua; conexiones/m de la receta; M.O. SINAPI sin cambio"),
            "nota": "el tubo ya tenía precio SINAPI; cambia la M.O. (encanador + auxiliar SINAPI) y el joelho con su instalación"},

        "IS019BR": {
            "partes": [P("92688", 1, "tubo galvanizado 3/4\" clase media, unión roscada, por metro"),
                       P("92701", 0.64, "conexiones: 0,64 piezas/m de la receta ArqOn, como joelho 90° 3/4\"")],
            "regla": ("92688 + 92701 × 0,64: el SINAPI sólo publica el galvanizado 3/4\" instalado en ramal de gas; es el mismo tubo "
                      "(ICD 7700) con la misma unión roscada, usado acá para agua; conexiones/m de la receta; M.O. SINAPI sin cambio"),
            "nota": "sube por la M.O. SINAPI del tubo (0,28 h/m de cada oficio) y por el joelho instalado (41,09 c/u × 0,64)"},

        "IS023BR": _pvc_roscavel("89355", "89358", 20, "1/2\"", 0.51, "9867", "9856", "3542", "3543", 0.0084, "92699"),
        "IS024BR": _pvc_roscavel("89356", "89362", 25, "3/4\"", 0.51, "9868", "9859", "3529", "3505", 0.0106, "92701"),
        "IS025BR": _pvc_roscavel("89357", "89367", 32, "1\"", 0.49, "9869", "9866", "3536", "3482", 0.01328, "92703"),

        "IS026BR": {
            "partes": [P("97896", 1, "caixa enterrada de concreto 0,4×0,4×0,4 m con fondo y tapa, instalada")],
            "regla": ("97896 sin cambio de cantidades: caixa de concreto 0,4×0,4×0,4 m; el SINAPI la publica pré-moldada (no tiene la "
                      "moldeada en obra de la receta ArqOn); misma medida y mismo material"),
            "nota": "sube porque la pieza pré-moldada (384) cuesta más que el hormigón hecho en obra de la receta"},

        "IS035BR": {
            "partes": [P("98104", 0.6, "caixa de gordura em tijolo 0,2×0,4 m, h 0,8: peso 0,6 de la interpolación"),
                       P("98105", 0.4, "caixa de gordura em tijolo 0,4×0,7 m, h 0,8: peso 0,4 de la interpolación")],
            "regla": ("interpolación entre 98104 (0,2×0,4) y 98105 (0,4×0,7), ambas h 0,8 m en tijolo maciço, por el perímetro de muro: "
                      "1,6 m → 2,0 m (0,3×0,5) → 2,6 m ⇒ 0,6 × 98104 + 0,4 × 98105; materiales y M.O. con la relación del propio SINAPI "
                      "(los tijolos de las dos composições escalan 1,61 = perímetro 1,625)"),
            "nota": "baja porque la receta traía 72 kg de cemento y tijolo aparente (2,32 c/u); el SINAPI usa tijolo maciço comum (0,60)"},
    }


    # ── NECESITA_DECISION ───────────────────────────────────────────────────────────────────────────────────────────
    DECISION = {
        "IS003BR": {
            "pregunta": ("La receta no dice la medida de la caja (82 bloques ≈ 0,60×0,60 m × 1,0 m de alto) y el SINAPI no tiene caja "
                         "de bloque cerámico hueco: ¿qué caja de esgoto SINAPI la reemplaza?"),
            "grupo": "Cajas de inspección: medida y material",
            "opciones": {
                "A": {"partes": [P("97902", 1, "caixa enterrada de alvenaria de tijolo maciço 0,6×0,6×0,6 m para esgoto, con fondo y tapa")],
                      "regla": "97902 sin cambio: caixa de alvenaria 0,6×0,6×0,6 m en tijolo maciço (incluye fondo, revoque impermeable y tapa de concreto)",
                      "nota": "sube porque el SINAPI incluye fondo, tapa de concreto y revoque impermeable que la receta no traía"},
                "B": {"partes": [P("97906", 1, "caixa enterrada de alvenaria de blocos de concreto 0,6×0,6×0,6 m para esgoto")],
                      "regla": "97906 sin cambio: caixa 0,6×0,6×0,6 m en bloco de concreto",
                      "nota": "bloque hueco (de concreto) en vez de tijolo maciço"},
                "C": {"partes": [P("97901", 1, "caixa enterrada de alvenaria de tijolo maciço 0,4×0,4×0,4 m para esgoto")],
                      "regla": "97901 sin cambio: caixa de alvenaria 0,4×0,4×0,4 m en tijolo maciço",
                      "nota": "caja chica"}},
            "etiquetas": {"A": "0,6×0,6×0,6 m en tijolo maciço", "B": "0,6×0,6×0,6 m en bloco de concreto", "C": "0,4×0,4×0,4 m en tijolo maciço"},
            "recomendada": "A"},

        "IS004BR": {
            "pregunta": "El tanque de lavar de hierro esmaltado no existe en el SINAPI (hay de louça, mármol sintético e inox): ¿cuál lo reemplaza?",
            "grupo": "Tanques de lavar: material que el SINAPI no tiene",
            "opciones": {
                "A": {"partes": [P("86924", 1, "tanque de louça branca suspenso 20 L con sifão, válvula y torneira plástica"),
                                 _base_alv(1.04, 26)],
                      "regla": ("86924 (tanque de louça suspenso con sifão, válvula y torneira) + 103332 × 1,04 m² (base de alvenaria: "
                                "26 bloques de la receta); el cemento blanco queda dentro de la instalación SINAPI"),
                      "nota": "tanque blanco vitrificado, el más parecido a la vista"},
                "B": None,
                "C": {"partes": [P("106777", 1, "tanque de aço inox suspenso, instalado"), P("86883", 1, "sifão flexível de PVC"),
                                 P("86916", 1, "torneira plástica para tanque"), _base_alv(1.04, 26)],
                      "sin_ccd": {"106777": "su insumo 45667 (tanque inox de parede) no está en el ICD 08/2026"},
                      "cambios": {"45667": ("ICD", "11688", 1, "tanque de aço inox 50×40×22 cm con esfregador y válvula (el inox con precio en SP)")},
                      "regla": ("106777 armada desde sus líneas con el tanque inox ICD 11688 (trae la válvula) + 86883 (sifão) + 86916 "
                                "(torneira) + 103332 × 1,04 m² (base de alvenaria de la receta)"),
                      "nota": "tanque metálico"}},
            "etiquetas": {"A": "tanque de louça + base de alvenaria", "B": "dejar la receta actual", "C": "tanque de inox + base de alvenaria"},
            "recomendada": "A"},

        "IS007BR": {
            "pregunta": ("El SINAPI sólo tiene la pia inox de 2 cubas con escorredor DUPLO (0,55×2,00 m); la de 2 cubas y 1 escorredor "
                         "no está. Con esa pieza el ítem queda igual que IS008."),
            "grupo": "Pia de cocina de 2 cubas",
            "opciones": {
                "A": {"partes": [P("106772", 1, "pia de aço inox instalada (composição de 1 cuba 0,55×1,20)"),
                                 P("86908", 1, "misturador de mesa para pia de cozinha")],
                      "cambios": {"1746": ("ICD", "1750", 1, "pia inox 2 cubas con escorredor duplo 0,55×2,00 m (la única de 2 cubas del SINAPI)")},
                      "regla": ("106772 con la pia cambiada por la de 2 cubas y escorredor duplo 0,55×2,00 m (ICD 1750) + 86908 "
                                "(misturador); M.O. SINAPI sin cambio"),
                      "nota": "queda con la misma receta que IS008"},
                "B": None},
            "etiquetas": {"A": "pia 2 cubas con escorredor duplo (igual que IS008)", "B": "dejar la receta actual"},
            "recomendada": "A"},

        "IS009BR": {
            "pregunta": "El tanque de lavar ropa de concreto no existe en el SINAPI; el más cercano es el de mármol sintético.",
            "grupo": "Tanques de lavar: material que el SINAPI no tiene",
            "opciones": {
                "A": {"partes": [P("86930", 1, "tanque de mármore sintético suspenso 22 L con sifão, válvula y torneira plástica"),
                                 _base_alv(1.04, 26)],
                      "regla": ("86930 (tanque de mármol sintético suspenso con sifão, válvula y torneira) + 103332 × 1,04 m² (base de "
                                "alvenaria: 26 bloques de la receta)"),
                      "nota": "tanque + base, como la receta"},
                "B": None,
                "C": {"partes": [P("86926", 1, "tanque de mármore sintético com coluna 22 L con sifão, válvula y torneira plástica")],
                      "regla": "86926 sin cambio: tanque de mármol sintético con columna (la columna reemplaza la base de alvenaria)",
                      "nota": "sin base de alvenaria"}},
            "etiquetas": {"A": "mármol sintético + base de alvenaria", "B": "dejar la receta actual", "C": "mármol sintético con columna, sin base"},
            "recomendada": "A"},

        "IS010BR": {
            "pregunta": "El tanque de lavar ropa de concreto de 2 cubas no existe en el SINAPI; hay tanque doble de mármol sintético (insumo, sin composição).",
            "grupo": "Tanques de lavar: material que el SINAPI no tiene",
            "opciones": {
                "A": {"partes": [P("86930", 1, "tanque de mármore sintético suspenso con sifão, válvula y torneira (1.ª cuba)"),
                                 P("86883", 1, "2.º sifão (receta: 2)"), P("86879", 1, "2.ª válvula"),
                                 P("86916", 1, "2.ª torneira (receta: 2)"), _base_alv(2.04, 51)],
                      "cambios": {"11690": ("ICD", "36790", 1, "tanque duplo de mármore sintético 110×60 cm en lugar del simple 60×46")},
                      "regla": ("86930 con el tanque cambiado por el duplo de mármol sintético 110×60 (ICD 36790) + 2.º sifão, válvula y "
                                "torneira (86883, 86879, 86916) + 103332 × 2,04 m² (base de alvenaria: 51 bloques de la receta); M.O. "
                                "del tanque la del SINAPI (no publica tanque doble)"),
                      "nota": "tanque doble + base, como la receta"},
                "B": None},
            "etiquetas": {"A": "tanque doble de mármol sintético + base de alvenaria", "B": "dejar la receta actual"},
            "recomendada": "A"},

        "IS027BR": {
            "pregunta": "La caja sifonada de concreto no existe en el SINAPI (las sifonadas son de PVC): ¿qué la reemplaza?",
            "grupo": "Cajas prefabricadas que el SINAPI no tiene",
            "opciones": {
                "A": {"partes": [P("98102", 1, "caixa de gordura simples circular de concreto pré-moldado Ø 0,4 m (tiene sifón), instalada")],
                      "regla": "98102 sin cambio: caja pré-moldada de concreto con sifón (caixa de gordura Ø 0,4 m, h 0,4 m)",
                      "nota": "conserva concreto y sifón"},
                "B": {"partes": [P("97895", 1, "caixa enterrada de concreto pré-moldado 0,3×0,3×0,3 m con fondo y tapa")],
                      "regla": "97895 sin cambio: caja de concreto pré-moldada 0,3×0,3×0,3 m (sin sifón)",
                      "nota": "conserva el concreto, pierde el sifón"},
                "C": {"partes": [P("89708", 1, "caixa sifonada de PVC 150×185×75 mm en ramal de esgoto")],
                      "regla": "89708 sin cambio: caixa sifonada de PVC 150×185×75 mm",
                      "nota": "conserva el sifón, cambia a PVC"}},
            "etiquetas": {"A": "caja de concreto con sifón (caixa de gordura Ø 0,4)", "B": "caja de concreto 0,3×0,3×0,3 sin sifón",
                          "C": "caixa sifonada de PVC 150×185×75"},
            "recomendada": "A"},

        "IS030BR": {
            "pregunta": "La caja receptora pluvial de PVC 8\" × 40 cm no existe en el SINAPI; las cajas de PVC son 150×185×75 (con rejilla) y 250×230×75 (tapa ciega).",
            "grupo": "Cajas prefabricadas que el SINAPI no tiene",
            "opciones": {
                "A": {"partes": [P("89491", 1, "caixa sifonada de PVC 150×185×75 mm con rejilla, en ramal de agua pluvial")],
                      "regla": "89491 sin cambio: caja de PVC pluvial 150×185×75 mm con rejilla (la receta es de 200 mm × 40 cm)",
                      "nota": "caja pluvial más chica"},
                "B": {"partes": [P("89491", 1, "caixa de PVC en ramal de agua pluvial")],
                      "cambios": {"11714": ("ICD", "11880", 1, "caixa sifonada de PVC 250×230×75 mm con tapa ciega en lugar de la 150×185×75")},
                      "regla": "89491 con la caja cambiada por la de PVC 250×230×75 mm con tapa ciega (ICD 11880); M.O. SINAPI sin cambio",
                      "nota": "caja más grande, sin rejilla"},
                "C": None},
            "etiquetas": {"A": "caja PVC pluvial 150×185×75 con rejilla", "B": "caja PVC 250×230×75 con tapa ciega", "C": "dejar la receta actual"},
            "recomendada": "A"},

        "IS032BR": {
            "pregunta": "La cámara de inspección de polietileno Ø 60 cm no existe en el SINAPI (en polietileno sólo hay Ø 0,3 m para puesta a tierra): ¿se pasa a concreto?",
            "grupo": "Cajas prefabricadas que el SINAPI no tiene",
            "opciones": {
                "A": {"partes": [P("97897", 1, "caixa enterrada de concreto pré-moldado 0,6×0,6×0,5 m con fondo y tapa")],
                      "regla": "97897 sin cambio: caja de concreto pré-moldada 0,6×0,6×0,5 m con fondo y tapa",
                      "nota": "caja cuadrada de concreto con tapa"},
                "B": {"partes": [P("97974", 1, "poço de inspeção circular de concreto pré-moldado Ø 0,60 m, profundidad 0,90 m, sin tampão")],
                      "regla": "97974 sin cambio: pozo circular de concreto pré-moldado Ø 0,60 m, h 0,90 m (no incluye el tampão)",
                      "nota": "circular Ø 0,60 como el ítem, sin tapa"},
                "C": None},
            "etiquetas": {"A": "caja de concreto 0,6×0,6×0,5 con tapa", "B": "pozo circular de concreto Ø 0,60 sin tapa", "C": "dejar la receta actual"},
            "recomendada": "A"},

        "IS037BR": {
            "pregunta": ("Igual que IS036: ArqOn cotiza una bomba HIDRONEUMÁTICA de 2 HP (4237 estimado); el SINAPI sólo tiene bombas "
                         "centrífugas y salta de 1,5 CV a 3 CV."),
            "grupo": "Bombas de agua",
            "opciones": {"A": _bomba("102116", "1,5"), "B": _bomba("102118", "3"), "C": None},
            "etiquetas": {"A": "bomba centrífuga 1,5 CV + accesorios", "B": "bomba centrífuga 3 CV + accesorios", "C": "dejar la receta actual"},
            "recomendada": "C"},

        "IS040BR": {
            "pregunta": "El SINAPI no tiene caixa d'água de 600 L (hay 500 y 750 L).",
            "grupo": "Tanques de agua de una capacidad que el SINAPI no tiene",
            "opciones": {
                "A": _caixa("102605", 500, 600, "94704", "102593", "32 mm × 1\""),
                "B": _caixa("102606", 750, 600, "94704", "102593", "32 mm × 1\""),
                "C": {"partes": [P("102622", 1, "caixa d'água 500 L con tubos, conexiones, registros y torneira de boia (kit SINAPI)")],
                      "regla": "102622 sin cambio: kit SINAPI de 500 L con tubos, conexiones, 3 registros y torneira de boia",
                      "nota": "incluye tubería y registros que la receta no trae"}},
            "etiquetas": {"A": "500 L + accesorios", "B": "750 L + accesorios", "C": "kit SINAPI 500 L con tubería y registros"},
            "recomendada": "A"},

        "IS041BR": {
            "pregunta": "El SINAPI no tiene caixa d'água de 1200 L (hay 1000 y 1500 L).",
            "grupo": "Tanques de agua de una capacidad que el SINAPI no tiene",
            "opciones": {
                "A": _caixa("102607", 1000, 1200, "94705", "102595", "40 mm × 1 1/4\""),
                "B": _caixa("102608", 1500, 1200, "94705", "102595", "40 mm × 1 1/4\""),
                "C": {"partes": [P("102623", 1, "caixa d'água 1000 L con tubos, conexiones, registros y torneira de boia (kit SINAPI)")],
                      "regla": "102623 sin cambio: kit SINAPI de 1000 L con tubos, conexiones, 3 registros y torneira de boia",
                      "nota": "incluye tubería y registros que la receta no trae"}},
            "etiquetas": {"A": "1000 L + accesorios", "B": "1500 L + accesorios", "C": "kit SINAPI 1000 L con tubería y registros"},
            "recomendada": "A"},

        "IS042BR": {
            "pregunta": "El SINAPI no tiene caixa d'água de 2300 L (hay 2000 y 3000 L).",
            "grupo": "Tanques de agua de una capacidad que el SINAPI no tiene",
            "opciones": {
                "A": _caixa("102609", 2000, 2300, "94705", "102595", "40 mm × 1 1/4\""),
                "B": _caixa("102610", 3000, 2300, "94705", "102595", "40 mm × 1 1/4\"")},
            "etiquetas": {"A": "2000 L + accesorios", "B": "3000 L + accesorios"},
            "recomendada": "A"},
    }


    # ── NO_CONVIENE ─────────────────────────────────────────────────────────────────────────────────────────────────
    NO_CONVIENE = {}
    return LISTO, DECISION, NO_CONVIENE


# ── Inst. Sanitarias (2) ──
def _tablas_sanitarias2():
    LISTO, DECISION, NO_CONVIENE = {}, {}, {}
    # frag_sanitarias2.py — fase C (Brasil), grupo sanitarias2. Se ejecuta con P ya definido.
    # 22 ítems: IS043 IS044 IS045 IS046 IS047 IS048 IS049 IS050 IS059 IS061 IS062 IS063 IS064 IS065 IS067 IS071 IS072
    #           IS073 IS076 IS079 IS080 IS086


    # ── Ayudas ──────────────────────────────────────────────────────────────────────────────────────────────────────
    def _area(de, e):
        """Sección de pared de un tubo (proporcional a la masa por metro): (DE − e) × e."""
        return (de - e) * e


    def _f(de, e, de0, e0):
        return round(_area(de, e) / _area(de0, e0), 4)


    _GRUPO_PEAD = "Tubo PEAD: el SINAPI sólo publica SDR 11"
    _NOTA_PEAD = ("el tubo pasa de precio estimado a precio SINAPI (≈ 42 R$/kg de PEAD en todos los diámetros del ICD); la luva de "
                  "compresión de la receta (0,01 pieza/m) se omite: el ICD no la tiene en este diámetro")


    def _pead(base, sin_ccd, tubo_base, tubo_icd, de0, e0, de, e, sdr, mo, mo_txt, nota=_NOTA_PEAD):
        """Tubo PEAD por metro: composição `base` con el tubo valorado por masa por metro a DE × e, y la M.O. llevada al
        diámetro del ítem con la relación del propio SINAPI (M.O. proporcional al diámetro)."""
        f = _f(de, e, de0, e0)
        r = {"partes": [P(base, 1, f"tubo PEAD asentado, por metro; M.O. × {mo}: {mo_txt}", mo=mo)],
             "regla": (f"{base} con el tubo llevado a DE {de} × {e} mm (SDR {sdr}) por masa por metro: tubo ICD {tubo_icd} "
                       f"(DE {de0} × {e0} mm) × {f} = ({de} − {e}) × {e} ÷ [({de0} − {e0}) × {e0}]; M.O. × {mo} ({mo_txt}); "
                       f"sin la luva de compresión (0,01 pieza/m, no está en el ICD)"),
             "nota": nota}
        if sin_ccd:
            r["sin_ccd"] = {base: sin_ccd}
            r["cambios"] = {tubo_base: ("ICD", tubo_icd, f, f"tubo PEAD DE {de0} × {e0} mm (con precio en SP) valorado por masa "
                                                             f"por metro como DE {de} × {e} mm (SDR {sdr})")}
        else:
            r["escala"] = {tubo_base: (f, f"masa por metro: DE {de} × {e} mm (SDR {sdr}) ÷ DE {de0} × {e0} mm")}
        return r


    def _dec_pead(nombre, a, b, sdr_item, recomendada="A", extra=""):
        return {"pregunta": (f"{nombre}: el SINAPI sólo publica tubo PEAD SDR 11 (PN 12,5/16) y no tiene este diámetro/pared. "
                             f"¿Se valora el tubo con la pared del ítem (SDR {sdr_item}), se pasa a SDR 11 o queda la receta actual "
                             f"(como IS066)?{extra}"),
                "grupo": _GRUPO_PEAD,
                "opciones": {"A": a, "B": b, "C": None},
                "etiquetas": {"A": f"pared del ítem (SDR {sdr_item}), tubo SINAPI valorado por masa por metro",
                              "B": "tubo SDR 11 del mismo diámetro (la clase que publica el SINAPI)",
                              "C": "dejar la receta actual"},
                "recomendada": recomendada}


    _GRUPO_CAIXA = "Tanques de agua de una capacidad que el SINAPI no tiene"
    _GRUPO_FOSSA = "Fossa séptica de polietileno: capacidad que el SINAPI no tiene"
    _GRUPO_POZO = "Pozos de hormigón ciclópico o ladrillo (sumideros y pozos de visita)"
    _GRUPO_PVC = "Tubo de desagüe PVC «C-9» (clase que en Brasil no existe)"


    def _caixa_fibra(comp, litros):
        """Caixa d'água de fibra de vidrio de la misma capacidad + accesorios como el kit SINAPI 102623 (igual que IS040-IS042)."""
        return {
            "partes": [P(comp, 1, f"caixa d'água de poliéster reforzado con fibra de vidrio {litros} L con tapa, instalada (incluye guindaste)"),
                       P("94796", 1, "torneira de boia 3/4\" (la boia de la receta)"),
                       P("94703", 3, "3 adaptadores com flange 25 mm × 3/4\" (entrada, extravasor y limpieza), como el kit SINAPI"),
                       P("94705", 1, "1 adaptador com flange 40 mm × 1 1/4\" (salida), como el kit SINAPI 102623"),
                       P("102591", 3, "3 furos Ø 25 mm"),
                       P("102595", 1, "1 furo Ø 40 mm para la salida")],
            "regla": (f"{comp} (caixa de fibra de vidrio {litros} L: el SINAPI sólo trae polietileno hasta 3000 L) + accesorios como el kit "
                      f"SINAPI 102623: torneira de boia 94796, 4 adaptadores com flange (94703 × 3 + 94705) y sus 4 furos; sin tubos, "
                      f"conexiones ni registros (son de la instalación); M.O. y guindaste los de cada composição"),
            "nota": "el tanque y la boia pasan de precio estimado a precio SINAPI; la instalación SINAPI de 5000 L o más lleva guindaste",
        }


    def _fossa(icd, litros, comp_caixa, icd_caixa, litros_caixa, cemento, acero, extras, regla_extra):
        """Fossa séptica de PEAD del ICD colocada con la M.O. SINAPI de un tanque de polietileno de tamaño parecido, sobre la
        base de hormigón pobre armada de la receta del ítem."""
        v = round(cemento / 294.565, 4)
        return {
            "partes": [P(comp_caixa, 1, f"colocación de un tanque de polietileno de {litros_caixa} L (M.O. SINAPI), con el tanque cambiado por la fossa"),
                       P("96620", v, f"base de concreto magro: {cemento} kg de cemento de la receta ÷ 294,565 kg por m³ de lastro SINAPI = {v} m³"),
                       P("107280", acero, f"armadura de la base: {acero} kg de acero CA-50 de la receta")],
            "cambios": {icd_caixa: ("ICD", icd, 1, f"fossa séptica de PEAD de ≈ {litros} L (NBR 7229) en lugar de la caixa d'água de {litros_caixa} L")},
            "extras": extras,
            "regla": (f"fossa séptica de PEAD ≈ {litros} L (ICD {icd}) colocada con la M.O. de {comp_caixa} (tanque de polietileno de "
                      f"{litros_caixa} L; el SINAPI no publica la instalación de la fossa de PEAD) + base de la receta: 96620 × {v} m³ "
                      f"(lastro de concreto magro, por el cemento de la receta) + 107280 × {acero} kg (acero de la receta) + {regla_extra}"),
            "nota": "sube porque la fossa pasa de precio estimado a precio SINAPI (ICD), bastante más alto; la M.O. SINAPI es menor que la de la receta",
        }


    def _ext_pvc(adh, sol):
        return [("BR", "br_pegamento_l", adh, f"adhesivo para PVC de la receta ({adh} L, conexión de entrada y salida)"),
                ("BR", "br_limpiador_l", sol, f"solución limpiadora de la receta ({sol} L)")]


    def _ext_anel(n, receta):
        return [("BR", "br_anillo_de_goma_stp_4_pza", n, f"anillos de goma DN 100 de la receta ({receta} → {n})")]


    def _tanque_concreto():
        return {
            "partes": [P("98052", 1, "tanque séptico circular de concreto pré-moldado Ø 1,10 m, h 2,50 m, 2138 L, completo (Pza ↔ UN)")],
            "regla": ("98052 sin cambio: tanque séptico de anillos de concreto pré-moldado de 2138 L (el tamaño SINAPI más cercano), "
                      "en lugar del de polietileno"),
            "nota": "cambia el material: anillos de concreto en lugar de polietileno",
        }


    def _pv_premoldado(h, acrescimo, quitar_anel):
        signo = "+" if acrescimo > 0 else "−"
        r = {"partes": [P("102139", 1, "base de poço de visita Ø 1,20 m en concreto pré-moldado, profundidad 1,60 m (Pza ↔ UN)"),
                        P("97987", acrescimo, f"acréscimo por metro del mismo poço: {signo} {abs(acrescimo)} m para llegar a H = {h} m")],
             "regla": (f"102139 (base de PV Ø 1,20 m en concreto pré-moldado, prof. 1,60 m) {signo} 97987 × {abs(acrescimo)} m (acréscimo por "
                       f"metro del SINAPI) = profundidad {round(1.6 + acrescimo, 2)} m; anillos de concreto en lugar de hormigón ciclópico; sin tampão"),
             "nota": "cambia el material: anillos de concreto pré-moldado en lugar de hormigón ciclópico moldeado en obra"}
        if quitar_anel:
            r["quitar"] = {"12551": "el anillo sin fondo de 0,50 m: la base (1) menos 0,5 m de acréscimo (2 anillos/m) lo deja en cero"}
        return r


    def _pv_ciclopico(h):
        v = round(3.1416 * 0.8 ** 2 * 0.20 + 3.1416 * 1.4 * 0.20 * h, 3)
        f = round(3.1416 * 1.2 * h, 2)
        return {"partes": [P("102487", v, f"hormigón ciclópico: fondo Ø 1,60 × 0,20 m + pared e = 0,20 m × H {h} m = {v} m³ (Pza ↔ m³ por geometría)"),
                           P("96536", f, f"fôrma de la cara interior de la pared: π × 1,20 × {h} = {f} m² (la exterior va contra el terreno)"),
                           P("97740", 0.2592, "losa superior de concreto armado, como en la base de PV SINAPI 97988 (0,2592 m³)"),
                           P("97738", 0.0221, "pieza chica de la losa superior, como en la base de PV SINAPI (0,0221 m³)")],
                "regla": (f"por geometría, con pared y fondo de 0,20 m (SUPUESTO: el ítem no da el espesor): 102487 (concreto ciclópico fck 15, "
                          f"30 % pedra de mão) × {v} m³ + 96536 (fôrma) × {f} m² de cara interior + losa superior como la del PV SINAPI "
                          f"(97740 × 0,2592 + 97738 × 0,0221 m³); sin tampão"),
                "nota": "conserva el hormigón ciclópico del nombre; el espesor de 0,20 m es un supuesto"}


    _SIN_63 ="su insumo 44430 (tubo PEAD DE 63 SDR 11 PE-100) no está en el ICD 08/2026"
    _SIN_90 = "su insumo 44431 (tubo PEAD DE 90 SDR 11 PE-100) no está en el ICD 08/2026"
    _MO_LIG = "relación 104060 (DE 20) → 104061 (DE 32) de la ligação predial"
    _MO_REDE = "M.O. SINAPI proporcional al diámetro en la rede de PEAD (103373 DE 32, 103374 DE 63, 103375 DE 90)"


    # ── LISTO ───────────────────────────────────────────────────────────────────────────────────────────────────────
    LISTO = {
        "IS059BR": _pead("104060", None, "9813", "9813", 20, 2.3, 25, 2.3, 11, 1.2135,
                         "interpolada a DE 25 con la " + _MO_LIG,
                         nota=("sube porque la receta traía 0,011 h/m de M.O. y el SINAPI pone 0,18 h/m en la ligação predial "
                               "(igual que IS058/IS060 ya publicados); el tubo pasa de 4,33 estimado a 7,04")),

        "IS047BR": _fossa("39361", 1100, "102607", "34636", 1000, 20.5592, 4.0965, _ext_anel(2, "2,05"),
                          "2 anillos de goma DN 100 de la receta"),

        "IS076BR": {
            "partes": [P("95567", 1, "tubo de concreto simple DN 300 asentado, junta rígida; M.O. y equipo × 0,8132 (llevados a DN 250)",
                         mo=0.8132, eq=0.8132)],
            "escala": {"7796": (0.5, "mitad del tubo DN 300: precio del DN 250 interpolado entre DN 200 y DN 300")},
            "extras": [("ICD", "7778", 0.515, "mitad del tubo DN 200 PS1 ponta e bolsa (1,03 m/m × 0,5): interpolación DN 200 – DN 300")],
            "regla": ("95567 (tubo de concreto simple DN 300, junta rígida) llevado a DN 250 (10\"): tubo = promedio de los ICD 7778 "
                      "(DN 200) y 7796 (DN 300), 0,515 m de cada uno; M.O. y equipo × 0,8132 con la relación del SINAPI 95567 (DN 300) → "
                      "95568 (DN 400): 0,3132 → 0,4302 h de servente"),
            "nota": "el tubo pasa de 44,57 estimado a 62,39 (promedio SINAPI de DN 200 y DN 300); el SINAPI agrega la excavadora para bajar el tubo"},
    }


    # ── NECESITA_DECISION ───────────────────────────────────────────────────────────────────────────────────────────
    DECISION = {
        "IS061BR": _dec_pead(
            "PEAD 40 mm SDR 17 PN 10",
            _pead("104061", None, "9815", "9815", 32, 3.0, 40, 2.4, 17, 1.2258, "extrapolada a DE 40 con la " + _MO_LIG),
            _pead("104061", None, "9815", "9815", 32, 3.0, 40, 3.7, 11, 1.2258, "extrapolada a DE 40 con la " + _MO_LIG),
            17),
        "IS062BR": _dec_pead(
            "PEAD 50 mm SDR 17 PN 8",
            _pead("103374", _SIN_63, "44430", "44521", 50, 4.6, 50, 3.0, 17, 0.794, "interpolada a DE 50; " + _MO_REDE),
            _pead("103374", _SIN_63, "44430", "44521", 50, 4.6, 50, 4.6, 11, 0.794, "interpolada a DE 50; " + _MO_REDE),
            17),
        "IS063BR": _dec_pead(
            "PEAD 63 mm SDR 21 PN 6",
            _pead("103374", _SIN_63, "44430", "44524", 75, 6.9, 63, 3.0, 21, 1, "la de la composição (DE 63)"),
            _pead("103374", _SIN_63, "44430", "44524", 75, 6.9, 63, 5.8, 11, 1, "la de la composição (DE 63)"),
            21, extra=" La composição exacta 103374 (DE 63 SDR 11) no tiene costo en SP: falta su tubo en el ICD."),
        "IS064BR": _dec_pead(
            "PEAD 75 mm SDR 21",
            _pead("103375", _SIN_90, "44431", "44524", 75, 6.9, 75, 3.6, 21, 0.833, "interpolada a DE 75; " + _MO_REDE),
            _pead("103375", _SIN_90, "44431", "44524", 75, 6.9, 75, 6.9, 11, 0.833, "interpolada a DE 75; " + _MO_REDE),
            21),
        "IS065BR": _dec_pead(
            "PEAD 90 mm (el nombre no dice el SDR; su precio estimado corresponde a SDR 21, como IS063/IS064)",
            _pead("103375", _SIN_90, "44431", "44524", 75, 6.9, 90, 4.3, 21, 1, "la de la composição (DE 90)"),
            _pead("103375", _SIN_90, "44431", "44524", 75, 6.9, 90, 8.2, 11, 1, "la de la composição (DE 90)"),
            21, extra=" La composição exacta 103375 (DE 90 SDR 11) no tiene costo en SP: falta su tubo en el ICD."),

        "IS043BR": {
            "pregunta": "El SINAPI trae la caixa d'água de polietileno sólo hasta 3000 L; de 5000 L la tiene de fibra de vidrio: ¿se usa esa?",
            "grupo": _GRUPO_CAIXA,
            "opciones": {"A": _caixa_fibra("102617", 5000), "B": None},
            "etiquetas": {"A": "caixa de fibra de vidrio 5000 L + accesorios", "B": "dejar la receta actual"},
            "recomendada": "A"},
        "IS044BR": {
            "pregunta": "El SINAPI trae la caixa d'água de polietileno sólo hasta 3000 L; de 10 000 L la tiene de fibra de vidrio: ¿se usa esa?",
            "grupo": _GRUPO_CAIXA,
            "opciones": {"A": _caixa_fibra("102619", 10000), "B": None},
            "etiquetas": {"A": "caixa de fibra de vidrio 10 000 L + accesorios", "B": "dejar la receta actual"},
            "recomendada": "A"},

        "IS045BR": {
            "pregunta": "El SINAPI trae la fossa séptica de PEAD de ≈ 1100, 3000, 5500 y 10 000 L; el ítem es de 1200 L: ¿se usa la de ≈ 1100 L?",
            "grupo": _GRUPO_FOSSA,
            "opciones": {"A": _fossa("39361", 1100, "102607", "34636", 1000, 20.5137, 3.9198, _ext_pvc(0.04119, 0.07763),
                                     "adhesivo y solución limpiadora de la receta"),
                         "B": None},
            "etiquetas": {"A": "fossa de PEAD ≈ 1100 L (4 a 7 contribuyentes)", "B": "dejar la receta actual"},
            "recomendada": "A"},
        "IS046BR": {
            "pregunta": "El SINAPI trae la fossa séptica de PEAD de ≈ 1100 y 3000 L; el ítem es de 2300 L: ¿cuál la reemplaza?",
            "grupo": _GRUPO_FOSSA,
            "opciones": {"A": _fossa("39362", 3000, "102610", "43977", 3000, 20.4227, 4.0922, _ext_pvc(0.05119, 0.09778),
                                     "adhesivo y solución limpiadora de la receta"),
                         "B": _tanque_concreto(), "C": None},
            "etiquetas": {"A": "fossa de PEAD ≈ 3000 L (8 a 14 contribuyentes)", "B": "tanque séptico de concreto pré-moldado 2138 L",
                          "C": "dejar la receta actual"},
            "recomendada": "A"},
        "IS048BR": {
            "pregunta": "El SINAPI trae la fossa séptica de PEAD de ≈ 1100 y 3000 L; el ítem es de 2500 L: ¿cuál la reemplaza?",
            "grupo": _GRUPO_FOSSA,
            "opciones": {"A": _fossa("39362", 3000, "102610", "43977", 3000, 19.4345, 4.1151, _ext_anel(4, "4,11"),
                                     "4 anillos de goma DN 100 de la receta"),
                         "B": _tanque_concreto(), "C": None},
            "etiquetas": {"A": "fossa de PEAD ≈ 3000 L (8 a 14 contribuyentes)", "B": "tanque séptico de concreto pré-moldado 2138 L",
                          "C": "dejar la receta actual"},
            "recomendada": "A"},

        "IS049BR": {
            "pregunta": ("El SINAPI no tiene sumidero de hormigón ciclópico: trae el circular de anillos perforados Ø 1,88 m (h 2,00 m, por "
                         "unidad). ¿Se usa ése por metro, o se arma el de hormigón ciclópico por geometría (el ítem no da el espesor)?"),
            "grupo": _GRUPO_POZO,
            "opciones": {
                "A": {"partes": [P("98062", 0.5, "sumidouro circular pré-moldado Ø 1,88 m de 2,00 m de alto: 1 m de profundidad = 1/2 unidad")],
                      "regla": ("98062 × 0,5: sumidouro circular de anillos perforados de concreto Ø 1,88 m y 2,00 m de alto, por metro de "
                                "profundidad (1 ÷ 2,00 m); la tapa y el fondo de brita quedan prorrateados por metro"),
                      "nota": "cambia el material: anillos perforados pré-moldados en lugar de hormigón ciclópico"},
                "B": {"partes": [P("102487", 1.382, "pared de hormigón ciclópico e = 0,20 m, Ø interior 2,00 m: π × 2,20 × 0,20 = 1,382 m³ por metro"),
                                 P("96536", 6.28, "fôrma de la cara interior: π × 2,00 = 6,28 m² por metro (la exterior va contra el terreno)")],
                      "regla": ("por geometría, con pared de 0,20 m (SUPUESTO: el ítem no da el espesor): 102487 (concreto ciclópico fck 15, "
                                "30 % pedra de mão) × 1,382 m³/m + 96536 (fôrma) × 6,28 m²/m de cara interior; sin tapa ni fondo"),
                      "nota": "conserva el hormigón ciclópico del nombre; el espesor de 0,20 m es un supuesto"},
                "C": None},
            "etiquetas": {"A": "sumidero SINAPI de anillos perforados Ø 1,88 m, por metro", "B": "pared de hormigón ciclópico e = 20 cm, por geometría",
                          "C": "dejar la receta actual"},
            "recomendada": "A"},
        "IS050BR": {
            "pregunta": ("El SINAPI trae el sumidero de ladrillo macizo sólo rectangular (0,8 × 1,4 m, h 3,0 m, por unidad): ¿se lleva al "
                         "circular Ø 2 m por metro de profundidad con la razón de perímetros?"),
            "grupo": _GRUPO_POZO,
            "opciones": {
                "A": {"partes": [P("98078", 0.476, "sumidouro de tijolo maciço 0,8 × 1,4 × 3,0 m: por metro (1/3) × perímetro interior "
                                                   "π × 2,00 ÷ 4,40 m = 1,428")],
                      "regla": ("98078 × 0,476 = (1 ÷ 3,0 m de alto) × (perímetro interior 6,283 m del Ø 2 m ÷ 4,40 m del rectangular): pared de "
                                "tijolo maciço comum 5×10×20 de 20 cm con juntas abiertas; tapa, cinta y fondo quedan prorrateados"),
                      "nota": "pared de 20 cm de tijolo comum SINAPI en lugar de la de 12 cm de ladrillo de 18 huecos de la receta"},
                "B": None},
            "etiquetas": {"A": "sumidero SINAPI de tijolo maciço llevado a Ø 2 m por metro", "B": "dejar la receta actual"},
            "recomendada": "A"},

        "IS071BR": {
            "pregunta": ("El nombre dice cama de 5 cm por metro de tubería, pero la receta trae 1,13 m³ de tierra por metro (es una receta "
                         "por m³). El SINAPI la publica por m³ y con arena: ¿qué ancho de zanja se toma para el metro?"),
            "grupo": "Cama de asiento de tubería: ancho de zanja",
            "opciones": {
                "A": {"partes": [P("101618", 0.03, "cama de arena en fondo de zanja: 0,60 m de ancho × 0,05 m = 0,03 m³ por metro")],
                      "regla": ("101618 (preparo de fundo de vala < 1,5 m con camada de areia, lançamento manual, por m³) × 0,03 m³/m = "
                                "ancho 0,60 m × e 0,05 m; arena en lugar de tierra cernida (el SINAPI no tiene tierra cernida)"),
                      "nota": "baja porque la receta traía 1,13 m³ de tierra y 1,16 h por metro: cantidades de 1 m³, no de 1 m con e = 5 cm"},
                "B": {"partes": [P("101618", 0.05, "cama de arena en fondo de zanja: 1,00 m de ancho × 0,05 m = 0,05 m³ por metro")],
                      "regla": ("101618 (preparo de fundo de vala < 1,5 m con camada de areia, lançamento manual, por m³) × 0,05 m³/m = "
                                "ancho 1,00 m × e 0,05 m; arena en lugar de tierra cernida"),
                      "nota": "baja porque la receta traía 1,13 m³ de tierra y 1,16 h por metro: cantidades de 1 m³, no de 1 m con e = 5 cm"},
                "C": None},
            "etiquetas": {"A": "zanja de 0,60 m de ancho (0,03 m³/m)", "B": "zanja de 1,00 m de ancho (0,05 m³/m)", "C": "dejar la receta actual"},
            "recomendada": "A"},

        "IS072BR": {
            "pregunta": ("El SINAPI no tiene poço de visita de hormigón ciclópico: lo trae de anillos de concreto pré-moldado o de tijolo, "
                         "Ø 1,20 m, con base de 1,60 m y acréscimo por metro. ¿Anillos pré-moldados, o ciclópico por geometría?"),
            "grupo": _GRUPO_POZO,
            "opciones": {"A": _pv_premoldado(1, -0.5, True), "B": _pv_ciclopico(1), "C": None},
            "etiquetas": {"A": "PV SINAPI de anillos de concreto, profundidad 1,10 m", "B": "hormigón ciclópico e = 20 cm, por geometría",
                          "C": "dejar la receta actual"},
            "recomendada": "A"},
        "IS073BR": {
            "pregunta": ("El SINAPI no tiene poço de visita de hormigón ciclópico: lo trae de anillos de concreto pré-moldado o de tijolo, "
                         "Ø 1,20 m, con base de 1,60 m y acréscimo por metro. ¿Anillos pré-moldados, o ciclópico por geometría?"),
            "grupo": _GRUPO_POZO,
            "opciones": {"A": _pv_premoldado(2, 0.4, False), "B": _pv_ciclopico(2), "C": None},
            "etiquetas": {"A": "PV SINAPI de anillos de concreto, profundidad 2,00 m", "B": "hormigón ciclópico e = 20 cm, por geometría",
                          "C": "dejar la receta actual"},
            "recomendada": "A"},

        "IS079BR": {
            "pregunta": "La clase «C-9» no existe en Brasil: el PVC de desagüe predial es série normal o série R (reforzada). ¿Cuál para el 3\"?",
            "grupo": _GRUPO_PVC,
            "opciones": {
                "A": {"partes": [P("89713", 1, "tubo PVC série normal DN 75, esgoto predial, en ramal de esgoto, por metro")],
                      "regla": ("89713 sin cambio: tubo PVC série normal DN 75 mm (3\") instalado en ramal de esgoto sanitário; sin conexiones, "
                                "como la receta (el adhesivo y la solución van con las conexiones en el SINAPI)"),
                      "nota": "tubo de pared delgada (série normal)"},
                "B": {"partes": [P("89511", 1, "tubo PVC série R DN 75, en ramal de encaminhamento, por metro")],
                      "regla": ("89511 sin cambio: tubo PVC série R (reforzada) DN 75 mm (3\"); el SINAPI lo publica instalado en ramal de "
                                "encaminhamento de agua pluvial (el tubo ICD 9839 es para esgoto o pluvial); sin conexiones, como la receta"),
                      "nota": "tubo de pared gruesa (série R), el más parecido a una clase 9"},
                "C": None},
            "etiquetas": {"A": "PVC série normal DN 75", "B": "PVC série R (reforzada) DN 75", "C": "dejar la receta actual"},
            "recomendada": "A"},
        "IS080BR": {
            "pregunta": "La clase «C-9» no existe en Brasil: el PVC de desagüe predial es série normal o série R (reforzada). ¿Cuál para el 4\"?",
            "grupo": _GRUPO_PVC,
            "opciones": {
                "A": {"partes": [P("89714", 1, "tubo PVC série normal DN 100, esgoto predial, en ramal de esgoto, por metro")],
                      "regla": ("89714 sin cambio: tubo PVC série normal DN 100 mm (4\") instalado en ramal de esgoto sanitário; sin conexiones, "
                                "como la receta (el adhesivo y la solución van con las conexiones en el SINAPI)"),
                      "nota": "tubo de pared delgada (série normal)"},
                "B": {"partes": [P("89512", 1, "tubo PVC série R DN 100, en ramal de encaminhamento, por metro")],
                      "regla": ("89512 sin cambio: tubo PVC série R (reforzada) DN 100 mm (4\"); el SINAPI lo publica instalado en ramal de "
                                "encaminhamento de agua pluvial (el tubo ICD 9841 es para esgoto o pluvial); sin conexiones, como la receta"),
                      "nota": "tubo de pared gruesa (série R), el más parecido a una clase 9"},
                "C": None},
            "etiquetas": {"A": "PVC série normal DN 100", "B": "PVC série R (reforzada) DN 100", "C": "dejar la receta actual"},
            "recomendada": "A"},
    }


    # ── NO_CONVIENE ─────────────────────────────────────────────────────────────────────────────────────────────────
    NO_CONVIENE = {
        "IS067BR": ("la unión por termofusión no tiene costo SINAPI: la serie de junta soldada por termofusão empieza en DE 160 "
                    "(103443-103460) y no tiene costo en ninguna UF porque la máquina de soldar (103169/103170) no tiene precio; la de "
                    "eletrofusão (103463-103465) tampoco; además el SINAPI no publica tubo DE 125 ni SDR 21 (sólo SDR 11: 103376 DE 110, "
                    "103377 DE 160). Mismo criterio que IS068/IS069/IS070"),
        "IS086BR": ("el SINAPI 08/2026 no tiene bidê: no hay composição de instalación ni insumo en el ICD (buscado «BIDE»); usar 95469 "
                    "con la bacia sanitária (ICD 10420) como precio del bidê con grifería sería inventar el material principal"),
    }
    return LISTO, DECISION, NO_CONVIENE


# ── Obra Gruesa (1) ──
def _tablas_gruesa1():
    LISTO, DECISION, NO_CONVIENE = {}, {}, {}
    # frag_gruesa1.py — fase C, grupo gruesa1 (obra gruesa: juntas, baldrame, pavimentos, meio-fio, demoliciones, gabião)
    # Se ejecuta con P ya definido: P(composição, cantidad, "de dónde sale", mat=1, mo=1, eq=1)

    LISTO = {
        "OG027BR": {
            "partes": [P("101159", 0.625, "pilar 25 × 25 cm = 0,0625 m³ por metro ÷ 0,10 m³ por m² de la alvenaria de 10 cm = 0,625 m²")],
            "cambios": {"7258": ("ICD", "7260", 1, "tijolo maciço 6 × 12 × 24 cm, el de la receta del ítem, en lugar del 5 × 10 × 20")},
            "fijar": {"7260": (29, "piezas de la receta del ítem (28,75 → 29): 2 por hilada × 14,3 hiladas de 7 cm, con pérdida")},
            "regla": ("101159 (alvenaria de tijolo maciço, e = 10 cm) por volumen: 0,0625 m³/m ÷ 0,10 = 0,625 m² por metro de pilar; "
                      "tijolo 5×10×20 → 6×12×24 (ICD 7260) con las 29 piezas de la receta; argamassa y M.O. SINAPI por volumen "
                      "(el SINAPI no publica pilar de ladrillo ni otra alvenaria maciça para comparar)")},
        "OG028BR": {
            "partes": [P("94990", 0.05, "espesor 5 cm: 15 kg de cemento por m² de la receta ÷ 323 kg/m³ del concreto 94964 ≈ 0,046 m³ → 0,05 m³/m²")],
            "regla": ("94990 (passeio de concreto feito em obra, não armado, por m³) × 0,05 m³/m²: espesor 5 cm deducido del "
                      "cemento de la receta (15 kg/m²); misma base que OG036BR (94990 × 0,04)")},
        "OG030BR": {
            "partes": [P("98557", 0.5, "desarrollo del baldrame H = 30: 0,5 m² por metro (lo que cubre el polietileno de la receta, 0,49 m²)"),
                       P("97113", 0.5, "lona plástica colocada sobre el mismo desarrollo de 0,5 m² por metro")],
            "fijar": {"42408": (0.4891, "m² de polietileno de la receta del ítem")},
            "extras": [("ICD", "366", 0.009765, "arena fina de la receta del ítem")],
            "regla": ("98557 (emulsão asfáltica, 2 demãos) × 0,5 m²/m en lugar del alcatrão + 97113 (lona plástica) × 0,5 con los "
                      "0,4891 m² de polietileno de la receta + arena fina de la receta; M.O. SINAPI")},
        "OG044BR": {
            "partes": [P("97114", 1, "corte con cortadora de piso y disco diamantado para concreto/asfalto, por metro")],
            "regla": ("97114 tal cual (corte de junta con cortadora de piso, por metro): única composição SINAPI de corte por "
                      "metro; el disco del SINAPI es para concreto/asfalto"),
            "nota": ("baja porque el SINAPI corta a máquina (0,004 h de cortadora y 0,013 h de pedreiro + servente por metro); "
                     "la receta traía 0,061 h de oficial y ninguna máquina")},
        "OG045BR": {
            "partes": [P("103800", 0.15, "espesor 15 cm: 0,15 m³ de piedra por m² en la receta (0,1542 con la variación)")],
            "extras": [("ICD", "11615", 0.0255, "junta: 0,05105 placas de EPS 100 × 50 × 1 cm de la receta × 0,5 m²"),
                       ("ICD", "510", 0.02912, "sello de junta: asfalto oxidado en lugar del alcatrão, mismos kg de la receta")],
            "regla": ("103800 (pedra argamassada 1:3, por m³) × 0,15 m³/m² (espesor 15 cm por la piedra de la receta) + junta "
                      "de la receta: EPS 0,0255 m² y asfalto oxidado (ICD 510) por el alcatrão, 0,029 kg")},
        "OG046BR": {
            "partes": [P("104796", 1, "demolición de guía por metro")],
            "regla": ("104796 tal cual: el SINAPI sólo publica la demolición de guías mecanizada (martelete + compresor); "
                      "la receta era manual (0,57 h de servente)")},
        "OG047BR": {
            "partes": [P("97636", 20, "1 m³ ÷ 0,05 m = 20 m²: la misma conversión que usa el SINAPI en la 102098 (97636 × 20 por m³)")],
            "regla": ("97636 (demolição de pavimento asfáltico mecanizada, por m²) × 20 m²/m³ (capa de 5 cm): es el coeficiente "
                      "con que el propio SINAPI la lleva a m³ en la composição 102098"),
            "nota": ("sube mucho porque la receta traía 0,31 h de oficial y de rompedor por m³ (20 m² de capa); el SINAPI pone "
                     "por m³ 4,9 h de pedreiro, 1,0 h de cortadora y 0,65 h productivas de escavadeira")},
        "OG056BR": {
            "partes": [P("92757", 3.3333, "colchão de 0,30 m de altura: 1 m³ ÷ 0,30 m = 3,3333 m²")],
            "cambios": {"40452": ("ICD", "34383", 0.125, "colchão 4,0 × 2,0 × 0,30 m del ítem (pieza de 8 m²) en lugar del 5,0 × 2,0 × 0,30 por m²: 1 m² = 1/8 de pieza")},
            "quitar": {"4011": "el ítem no incluye geotextil (no está en su receta)"},
            "regla": ("92757 (gabião colchão h = 30 cm, por m²) × 3,3333 m²/m³ (1 ÷ 0,30 m); colchão 5×2×0,30 (m²) → pieza "
                      "4×2×0,30 del ítem (ICD 34383, 1/8 de pieza por m²); sin geotextil; M.O. y escavadeira SINAPI"),
            "nota": "sube por la escavadeira del SINAPI (1,6 h por m³) y el colchão SINAPI (R$ 624/m³ contra 219 de la receta)"},
    }

    DECISION = {
        "OG019BR": {
            "pregunta": ("La junta del ítem es de placa de EPS de 1 cm sellada con alcatrão (hoy R$ 8,82/m con 0,07 h de "
                         "pedreiro). El SINAPI sólo publica juntas con tarugo de polietileno y sellante (1,33 h de pedreiro por "
                         "metro). ¿Se conservan los materiales del ítem con la M.O. SINAPI, o se pasa a la junta SINAPI completa?"),
            "grupo": "Juntas con alcatrão: materiales del ítem o junta SINAPI",
            "opciones": {
                "A": {"partes": [P("98575", 1, "tratamiento de junta de dilatación, por metro")],
                      "quitar": {"44074": "primer de poliuretano: no corresponde al sello asfáltico",
                                 "44073": "tarugo de polietileno: el ítem rellena con placa de EPS",
                                 "142": "sellante PU: el ítem sella con alcatrão"},
                      "extras": [("ICD", "11615", 0.1021, "relleno: 0,2042 placas de EPS 100 × 50 × 1 cm de la receta × 0,5 m²"),
                                 ("ICD", "510", 0.512, "sello: asfalto oxidado en lugar del alcatrão, mismos kg de la receta")],
                      "regla": ("98575 (junta de dilatación) con los materiales del ítem: EPS 1 cm 0,1021 m²/m por el tarugo y "
                                "asfalto oxidado (ICD 510) 0,512 kg/m por el sellante PU y su primer; M.O. SINAPI sin cambio"),
                      "nota": "sube porque el SINAPI pone 1,33 h de pedreiro y 0,27 h de servente por metro de junta; la receta traía 0,07 h de cada uno"},
                "B": {"partes": [P("98575", 1, "tratamiento de junta de dilatación con tarugo y sellante PU, por metro")],
                      "regla": "98575 tal cual: junta de dilatación con tarugo de polietileno y sellante PU (cambia los materiales del ítem)",
                      "nota": "sube por la M.O. SINAPI (1,33 h de pedreiro por metro) y el sellante PU (R$ 21/m)"},
                "C": None},
            "etiquetas": {"A": "EPS + asfalto oxidado (materiales del ítem), M.O. SINAPI",
                          "B": "junta SINAPI: tarugo de polietileno + sellante PU",
                          "C": "dejar la receta actual"},
            "recomendada": "A"},
        "OG052BR": {
            "pregunta": ("La junta del ítem se rellena con alcatrão (hoy R$ 4,92/m con 0,13 h de servente). El SINAPI sólo "
                         "publica la junta serrada con tarugo y sellante de silicona (1,17 h de pedreiro por metro). ¿Se conserva "
                         "el sello asfáltico con la M.O. SINAPI, o se pasa a la junta SINAPI completa?"),
            "grupo": "Juntas con alcatrão: materiales del ítem o junta SINAPI",
            "opciones": {
                "A": {"partes": [P("98577", 1, "tratamiento de junta de pavimento, por metro")],
                      "quitar": {"44073": "tarugo de polietileno: el ítem no lo lleva",
                                 "43142": "sellante de silicona: el ítem sella con alcatrão"},
                      "extras": [("ICD", "510", 0.1261, "sello: asfalto oxidado en lugar del alcatrão, mismos kg de la receta")],
                      "regla": ("98577 (junta de pavimento) con el material del ítem: asfalto oxidado (ICD 510) 0,1261 kg/m por el "
                                "tarugo y el sellante de silicona; M.O. SINAPI sin cambio (la receta no trae arena)"),
                      "nota": "sube porque el SINAPI pone 1,17 h de pedreiro y 0,24 h de servente por metro de junta; la receta traía 0,13 h de servente"},
                "B": {"partes": [P("98577", 1, "tratamiento de junta serrada con tarugo y sellante de silicona, por metro")],
                      "regla": "98577 tal cual: junta serrada con tarugo de polietileno y sellante de silicona (cambia el material del ítem)",
                      "nota": "sube por la M.O. SINAPI (1,17 h de pedreiro por metro) y el sellante de silicona (R$ 8/m)"},
                "C": None},
            "etiquetas": {"A": "asfalto oxidado (material del ítem), M.O. SINAPI",
                          "B": "junta SINAPI: tarugo + sellante de silicona",
                          "C": "dejar la receta actual"},
            "recomendada": "A"},
        "OG031BR": {
            "pregunta": ("El nombre dice «com Manta Asfáltica (Asfaltex)», pero la receta es pintura asfáltica (0,15 kg de tinta "
                         "por metro, sin manta): el Asfaltex boliviano es una pintura. ¿Qué es el ítem? (si es pintura, el nombre "
                         "en portugués confunde y queda casi igual a OG030BR)"),
            "grupo": "Baldrame «com manta asfáltica»: ¿pintura o manta?",
            "opciones": {
                "A": {"partes": [P("98557", 0.5, "desarrollo del baldrame H = 30: 0,5 m² por metro, igual que OG030BR")],
                      "extras": [("ICD", "366", 0.009717, "arena fina de la receta del ítem")],
                      "regla": ("98557 (emulsão asfáltica, 2 demãos) × 0,5 m²/m por la tinta asfáltica de la receta + arena fina "
                                "de la receta; M.O. SINAPI")},
                "B": {"partes": [P("98546", 0.5, "desarrollo del baldrame H = 30: 0,5 m² por metro, igual que OG030BR")],
                      "regla": "98546 (manta asfáltica 4 mm, una capa, con primer) × 0,5 m²/m de desarrollo del baldrame H = 30; M.O. SINAPI",
                      "nota": "sube porque la manta de 4 mm (R$ 73/m²) reemplaza 0,15 kg de pintura"}},
            "etiquetas": {"A": "pintura asfáltica, como la receta (emulsão, 2 demãos)",
                          "B": "manta asfáltica de 4 mm, como el nombre"},
            "recomendada": "A"},
        "OG037BR": {
            "pregunta": ("El nombre dice «Blocos Intertravados», pero la receta es de paralelepípedos de piedra (22,5 piezas por "
                         "m², el «adoquín Comanche» boliviano). ¿Qué es el ítem? (OG050BR y OG051BR ya son intertravados de "
                         "10 cm, sextavado y 16 faces)"),
            "grupo": "Pavimento de rua: ¿paralelepípedo o bloco intertravado?",
            "opciones": {
                "A": {"partes": [P("101167", 1, "pavimento de paralelepípedos rejuntado con pó de pedra, por m²")],
                      "regla": ("101167 tal cual: paralelepípedo granítico (33 piezas/m² del SINAPI, no las 22,5 del adoquín "
                                "boliviano) sobre arena, rejunte con pó de pedra; M.O. y rolo SINAPI")},
                "B": {"partes": [P("92400", 1, "piso intertravado retangular 20 × 10 cm, e = 10 cm, por m²")],
                      "regla": "92400 tal cual: bloco de concreto retangular 20 × 10 cm, e = 10 cm (tráfico de calle, como OG050BR y OG051BR)"},
                "C": {"partes": [P("92398", 1, "piso intertravado retangular 20 × 10 cm, e = 8 cm, por m²")],
                      "regla": "92398 tal cual: bloco de concreto retangular 20 × 10 cm, e = 8 cm (tráfico liviano)"}},
            "etiquetas": {"A": "paralelepípedo de piedra, como la receta",
                          "B": "bloco intertravado de concreto 20 × 10, e = 10 cm",
                          "C": "bloco intertravado de concreto 20 × 10, e = 8 cm"},
            "recomendada": "A"},
        "OG042BR": {
            "pregunta": ("La placa es de E = 17 cm pero la receta trae 0,08 m³ de hormigón por m² (menos de la mitad) y 10 kg de "
                         "acero en barras. El pavimento armado SINAPI de 17,5 cm lleva 0,19 m³ de concreto C30 y 6,2 kg de telas "
                         "soldadas más las barras de junta. ¿Se pasa a la placa SINAPI llevada a 17 cm?"),
            "grupo": "Pavimento rígido E = 17 cm: receta incoherente con el espesor",
            "opciones": {
                "A": {"partes": [P("97112", 1, "pavimento de concreto armado e = 17,5 cm, por m²")],
                      "escala": {"34494": (0.9714, "espesor 17 cm ÷ 17,5 cm")},
                      "regla": ("97112 (PCA, fck 30, e = 17,5 cm) llevado a 17 cm: concreto × 17/17,5; armadura (telas Q-196 y Q-159, "
                                "barras de junta), fôrmas y M.O. SINAPI sin cambio (97111 de 15 cm y 97112 de 17,5 cm tienen la misma M.O.)")},
                "B": {"partes": [P("97112", 1, "pavimento de concreto armado e = 17,5 cm, por m²")],
                      "cambios": {"34494": ("ICD", "34493", 0.9714, "concreto C25 de la receta (H-25) en lugar del C30; espesor 17 cm ÷ 17,5 cm")},
                      "regla": ("97112 (PCA, e = 17,5 cm) llevado a 17 cm y a concreto C25 como la receta (ICD 34494 → 34493, × 17/17,5); "
                                "armadura, fôrmas y M.O. SINAPI sin cambio")},
                "C": None},
            "etiquetas": {"A": "placa SINAPI a 17 cm, concreto C30 (el del SINAPI)",
                          "B": "placa SINAPI a 17 cm, concreto C25 (el de la receta)",
                          "C": "dejar la receta actual (0,08 m³/m²)"},
            "recomendada": "A"},
        "OG043BR": {
            "pregunta": ("El meio-fio de 20 × 40 cm es vaciado en obra con encofrado y hormigón hecho en obra. El SINAPI sólo "
                         "publica la guía moldada con extrusora (13 × 22 y 15 × 30 cm) o prefabricada. ¿Se adapta la guía con "
                         "extrusora a la sección 20 × 40, o se arma por partes (hormigón en obra + fôrma) como en el hormigón armado?"),
            "grupo": "Meio-fio vaciado en obra: extrusora SINAPI o fôrma + hormigón",
            "opciones": {
                "A": {"partes": [P("94265", 1, "guía moldada in loco con extrusora 15 × 30 cm, por metro", mo=1.139, eq=1.241)],
                      "cambios": {"34492": ("COMP", "94965", 1.7778, "hormigón hecho en obra (fck 25, betoneira) en lugar del usinado; sección 20 × 40 ÷ 15 × 30 = 0,08 ÷ 0,045")},
                      "regla": ("94265 (guía con extrusora 15 × 30) llevada a 20 × 40: concreto × 1,7778 (0,08 ÷ 0,045 m²) y hecho en "
                                "obra (94965); M.O. × 1,139 y extrusora × 1,241 extrapolando la relación SINAPI entre 94263 (13 × 22) "
                                "y 94265 (15 × 30); sin la piedra desplazadora de la receta")},
                "B": {"partes": [P("94965", 0.08824, "hormigón hecho en obra: 0,20 × 0,40 = 0,08 m³ por metro × 1,103"),
                                 P("103670", 0.08, "lançamento con baldes, adensamento y acabado: 0,08 m³ por metro"),
                                 P("96536", 0.8, "fôrma de las dos caras: 2 × 0,40 m = 0,8 m² por metro")],
                      "regla": ("por partes, como el hormigón armado de la fase B: 94965 × 0,08824 (0,08 m³ × 1,103) + 103670 × 0,08 "
                                "(lançamento) + 96536 × 0,8 m² (fôrma de viga baldrame, 2 caras de 0,40 m); sin la piedra "
                                "desplazadora de la receta")}},
            "etiquetas": {"A": "guía con extrusora SINAPI llevada a 20 × 40",
                          "B": "hormigón en obra + fôrma de madera (como la receta)"},
            "recomendada": "B"},
        "OG053BR": {
            "pregunta": ("El SINAPI no tiene adoquín cerámico (el «Pavic» es un producto boliviano) y la receta trae 12,9 piezas "
                         "de 20 × 10 cm por m² (cubren 0,26 m²). ¿Con qué pieza se arma el ítem?"),
            "grupo": "Bloquete cerámico Pavic: no existe en el SINAPI",
            "opciones": {
                "A": {"partes": [P("92397", 1, "piso intertravado retangular 20 × 10 cm, e = 6 cm, por m²")],
                      "cambios": {"36155": ("ICD", "7258", 47.8, "tijolo cerâmico maciço 5 × 10 × 20 colocado de plano, junta de arena de 3 mm: 1 ÷ (0,203 × 0,103) = 47,8 piezas por m²")},
                      "fijar": {"7258": (48, "piezas al entero: 47,8 × 1,0041 de pérdida SINAPI = 48")},
                      "regla": ("92397 (intertravado 20 × 10, e = 6 cm) con pieza cerámica: bloquete de concreto → tijolo cerâmico maciço "
                                "5 × 10 × 20 (ICD 7258), 48 piezas/m² con junta de 3 mm; arena, equipo y M.O. SINAPI"),
                      "nota": "baja porque el tijolo maciço común cuesta R$ 0,60 la pieza y la M.O. SINAPI es 0,20 h de calceteiro y de servente (la receta traía 1,4 y 1,6 h)"},
                "B": {"partes": [P("92397", 1, "piso intertravado retangular 20 × 10 cm, e = 6 cm, por m²")],
                      "regla": "92397 tal cual: bloquete de concreto retangular 20 × 10 cm, e = 6 cm (misma forma y colocación; cambia cerámica por concreto)"},
                "C": None},
            "etiquetas": {"A": "tijolo cerâmico maciço 5 × 10 × 20 de plano (sigue siendo cerámico)",
                          "B": "bloquete de concreto 20 × 10, e = 6 cm (SINAPI tal cual)",
                          "C": "dejar la receta actual"},
            "recomendada": "B"},
    }

    NO_CONVIENE = {
    }

    # ── Revisión del coordinador ──
    # OG047BR: el espesor de la capa no sale del ítem (está por m³) y el costo cambia 24 veces → decisión.
    _og047 = LISTO.pop("OG047BR")
    DECISION["OG047BR"] = {
        "pregunta": ("El SINAPI demuele el pavimento asfáltico por m² (97636) y el ítem es por m³: hay que fijar el espesor de la capa. "
                     "Con cualquier espesor el costo sube mucho: la receta traía 0,31 h de oficial y de rompedor por m³"),
        "grupo": "Pavimento: corte y demolición",
        "opciones": {
            "A": _og047,
            "B": {"partes": [P("97636", 10, "1 m³ ÷ 0,10 m = 10 m²")],
                  "regla": "97636 (demolição de pavimento asfáltico mecanizada, por m²) × 10 m²/m³ (capa de 10 cm)",
                  "nota": "sube porque el SINAPI pone por m³ 2,4 h de pedreiro más cortadora y escavadeira contra 0,31 h de la receta"},
            "C": None},
        "etiquetas": {"A": "capa de 5 cm (20 m²/m³, el coeficiente de la composição SINAPI 102098)", "B": "capa de 10 cm (10 m²/m³)",
                      "C": "dejar la receta actual (ya usa sólo hojas SINAPI)"},
        "recomendada": "A"}
    # OG044BR: 97114 es el corte de juntas de contracción en pavimento de CONCRETO (corte parcial); aplicarlo al corte de capa
    # asfáltica es la composição más cercana, pero no el mismo servicio → decisión, junto con OG081BR (corte de pavimento rígido).
    _og044 = LISTO.pop("OG044BR")
    DECISION["OG044BR"] = {
        "pregunta": ("El SINAPI no tiene corte de capa asfáltica por metro; la composição más cercana es 97114 (corte de juntas de "
                     "contracción en pavimento de concreto, con cortadora de piso). La receta actual sólo trae 0,061 h de oficial, sin máquina"),
        "grupo": "Pavimento: corte y demolición",
        "opciones": {
            "A": _og044,
            "B": {"partes": [P("97114", 1, "corte con cortadora de piso, por metro")],
                  "fijar": {"C:91283": (0.0613, "cortadora (CHP) con las 0,0613 h/m de la receta"),
                            "C:88309": (0.0613, "pedreiro con las 0,0613 h/m de la receta")},
                  "quitar": {"C:91285": "hora improductiva de la cortadora: se toma la hora de la receta como productiva",
                             "C:88316": "servente: la receta no lo trae"},
                  "regla": "cortadora de piso (CHP 91283) y pedreiro de la 97114 con las 0,0613 h por metro de la receta (propuesta del análisis)"},
            "C": None},
        "etiquetas": {"A": "97114 tal cual (productividad SINAPI del corte de juntas)", "B": "cortadora + pedreiro con las horas de la receta",
                      "C": "dejar la receta actual (sólo M.O., con precio SINAPI)"},
        "recomendada": "A"}
    return LISTO, DECISION, NO_CONVIENE


# ── Obra Gruesa (2) ──
def _tablas_gruesa2():
    LISTO, DECISION, NO_CONVIENE = {}, {}, {}
    # frag_gruesa2.py — fase C, grupo gruesa2 (se ejecuta con P ya definido)
    LISTO = {
        "OG054BR": {
            "partes": [P("96386", 1, "execução e compactação de corpo de aterro, camadas de 15 cm (m³ compactado; el SINAPI excluye el material)")],
            "cambios": {"C:96463": ("CCD", "5684", 1, "rolo de pneus → rolo vibratório de um cilindro aço liso (el del ítem), CHP, mismas horas"),
                        "C:96464": ("CCD", "5685", 1, "idem, CHI (horas improductivas)")},
            "extras": [("ICD", "6081", 1.2753, "suelo de aporte de la receta del ítem: 1,2753 m³ sueltos por m³ compactado (argila/barro para aterro, com transporte até 10 km)")],
            "regla": "96386 (corpo de aterro compactado, camadas 15 cm) con el rolo de pneus cambiado por rolo liso vibratório (5684/5685, mismas horas) + 1,2753 m³ de suelo de aporte de la receta (ICD 6081); M.O., motoniveladora y caminhão pipa SINAPI sin cambio",
            "nota": "baja porque el SINAPI compacta con equipo de terraplén (0,015 h de rolo y 0,015 h de servente por m³) y la receta ArqOn traía 0,31 h de rolo y 1,38 h de servente; el 90 % del costo nuevo es el suelo"},
        "OG072BR": {
            "partes": [P("89714", 1, "tubo PVC série normal DN 100 mm fornecido e instalado, por metro")],
            "regla": "89714 (tubo PVC esgoto série normal DN 100, el mismo tubo ICD 9836 de la receta) sin cambio de cantidades, usado como tubo de drenaje; el SINAPI no publica tubo de drenaje de PVC liso por metro (102724 barbacã es por unidad de 0,5 m con brita y geotêxtil; 106545 es PEAD corrugado)"},
        "OG073BR": {
            "partes": [P("94265", 1, "guia (meio-fio) moldada in loco 15 × 30 cm, por metro", mat=1.1667, mo=1.03, eq=1.06)],
            "cambios": {"34492": ("COMP", "94964", 1, "el ítem hace el hormigón en obra con betoneira: concreto usinado C20 → concreto fck 20 em betoneira 400 L, mismo volumen")},
            "regla": "94265 (guia 15 × 30 cm) llevado a 15 × 35 cm: materiales × 35/30 = 1,1667 (concreto 0,0533 → 0,0622 m³/m); M.O. × 1,03 y equipo × 1,06 extrapolando la relación SINAPI entre 94263 (13 × 22) y 94265 (15 × 30); concreto usinado C20 cambiado por 94964 (fck 20 en betoneira). Queda la extrusora del SINAPI en lugar del encofrado de madera"},
        "OG074BR": {
            "partes": [P("100322", 0.1232, "lastro granular (m³): 0,1466 m³ de piedra de la receta ÷ 1,19 m³ de piedra por m³ de lastro SINAPI = 0,1232 m³/m² (e ≈ 12 cm)")],
            "cambios": {"4722": ("ICD", "4730", 1, "brita n.º 3 → pedra de mão (rachão), el insumo SINAPI que ya tiene la receta; mismo volumen")},
            "regla": "100322 (lastro com material granular, m³) × 0,1232 m³/m² (e ≈ 12 cm, sale de los 0,1466 m³ de piedra de la receta ÷ 1,19) con la brita n.º 3 cambiada por pedra de mão ICD 4730; M.O. y placa vibratória SINAPI"},
        "OG075BR": {
            "partes": [P("94990", 0.07, "passeio de concreto feito em obra, não armado (m³): e = 7 cm → 0,07 m³ por m²")],
            "regla": "94990 (passeio/calçada de concreto feito em obra, não armado, por m³) × 0,07 m³/m² (e = 7 cm del nombre); incluye sarrafos de guía y desmoldante que trae el SINAPI",
            "nota": "sube porque el SINAPI usa concreto fck 20 (323 kg de cemento/m³ y 1,23 m³ de concreto por m³ colocado) y la receta ArqOn traía 180 kg/m³"},
        "OG076BR": {
            "partes": [P("94263", 1, "guia (meio-fio) moldada in loco 13 × 22 cm, por metro", mat=1.049)],
            "cambios": {"34492": ("COMP", "94964", 1, "el ítem hace el hormigón en obra con betoneira y pide R = 180 kg/cm²: concreto usinado C20 → concreto fck 20 em betoneira 400 L, mismo volumen")},
            "regla": "94263 (guia 13 × 22 cm = 286 cm²) llevado a 10 × 30 cm = 300 cm²: materiales × 300/286 = 1,049; M.O. y equipo SINAPI sin cambio (entre 94263 y 94265 el SINAPI la sube 6 % para 57 % más de sección: acá sería +0,5 %); concreto usinado C20 cambiado por 94964 (fck 20 en betoneira ≈ R 180). Se omite la placa de EPS de junta (menor)"},
        "UH012BR": {
            "partes": [P("95240", 1, "lastro de concreto magro e = 3 cm, por m² (la receta trae 0,0204 m³ de brita ≈ 0,0197 del SINAPI de 3 cm)"),
                       P("100322", 0.0863, "lastro granular (m³): 0,1027 m³ de piedra de la receta ÷ 1,19 = 0,0863 m³/m² (e ≈ 9 cm)")],
            "cambios": {"4722": ("ICD", "4730", 1, "brita n.º 3 → pedra de mão (rachão), el insumo SINAPI que ya tiene la receta; mismo volumen")},
            "regla": "lastro de pedra de mão = 100322 × 0,0863 m³/m² (0,1027 m³ de piedra de la receta ÷ 1,19; brita 3 → ICD 4730) + capa de concreto = 95240 (lastro de concreto magro 3 cm; el volumen de concreto sale de la brita de la receta)"},
        "OT021BR": {
            "partes": [P("102358", 1, "desmonte de material de 3ª categoria com emulsão explosiva, m³ (exclusive carga e transporte)")],
            "sin_ccd": {"102358": "sin costo publicado porque la broca conificada ICD 44271 no está en el ICD 08/2026; se arma desde sus líneas"},
            "quitar": {"44271": "broca conificada 32 mm: no está en el ICD 08/2026 (sin precio en ninguna UF) y el ICD no tiene otro bit de martillo manual; 0,0006 un/m³, incidencia menor al 1 %"},
            "regla": "102358 (desmonte de 3ª categoria con emulsão explosiva) armada desde sus líneas, sin la broca conificada 44271 (0,0006 un/m³, sin precio en el ICD); todo lo demás SINAPI sin cambio",
            "nota": "baja porque el SINAPI perfora con perfuratriz hidráulica sobre esteira (0,15 h de servente por m³) y la receta ArqOn traía 2,7 h de M.O. y 0,22 h de compresor y perforadora"},
    }
    DECISION = {
        "OG057BR": {
            "pregunta": "Alvenaria de pedra cortada: el SINAPI no tiene piedra cortada 20×20×20 (sólo pedra de mão/rachão) y la receta trae 5,86 m³ de piedra por m³. ¿Pasa a pedra argamassada de rachão?",
            "grupo": "Piedra labrada (el SINAPI sólo tiene rachão)",
            "opciones": {
                "A": {"partes": [P("103800", 1, "pedra argamassada com cimento e areia 1:3, 40 % de argamassa, m³")],
                      "regla": "103800 (pedra de mão argamassada 1:3, 40 % de mortero, 0,91 m³ de rachão por m³) sin cambio: rachão en lugar de piedra cortada 20×20×20"},
                "B": None},
            "etiquetas": {"A": "pedra de mão (rachão) argamassada, SINAPI 103800", "B": "dejar la receta actual (piedra cortada con precio estimado, 5,86 m³ por m³)"},
            "recomendada": "A"},
        "OG059BR": {
            "pregunta": "Bloco de pedra aparelhada tipo A 60×40×30 por pieza: el SINAPI no tiene cantaria y la receta trae 5 piezas por pieza (parece hecha por m² de cara). ¿Se adapta como pedra argamassada por el volumen de la pieza o queda como está hasta corregir la unidad?",
            "grupo": "Piedra labrada (el SINAPI sólo tiene rachão)",
            "opciones": {
                "A": {"partes": [P("103800", 0.072, "pedra argamassada (m³): volumen de una pieza 0,60 × 0,40 × 0,30 = 0,072 m³")],
                      "regla": "103800 (pedra de mão argamassada) × 0,072 m³ por pieza (0,60 × 0,40 × 0,30): rachão en lugar del sillar labrado",
                      "nota": "baja porque la receta ArqOn traía 5,06 piezas por pieza y el rachão SINAPI vale R$ 81,87/m³ (R$ 5,4 por pieza) contra R$ 52,73 estimado por sillar"},
                "B": None},
            "etiquetas": {"A": "pedra argamassada de rachão × 0,072 m³ (subvalora el sillar labrado)", "B": "dejar la receta actual y corregir aparte la unidad (5 piezas por pieza)"},
            "recomendada": "B"},
        "OG060BR": {
            "pregunta": "Bloco de pedra aparelhada tipo B 40×40×30 por pieza (el insumo dice 40×30×30): el SINAPI no tiene cantaria y la receta trae 8 piezas por pieza. ¿Se adapta como pedra argamassada por el volumen de la pieza o queda como está hasta corregir la unidad?",
            "grupo": "Piedra labrada (el SINAPI sólo tiene rachão)",
            "opciones": {
                "A": {"partes": [P("103800", 0.048, "pedra argamassada (m³): volumen de una pieza 0,40 × 0,40 × 0,30 = 0,048 m³ (medidas del nombre)")],
                      "regla": "103800 (pedra de mão argamassada) × 0,048 m³ por pieza (0,40 × 0,40 × 0,30 del nombre): rachão en lugar del sillar labrado",
                      "nota": "baja porque la receta ArqOn traía 8,17 piezas por pieza y el rachão SINAPI vale R$ 81,87/m³ contra R$ 36,41 estimado por sillar"},
                "B": None},
            "etiquetas": {"A": "pedra argamassada de rachão × 0,048 m³ (subvalora el sillar labrado)", "B": "dejar la receta actual y corregir aparte la unidad (8 piezas por pieza)"},
            "recomendada": "B"},
        "UH001BR": {
            "pregunta": "Locação da obra es un global y el SINAPI la mide por metro de gabarito: ¿cuántos metros de gabarito vale 1 global?",
            "grupo": "Global ↔ metro de gabarito",
            "opciones": {
                "A": {"partes": [P("99059", 10, "locação convencional com gabarito de tábuas corridas (m): 10 m por global = 14,4 h de M.O. de la receta ÷ 1,45 h/m del SINAPI")],
                      "regla": "99059 (locação com gabarito, pontaletes a cada 2 m) × 10 m de gabarito por global (las 14,4 h de M.O. de la receta ÷ 1,45 h/m)"},
                "B": None,
                "C": {"partes": [P("99059", 2.7, "locação convencional com gabarito (m): 2,7 m por global = 0,0161 m³ de madera de la receta ÷ 0,00595 m³/m del SINAPI")],
                      "regla": "99059 (locação com gabarito, pontaletes a cada 2 m) × 2,7 m de gabarito por global (los 6,83 p² = 0,0161 m³ de madera de la receta ÷ 0,00595 m³/m)",
                      "nota": "baja porque 2,7 m de gabarito llevan 3,9 h de M.O. SINAPI y la receta ArqOn traía 14,4 h"}},
            "etiquetas": {"A": "10 m de gabarito por global (por la M.O. de la receta)", "B": "dejar la receta actual (todas sus líneas ya tienen precio SINAPI)",
                          "C": "2,7 m de gabarito por global (por la madera de la receta)"},
            "recomendada": "A"},
        "UH022BR": {
            "pregunta": "Estaca de concreto armado por metro: la receta trae las cantidades de 1 m³ (350 kg de cemento, 80 kg de acero, encofrado) y no dice diámetro ni tipo. ¿Qué estaca es?",
            "grupo": "Estaca sin diámetro ni tipo",
            "opciones": {
                "A": {"partes": [P("101176", 1, "estaca broca Ø 30 cm, escavação manual, inteiramente armada, por metro")],
                      "regla": "101176 (estaca broca de concreto Ø 30 cm, trado manual, inteiramente armada: 0,087 m³ de concreto y 4,95 kg de acero por metro) sin cambio",
                      "nota": "baja porque la receta ArqOn traía por metro las cantidades de 1 m³ de hormigón armado (una estaca Ø 30 tiene 0,07 m³ por metro)"},
                "B": {"partes": [P("100656", 1, "estaca pré-moldada de concreto seção quadrada 16 × 16 cm, 25 t, cravada, por metro")],
                      "regla": "100656 (estaca pré-moldada de concreto armado 16 × 16 cm, 25 t, cravada con bate-estacas, inclusive emenda) sin cambio",
                      "nota": "baja porque la receta ArqOn traía por metro las cantidades de 1 m³ de hormigón armado"}},
            "etiquetas": {"A": "estaca broca Ø 30 cm hecha en obra, inteiramente armada", "B": "estaca pré-moldada 16 × 16 cm cravada (25 t)"},
            "recomendada": "A"},
    }
    NO_CONVIENE = {
        "OG081BR": "el SINAPI no tiene composição de corte de pavimento o piso de concreto por metro (la cortadora de piso 91283 sólo aparece dentro de passeio intertravado y demolição de asfalto, por m²; 98577 es sólo el sellado de la junta) y la receta actual ya usa únicamente hojas SINAPI con precio SP (servente 88316 y cortadora de piso CHP 91283)",
    }

    # ── Revisión del coordinador ──
    # OG081BR: el SINAPI 08/2026 sí trae un corte de pavimento de concreto por metro (97114, juntas de contracción, AF_08/2026);
    # es corte parcial de junta, no corte de demolición → decisión, en el mismo grupo que OG044BR (corte de capa asfáltica).
    NO_CONVIENE.pop("OG081BR")
    DECISION["OG081BR"] = {
        "pregunta": ("La composição más cercana es 97114 (corte de juntas de contracción en pavimento de concreto, con cortadora de "
                     "piso: 0,004 h productivas por metro). La receta actual ya usa sólo hojas SINAPI (0,13 h de cortadora y 0,14 h de servente por metro)"),
        "grupo": "Pavimento: corte y demolición",
        "opciones": {
            "A": {"partes": [P("97114", 1, "corte de junta con cortadora de piso y disco diamantado, por metro")],
                  "regla": "97114 tal cual (corte de juntas de contracción en pavimento de concreto, por metro): única composição SINAPI de corte por metro",
                  "nota": "baja porque el SINAPI mide 0,004 h productivas de cortadora y 0,013 h de cuadrilla por metro (corte de junta) contra 0,13 h de la receta"},
            "B": None},
        "etiquetas": {"A": "97114 tal cual (queda igual que OG044BR opción A)", "B": "dejar la receta actual (cortadora y servente con precio SINAPI)"},
        "recomendada": "A"}
    return LISTO, DECISION, NO_CONVIENE


# ── Otros ──
def _tablas_otros():
    LISTO, DECISION, NO_CONVIENE = {}, {}, {}
    # frag_otros.py — fase C, grupo otros (faenas, movimiento de tierra manual, demoliciones, jardines, cercos, placas)
    # Se ejecuta con P ya definido: P(composição, cantidad, "de dónde sale", mat=1, mo=1, eq=1)

    # terra vegetal: la 105521 esparce 0,0129 m³ por m²; se lleva al volumen de la receta como en OT028BR (105521 × 3,77)
    def tierra(m3, que):
        k = round(m3 / 0.0129, 3)
        return P("105521", k, f"espalhamento de terra vegetal: {str(m3).replace('.', ',')} m³ de {que} de la receta ÷ 0,0129 m³/m² "
                              f"del SINAPI = {str(k).replace('.', ',')} (misma regla que OT028BR)")


    LISTO = {
        "OT009BR": {
            "partes": [P("103689", 1, "placa de obra por m² (chapa galvanizada adesivada sobre estructura de madera)")],
            "regla": ("103689 tal cual (única placa de obra del SINAPI, por m²): chapa galvanizada n.º 22 adesivada + sarrafos "
                      "de pinus, en lugar de la lona con arte sobre tubo 50×30 soldado de la receta (el ICD no tiene lona "
                      "impresa ni tubo rectangular); el nombre del ítem no fija el material")},
        "OT030BR": {
            "partes": [P("101159", 0.30, "alvenaria de tijolo maciço e = 10 cm por volumen: 16 ladrillos 6 × 12 × 24 con junta de 1 cm "
                                         "= 0,03 m³ por metro ÷ 0,10 m = 0,30 m²"),
                       P("94965", 0.1039, "base de hormigón hecho en obra: 0,06165 m³ de brita de la receta ÷ 0,5934 m³ de brita por m³ "
                                          "del 94965 = 0,1039 m³ preparado (0,0942 m³ colocado × 1,103)"),
                       P("103670", 0.0942, "lançamento con baldes, adensamento y acabado: 0,0942 m³ de base por metro")],
            "cambios": {"7258": ("ICD", "7260", 1, "tijolo maciço 6 × 12 × 24 cm, el de la receta del ítem, en lugar del 5 × 10 × 20")},
            "fijar": {"7260": (16, "piezas de la receta del ítem (16,44 → 16)")},
            "regla": ("101159 (alvenaria de tijolo maciço, e = 10 cm) por volumen × 0,30 m²/m con los 16 ladrillos 6×12×24 de la "
                      "receta (ICD 7260) + base de hormigón hecho en obra como en la fase B: 94965 × 0,1039 (0,0942 m³ × 1,103, "
                      "por la brita de la receta) + 103670 × 0,0942; argamassa y M.O. SINAPI por volumen, igual que el pilar OG027BR"),
            "nota": ("baja porque la receta traía 3,94 h de pedreiro y 3,95 h de servente por metro; el SINAPI pone 0,8 h de "
                     "pedreiro, 0,2 h de carpinteiro y 1,2 h de servente para 0,03 m³ de ladrillo y 0,094 m³ de base")},
        "OT031BR": {
            "partes": [P("106257", 1, "cerca con mourões roliços y arame farpado, por metro", mo=0.90876)],
            "fijar": {"340": (4.0916, "metros de arame farpado de la receta del ítem (4 hilos)"),
                      "21138": (1.3373, "metros de mourão roliço de la receta del ítem (escora de eucalipto Ø 3″)")},
            "escala": {"5076": (0.8, "grampos: 4 hilos ÷ 5 hilos")},
            "regla": ("106257 (mourões roliços a cada 2,5 m, 5 hilos) llevado a 4 hilos: arame y mourão con los metros de la "
                      "receta (4,09 m y 1,34 m), grampos × 0,8, M.O. × 0,909 (el SINAPI pone 0,0442 h de carpinteiro y 0,0221 h "
                      "de ajudante por hilo: 106461 de 4 hilos vs 106462 de 8); M.O. de hincado sin cambio")},
        "OT048BR": {
            "partes": [P("104790", 1, "demolición de concreto simple con martelete y compresor, por m³")],
            "regla": ("104790 tal cual (concreto simple sin armar, con martelete neumático y compresor, el mismo método de la "
                      "receta): el SINAPI no distingue el concreto ciclópico; sin carga ni transporte")},
    }

    DECISION = {
        # ---- replanteo por m²: el SINAPI lo mide por metro ---------------------------------------------------------
        "OT002BR": {
            "pregunta": ("El SINAPI mide la locação por metro de gabarito y el ítem es por m² de obra: ¿cuántos metros de "
                         "gabarito por m²? La receta del ítem da 0,04 m/m² (por su madera y por su M.O.); un gabarito "
                         "perimetral de una planta de 10 × 10 m da 0,40 m/m²"),
            "grupo": "Replanteo por m² ↔ metro del SINAPI",
            "opciones": {
                "A": {"partes": [P("99059", 0.04, "m de gabarito por m²: 0,09737 p² de madera de la receta = 0,00023 m³ ÷ 0,00595 m³/m "
                                                  "del SINAPI = 0,039; M.O. de la receta 0,0528 h ÷ 1,449 h/m = 0,036")],
                      "regla": ("99059 (locação com gabarito de tábuas, pontaletes a cada 2 m) × 0,04 m de gabarito por m²: "
                                "factor sacado de la receta del ítem (madera 0,039; M.O. 0,036)")},
                "B": {"partes": [P("99059", 0.40, "m de gabarito por m²: perímetro de una planta de 10 × 10 m = 40 m ÷ 100 m²")],
                      "regla": ("99059 (locação com gabarito de tábuas, pontaletes a cada 2 m) × 0,40 m de gabarito por m² "
                                "(gabarito perimetral de una planta de 10 × 10 m; depende de la forma de la planta)"),
                      "nota": ("sube porque 0,40 m de gabarito llevan 0,58 h de M.O. y 0,0024 m³ de madera; la receta traía "
                               "0,053 h y 0,00023 m³ por m² (estacas y yeso, sin gabarito corrido)")},
                "C": None},
            "etiquetas": {"A": "0,04 m de gabarito por m² (lo que da la receta del ítem)",
                          "B": "0,40 m de gabarito por m² (gabarito perimetral, planta de 100 m²)",
                          "C": "dejar la receta actual (todas sus líneas ya tienen precio SINAPI)"},
            "recomendada": "A"},
        "OT042BR": {
            "pregunta": ("El SINAPI mide la locação de pavimentação por metro de eje (topógrafo + auxiliar + receptor GNSS, "
                         "sin costo en SP porque el GNSS no está en el ICD) y el ítem es por m² de superficie: ¿qué factor? "
                         "Las horas de topógrafo de la receta dan 1,05 m/m²; una vía de 7 m de ancho da 0,143 m/m²"),
            "grupo": "Replanteo por m² ↔ metro del SINAPI",
            "opciones": {
                "A": {"partes": [P("105137", 1.048, "m de locação por m²: 0,01845 h de topógrafo de la receta ÷ 0,0176 h/m del SINAPI")],
                      "sin_ccd": {"105137": "sin costo publicado porque la locação de receptor GNSS (ICD 45153) no está en el ICD 08/2026"},
                      "cambios": {"45153": ("ICD", "7247", 1, "locação de teodolito eletrônico (h) en lugar del receptor GNSS, mismas horas")},
                      "regla": ("105137 (locação de pavimentação, por metro) armada desde sus líneas × 1,048 m/m² (horas de "
                                "topógrafo de la receta); receptor GNSS (sin precio) → teodolito eletrônico ICD 7247; piquetes "
                                "de acero del SINAPI en lugar de estacas de madera y yeso")},
                "B": {"partes": [P("105137", 0.143, "m de eje por m²: vía de 7 m de ancho, 1 ÷ 7")],
                      "sin_ccd": {"105137": "sin costo publicado porque la locação de receptor GNSS (ICD 45153) no está en el ICD 08/2026"},
                      "cambios": {"45153": ("ICD", "7247", 1, "locação de teodolito eletrônico (h) en lugar del receptor GNSS, mismas horas")},
                      "regla": ("105137 (locação de pavimentação, por metro) armada desde sus líneas × 0,143 m/m² (vía de 7 m "
                                "de ancho); receptor GNSS (sin precio) → teodolito eletrônico ICD 7247"),
                      "nota": ("baja porque el SINAPI pone 0,0176 h de topógrafo por metro de eje (0,0025 h por m² de una vía "
                               "de 7 m); la receta traía 0,018 h por m²")},
                "C": None},
            "etiquetas": {"A": "1,05 m de locação por m² (por las horas de topógrafo de la receta)",
                          "B": "0,143 m de eje por m² (vía de 7 m de ancho)",
                          "C": "dejar la receta actual (todas sus líneas ya tienen precio SINAPI)"},
            "recomendada": "A"},

        # ---- demoliciones y desmontes que el SINAPI no tiene -------------------------------------------------------
        "OT006BR": {
            "pregunta": ("El SINAPI no tiene desmonte de gaviones (sólo su ejecución, 92743 a 92758). ¿Se asimila a una "
                         "demolición manual de alvenaria o queda la receta actual (1,93 h de servente, ya con precio SINAPI)?"),
            "grupo": "Demoliciones y desmontes sin composição propia",
            "opciones": {
                "A": {"partes": [P("97622", 1, "demolición manual de alvenaria de bloco furado, por m³ (la más liviana)")],
                      "regla": ("97622 tal cual (demolición manual de alvenaria de bloco furado, sin reaprovechamiento: 2,2 h de "
                                "servente + 0,35 h de pedreiro), por analogía: el gavión no tiene mortero; sin carga ni transporte")},
                "B": {"partes": [P("97624", 1, "demolición manual de alvenaria de tijolo maciço, por m³")],
                      "regla": ("97624 tal cual (demolición manual de alvenaria de tijolo maciço, sin reaprovechamiento: 4,1 h de "
                                "servente + 0,67 h de pedreiro), por analogía; sin carga ni transporte"),
                      "nota": "sube porque la 97624 rompe mortero (4,8 h por m³); la receta traía 1,93 h de servente"},
                "C": None},
            "etiquetas": {"A": "como demolición de alvenaria de bloco furado (97622)",
                          "B": "como demolición de alvenaria de tijolo maciço (97624)",
                          "C": "dejar la receta actual (sólo servente, ya con precio SINAPI)"},
            "recomendada": "C"},
        "OT050BR": {
            "pregunta": ("El SINAPI no tiene demolición de alvenaria de pedra. ¿Se toma la demolición manual de alvenaria de "
                         "tijolo maciço (4,8 h por m³) o la de concreto simple (9,0 h por m³)? La receta trae 10,7 h de servente"),
            "grupo": "Demoliciones y desmontes sin composição propia",
            "opciones": {
                "A": {"partes": [P("97624", 1, "demolición manual de alvenaria de tijolo maciço, por m³")],
                      "regla": ("97624 tal cual (demolición manual de alvenaria de tijolo maciço, sin reaprovechamiento), la "
                                "alvenaria más pesada del SINAPI; sin carga ni transporte"),
                      "nota": "baja porque la 97624 pone 4,8 h de M.O. por m³ y la receta traía 10,7 h de servente"},
                "B": {"partes": [P("104789", 1, "demolición manual de concreto simple, por m³")],
                      "regla": ("104789 tal cual (demolición manual de concreto simple, 7,7 h de servente + 1,2 h de pedreiro): "
                                "la piedra con mortero pesa y resiste como un concreto simple; sin carga ni transporte")}},
            "etiquetas": {"A": "como alvenaria de tijolo maciço (97624)",
                          "B": "como concreto simple manual (104789, queda igual que OT049BR)"},
            "recomendada": "B"},

        # ---- demolición de piso por m²: falta el espesor -----------------------------------------------------------
        "OT047BR": {
            "pregunta": ("El ítem demuele piso y contrapiso por m² y no dice espesor ni tipo de piso; el SINAPI demuele el "
                         "piso de concreto por m³ y la cerámica y la argamassa por m². ¿Qué se toma?"),
            "grupo": "Demolición de piso por m²: espesor",
            "opciones": {
                "A": {"partes": [P("104789", 0.07, "m³ por m²: piso + contrapiso de 7 cm (2 + 5 cm)")],
                      "regla": ("104789 (demolición manual de piso de concreto simple, por m³) × 0,07 m³/m² (piso + contrapiso "
                                "de 7 cm); sin carga ni transporte")},
                "B": {"partes": [P("97633", 1, "demolición manual del revestimiento cerámico, por m²"),
                                 P("97631", 1, "demolición manual de la argamassa del contrapiso, por m²")],
                      "regla": ("97633 (demolición manual de revestimiento cerámico) + 97631 (demolición manual de argamassas), "
                                "las dos por m²: piso cerámico sobre contrapiso de argamassa, sin suponer espesor")},
                "C": {"partes": [P("104789", 0.117, "m³ por m²: 1,05 h de servente de la receta ÷ 8,97 h de M.O. por m³ del SINAPI")],
                      "regla": ("104789 (demolición manual de piso de concreto simple, por m³) × 0,117 m³/m² (espesor de 11,7 cm "
                                "deducido de las horas de la receta)")}},
            "etiquetas": {"A": "concreto de 7 cm (piso + contrapiso)",
                          "B": "cerámica + contrapiso de argamassa, por m²",
                          "C": "concreto de 11,7 cm (por las horas de la receta)"},
            "recomendada": "A"},

        # ---- escoramento: el ítem no dice el tipo ------------------------------------------------------------------
        "OT008BR": {
            "pregunta": ("El ítem no dice qué se apuntala ni el tipo. El SINAPI tiene escoramento de vala por m² de pared: "
                         "contínuo, descontínuo y pontaleteamento. La madera de la receta (0,0097 m³/m²) es la del contínuo "
                         "(0,0091). ¿Cuál se toma?"),
            "grupo": "Escoramento: tipo",
            "opciones": {
                "A": {"partes": [P("101582", 1, "escoramento de vala contínuo, 0 a 1,5 m, por m² de pared")],
                      "regla": ("101582 tal cual (escoramento de vala tipo contínuo, profundidad 0 a 1,5 m, ancho < 1,5 m): "
                                "0,0091 m³ de madera por m² contra 0,0097 de la receta"),
                      "nota": ("baja porque la receta traía 2,3 h de pedreiro y 2,3 h de servente por m²; el SINAPI pone 1,0 h "
                               "de carpinteiro y 0,33 h de servente")},
                "B": {"partes": [P("101576", 1, "escoramento de vala descontínuo, 0 a 1,5 m, por m² de pared")],
                      "regla": ("101576 tal cual (escoramento de vala tipo descontínuo, profundidad 0 a 1,5 m, ancho < 1,5 m): "
                                "0,0051 m³ de madera por m²"),
                      "nota": ("baja porque la receta traía 4,6 h de M.O. y 0,0097 m³ de madera por m²; el SINAPI pone 0,84 h "
                               "y 0,0051 m³")},
                "C": None},
            "etiquetas": {"A": "escoramento de vala contínuo (101582)",
                          "B": "escoramento de vala descontínuo (101576)",
                          "C": "dejar la receta actual (todas sus líneas ya tienen precio SINAPI)"},
            "recomendada": "A"},

        # ---- movimiento de tierra manual ---------------------------------------------------------------------------
        "OT018BR": {
            "pregunta": ("El SINAPI tiene una sola excavación manual de zanja (93358) y ya se usó para terreno blando (OT016BR) "
                         "y semiduro (OT017BR). ¿El terreno duro lleva el recargo que el SINAPI pone entre 1ª y 2ª categoría "
                         "(+14,35 %) o queda igual?"),
            "grupo": "Movimiento de tierra manual",
            "opciones": {
                "A": {"partes": [P("93358", 1, "excavación manual de zanja, por m³", mo=1.1435)],
                      "regla": ("93358 (excavación manual de zanja) con M.O. × 1,1435: la relación que el SINAPI pone entre "
                                "excavación manual en suelo de 2ª y de 1ª categoría (106206 = 2,6114 h vs 106205 = 2,2838 h); "
                                "sin carga ni transporte")},
                "B": {"partes": [P("93358", 1, "excavación manual de zanja, por m³")],
                      "regla": "93358 tal cual (excavación manual de zanja): el SINAPI no distingue la dureza; sin carga ni transporte"}},
            "etiquetas": {"A": "93358 con +14,35 % de M.O. (relación SINAPI 2ª/1ª categoría)",
                          "B": "93358 tal cual (queda igual que OT016BR y OT017BR)"},
            "recomendada": "A"},
        "OT023BR": {
            "pregunta": ("El SINAPI no tiene apisonado manual: su reaterro manual de zanjas compacta con compactador de "
                         "percusión (93382) o placa vibratoria. ¿Se pasa a la 93382 o queda la receta actual (sólo M.O., ya con "
                         "precio SINAPI)?"),
            "grupo": "Movimiento de tierra manual",
            "opciones": {
                "A": {"partes": [P("93382", 1, "reaterro manual de zanjas con compactador de percusión, por m³")],
                      "regla": ("93382 tal cual (reaterro manual de zanjas, compactación con compactador de percusión en lugar "
                                "del pisón de mano); sin aporte de suelo"),
                      "nota": ("baja porque el SINAPI compacta a máquina (0,79 h de servente y 0,2 h de compactador por m³); "
                               "la receta traía 2,6 h de M.O. a mano")},
                "B": None},
            "etiquetas": {"A": "93382, compactador de percusión (queda igual que OT004BR)",
                          "B": "dejar la receta actual (apisonado a mano, M.O. ya con precio SINAPI)"},
            "recomendada": "A"},

        # ---- césped ------------------------------------------------------------------------------------------------
        "OT029BR": {
            "pregunta": ("El ítem siembra ray-grass con turba, paja y tierra negra; el SINAPI no tiene semillas, turba ni "
                         "paja (sólo grama en placas y terra vegetal). ¿Pasa a grama batatais en placas sobre la tierra de la "
                         "receta?"),
            "grupo": "Césped: siembra o especie que el SINAPI no tiene",
            "opciones": {
                "A": {"partes": [P("98504", 1, "plantio de grama batatais em placas, por m²"), tierra(0.09749, "tierra negra")],
                      "regla": ("98504 (grama batatais em placas) en lugar de la siembra de ray-grass + 105521 (terra vegetal) "
                                "× 7,557 por los 0,0975 m³ de tierra negra de la receta; turba y paja se omiten (no existen "
                                "en el SINAPI)"),
                      "nota": ("baja porque se omiten la turba y la paja y la M.O. SINAPI es 0,66 h por m² contra 2,3 h de "
                               "la receta")},
                "B": {"partes": [P("98504", 1, "plantio de grama batatais em placas, por m²"),
                                 tierra(0.30179, "tierra negra + turba (0,09749 + 0,2043)")],
                      "regla": ("98504 (grama batatais em placas) en lugar de la siembra de ray-grass + 105521 (terra vegetal) "
                                "× 23,395 por los 0,3018 m³ de tierra negra y turba de la receta (turba → terra vegetal); "
                                "la paja se omite")},
                "C": None},
            "etiquetas": {"A": "grama batatais en placas + 0,0975 m³ de terra vegetal (sin turba)",
                          "B": "grama batatais en placas + 0,30 m³ de terra vegetal (turba como terra vegetal)",
                          "C": "dejar la receta actual (semilla, turba y paja con precio estimado)"},
            "recomendada": "A"},
        "OT045BR": {
            "pregunta": ("El SINAPI no tiene grama kikuyu (quicuio) ni turba: sus gramas en placas son batatais y "
                         "esmeralda/são carlos/curitibana. ¿Qué grama la reemplaza?"),
            "grupo": "Césped: siembra o especie que el SINAPI no tiene",
            "opciones": {
                "A": {"partes": [P("98504", 1, "plantio de grama batatais em placas, por m²"), tierra(0.07821, "turba")],
                      "regla": ("98504 (grama batatais em placas) en lugar de kikuyu + 105521 (terra vegetal) × 6,063 por los "
                                "0,0782 m³ de turba de la receta (turba → terra vegetal)")},
                "B": {"partes": [P("103946", 1, "plantio de grama esmeralda em placas, por m²"), tierra(0.07821, "turba")],
                      "regla": ("103946 (grama esmeralda, são carlos o curitibana em placas) en lugar de kikuyu + 105521 (terra "
                                "vegetal) × 6,063 por los 0,0782 m³ de turba de la receta (turba → terra vegetal)")}},
            "etiquetas": {"A": "grama batatais (rústica, la más barata)", "B": "grama esmeralda / são carlos / curitibana"},
            "recomendada": "A"},

        # ---- placa de obra de lona ---------------------------------------------------------------------------------
        "OT041BR": {
            "pregunta": ("El ítem es una placa de lona de PVC impresa (3,58 m² por pieza) y el SINAPI sólo tiene la placa de "
                         "chapa galvanizada adesivada sobre madera (R$ 504,61 por m²); el ICD no tiene lona impresa. ¿Se pasa a "
                         "la placa SINAPI o queda la receta actual?"),
            "grupo": "Placa de obra de lona",
            "opciones": {
                "A": {"partes": [P("103689", 3.5788, "m² de placa por pieza: los 3,5788 m² de lona de la receta del ítem")],
                      "regla": ("103689 (placa de obra de chapa galvanizada con estructura de madera, por m²) × 3,5788 m² por "
                                "pieza (la lona de la receta); chapa adesivada en lugar de lona de PVC"),
                      "nota": ("sube porque la chapa galvanizada adesivada del SINAPI vale R$ 432 por m² y la lona impresa de "
                               "la receta R$ 25 (estimado)")},
                "B": None},
            "etiquetas": {"A": "placa SINAPI de chapa galvanizada × 3,58 m² (deja de ser de lona)",
                          "B": "dejar la receta actual (lona y estructura con precio estimado)"},
            "recomendada": "B"},

        # ---- reja metálica -----------------------------------------------------------------------------------------
        "OT036BR": {
            "pregunta": ("La reja de tubo rectangular 20×30 no existe en el SINAPI (el alambrado con gradil 98523 no tiene "
                         "costo: tres insumos sin precio). El único gradil de acero por m² es el de barras chatas 25×4,8 mm "
                         "para vãos (99861). ¿Se toma ese, con la pintura anticorrosiva de la receta?"),
            "grupo": "Reja metálica",
            "opciones": {
                "A": {"partes": [P("99861", 1, "gradil de acero de barras chatas 25 × 4,8 mm, por m²"),
                                 P("100722", 1.205, "fundo anticorrosivo (m²): 0,1323 L de la receta ÷ 0,1098 L/m² del SINAPI")],
                      "regla": ("99861 tal cual (gradil de acero de barras chatas 25×4,8 mm hecho y fijado en obra, por m²) en "
                                "lugar de la reja de tubo 20×30 + 100722 (fundo anticorrosivo a pincel) × 1,205 m² por la "
                                "pintura de la receta")},
                "B": None},
            "etiquetas": {"A": "gradil SINAPI de barras chatas (99861) + pintura anticorrosiva",
                          "B": "dejar la receta actual (reja con precio estimado)"},
            "recomendada": "A"},

        # ---- limpieza general --------------------------------------------------------------------------------------
        "OT037BR": {
            "pregunta": ("El SINAPI 08/2026 no tiene limpieza final de obra: tiene limpiezas por tipo de superficie. ¿Cuál "
                         "representa la limpieza general (la receta trae 0,18 h de servente y 0,05 h de encarregado por m²)?"),
            "grupo": "Limpieza general",
            "opciones": {
                "A": {"partes": [P("99803", 1, "limpieza de piso con paño húmedo, por m²")],
                      "regla": ("99803 tal cual (limpieza de piso cerámico o porcelanato con paño húmedo: 0,15 h de servente, "
                                "flanela y aguarrás), la más cercana a las horas de la receta")},
                "B": {"partes": [P("99814", 1, "limpieza de superficie de piso o pared con hidrolavadora, por m²")],
                      "regla": "99814 tal cual (limpieza de superficie, piso o pared, con chorro de alta presión: 0,07 h de servente)",
                      "nota": "baja porque el SINAPI limpia con hidrolavadora (0,07 h de servente por m²); la receta traía 0,22 h de M.O."},
                "C": None},
            "etiquetas": {"A": "limpieza de piso con paño húmedo (99803)",
                          "B": "limpieza de piso o pared con hidrolavadora (99814)",
                          "C": "dejar la receta actual (sólo M.O., ya con precio SINAPI)"},
            "recomendada": "A"},
    }

    NO_CONVIENE = {
    }

    # ── Revisión del coordinador ──
    # OT009BR: la receta es lona impresa sobre tubo soldado y la placa SINAPI es chapa adesivada sobre madera: cambia el
    # material de la placa → decisión, en el mismo grupo que OT041BR.
    _ot009 = LISTO.pop("OT009BR")
    DECISION["OT009BR"] = {
        "pregunta": ("La receta es una placa de lona impresa sobre tubo 50×30 soldado; el SINAPI sólo tiene la placa de obra de "
                     "chapa galvanizada adesivada sobre madera (103689, por m²) y el ICD no tiene lona impresa ni tubo rectangular. "
                     "El nombre del ítem no fija el material"),
        "grupo": "Placa de obra de lona",
        "opciones": {"A": _ot009, "B": None},
        "etiquetas": {"A": "placa SINAPI de chapa adesivada sobre madera, por m²", "B": "dejar la receta actual (lona y tubo con precio estimado)"},
        "recomendada": "A"}
    return LISTO, DECISION, NO_CONVIENE


LISTO, DECISION, NO_CONVIENE = {}, {}, {}
for _f in (_tablas_acabados1, _tablas_acabados2, _tablas_carpinteria, _tablas_cubiertas, _tablas_mamposteria, _tablas_sanitarias1, _tablas_sanitarias2, _tablas_gruesa1, _tablas_gruesa2, _tablas_otros):
    _l, _d, _n = _f()
    _rep = (set(_l) | set(_d) | set(_n)) & (set(LISTO) | set(DECISION) | set(NO_CONVIENE))
    assert not _rep, f"ítems repetidos entre familias: {sorted(_rep)}"
    LISTO.update(_l); DECISION.update(_d); NO_CONVIENE.update(_n)
#</TABLAS>

# Temas de las decisiones (para que Oscar responda por tema): tema → grupos (el `grupo` de cada decisión).
TEMAS = {
    "1. El material o producto del ítem no existe en el SINAPI: ¿cuál lo reemplaza?": [
        "Ladrillo boliviano → bloque brasileño", "Ladrillo pegado con adhesivo (sin mortero)", "Pared de placa cimentícia",
        "Drywall con placa de 0,90 × 2,40", "Teja que el SINAPI no tiene", "Cubierta en steel frame", "Bajante de chapa galvanizada",
        "Bloquete cerámico Pavic: no existe en el SINAPI", "Piedra labrada (el SINAPI sólo tiene rachão)", "Baldosa de granilite",
        "Rodapé de granilite: en sitio o premoldeado", "Rejilla de bronce → ferro fundido", "Cerámica de fachada",
        "Carpete: qué producto", "Tanques de lavar: material que el SINAPI no tiene", "Cajas prefabricadas que el SINAPI no tiene",
        "Pia de cocina de 2 cubas", "Placa de obra de lona", "Luminarias sin precio SINAPI", "Composição exacta sin precio del insumo",
        "Césped: siembra o especie que el SINAPI no tiene", "Tubo de desagüe PVC «C-9» (clase que en Brasil no existe)", "Bombas de agua"],
    "2. El SINAPI no tiene esa medida o capacidad: ¿cuál se toma?": [
        "Tanques de agua de una capacidad que el SINAPI no tiene", "Fossa séptica de polietileno: capacidad que el SINAPI no tiene",
        "Tubo PEAD: el SINAPI sólo publica SDR 11", "Cajas de inspección: medida y material",
        "Pozos de hormigón ciclópico o ladrillo (sumideros y pozos de visita)"],
    "3. Al ítem le falta un dato (espesor, altura, medida, tipo) para convertirlo": [
        "Demolición de pared por m²: espesor", "Demolición de piso por m²: espesor", "Pavimento: corte y demolición",
        "Rodapié cerámico: altura", "Pieza tipo: puerta/ventana sin medida", "Estaca sin diámetro ni tipo",
        "Global ↔ metro de gabarito", "Replanteo por m² ↔ metro del SINAPI", "Cama de asiento de tubería: ancho de zanja",
        "Escoramento: tipo", "Pintura anticorrosiva: número de manos", "Puertas y ventanas metálicas: tipología",
        "Barandas y portones metálicos", "Reja metálica", "Limpieza general"],
    "4. El nombre y la receta se contradicen, o el método del ítem no es el del SINAPI": [
        "Baldrame «com manta asfáltica»: ¿pintura o manta?", "Forro de gesso: ¿placas o yeso aplicado?",
        "Texturizado exterior: ¿textura acrílica o revoque?", "Pavimento de rua: ¿paralelepípedo o bloco intertravado?",
        "Pavimento rígido E = 17 cm: receta incoherente con el espesor", "Rodapés de mortero (receta incoherente)",
        "Revoque exterior con mortero listo", "Juntas con alcatrão: materiales del ítem o junta SINAPI", "Piedra en pared: mano de obra",
        "Mesón de hormigón armado", "Meio-fio vaciado en obra: extrusora SINAPI o fôrma + hormigón", "Movimiento de tierra manual",
        "Demoliciones y desmontes sin composição propia"],
}
TEMA_DE = {g: t for t, gs in TEMAS.items() for g in gs}
_sin_tema = sorted({d.get("grupo", "") for d in DECISION.values()} - set(TEMA_DE))
assert not _sin_tema, f"grupos de decisión sin tema: {_sin_tema}"

# Opciones elegidas por Oscar para los NECESITA_DECISION: {"ítem": "A" | "B"}. Una opción None = receta actual.
# 28-sep-2026 — Oscar aprobó: publicar los LISTO y aplicar la opción RECOMENDADA en los temas 2, 3 y 4 (medida que el
# SINAPI no tiene, dato que le falta al ítem, nombre ≠ receta). El tema 1 (el material no existe en el SINAPI) espera su
# confirmación ítem por ítem. Quedan EN ESPERA también: OG047BR (demolición de capa asfáltica: sube 12–24×) y AC040BR /
# AC044BR (rodapés de mortero: la recomendada conserva horas de la receta boliviana).
EN_ESPERA = {"OG047BR", "AC040BR", "AC044BR",
             # Decisiones cuya opción recomendada cambia el costo (SP) a menos de la mitad o a más del doble: no se
             # publican sin que Oscar las vea (misma regla que los 25 extremos de la fase A).
             "AC008BR", "CA002BR", "CA003BR", "CR001BR", "CR018BR", "IS061BR", "IS071BR", "MP001BR", "OG019BR",
             "OG044BR", "OG052BR", "OG081BR", "OT008BR", "OT023BR", "UH022BR"}
ELEGIDAS = {c: d["recomendada"] for c, d in DECISION.items()
            if not TEMA_DE[d.get("grupo", "")].startswith("1.") and c not in EN_ESPERA}


# ═════════════════════════════ cálculo ═════════════════════════════
# Categoría de los insumos nuevos: antes que las reglas de las fases A y B. Sobre la descripción SINAPI sin tildes.
CAT_EXTRA_C = [
    (r"^(HASTE|COROA|PUNHO|LUVA) PARA PERFURATRIZ", "Ferretería"),
    (r"^(JANELA|PORTA|PORTAO|MOURAO)\b.*\bMADEIRA\b", "Madera"),
    (r"^(JANELA|PORTA|PORTAO|GRADE|GRADIL|CORRIMAO|GUARDA-CORPO|TUBO DE ACO|TUBO ACO|METALON|TELA DE ARAME|PLACA DE OBRA)\b", "Acero y Metal"),
    (r"^(FORRO DE MADEIRA|LAMBRI|PECA DE MADEIRA|TABUA|RIPA|CAIBRO|SARRAFO|PRANCHA|PONTALETE|MEIA CANA|ALIZAR|GUARNICAO|"
     r"BATENTE|RODAPE EM MADEIRA|RODAPE DE MADEIRA|PISO LAMINADO|PISO EM MADEIRA|ESCORA DE MADEIRA|VIGA DE MADEIRA|"
     r"VIGA NAO APARELHADA|VIGA APARELHADA|COMPENSADO|MADEIRA)", "Madera"),
    (r"^(TELHA|CUMEEIRA|RUFO|CALHA)", "Cubiertas"),
    (r"^(MEMBRANA IMPERMEABILIZANTE|MANTA ASFALTICA)", "Impermeabilización"),
    (r"^MASSA PLASTICA", "Adhesivos"),
    (r"^MASSA PREMIUM PARA TEXTURA", "Pinturas"),
    (r"^(VIDRO|ESPELHO|TELA DE FIBRA DE VIDRO|MOLA HIDRAULICA|FECHADURA|DOBRADICA|CADEADO|FERROLHO|PUXADOR)", "Ferretería"),
    (r"^(BANCADA|PISO|REVESTIMENTO|SOLEIRA|PEITORIL|RODAPE|PEDRA|PLACA)\b.*\b(MARMORE|GRANITO|ARDOSIA|GRANILITE|VINILICA|CIMENTICIA|GESSO)\b",
     "Ladrillos y Cerámicos"),
    (r"^(CARPETE|PISO VINILICO|PISO DE BORRACHA|PISO TATIL|PISO PODOTATIL|GRANILHA)", "Ladrillos y Cerámicos"),
    (r"^(CAIXA D'AGUA|CAIXA D AGUA|CAIXA DAGUA|RESERVATORIO|TANQUE|FOSSA|FILTRO ANAEROBIO|SUMIDOURO|CAIXA DE GORDURA|"
     r"CAIXA DE INSPECAO|CAIXA SIFONADA|CAIXA DE CONCRETO|ANEL EM CONCRETO|CHUVEIRO|DUCHA|VASO SANITARIO|BACIA SANITARIA|"
     r"BOMBA|RALO)", "Plomería"),
    (r"^(LUMINARIA|LAMPADA|REATOR|REFLETOR|RELE)", "Eléctrico"),
    (r"^(MEIO-FIO|MEIO FIO|GUIA |ESTACA|PAVER)", "Obras Civiles"),
    (r"^(EXPLOSIVO|EMULSAO EXPLOSIVA|CORDEL|ESPOLETA|RETARDO|ESTOPIM|ACESSORIO INICIADOR)", "Ferretería"),
]
fb.CAT_EXTRA[:0] = CAT_EXTRA_C

# Tildes que el SINAPI no escribe y la lista de la fase A no trae (sólo afecta a los nombres de insumos NUEVOS).
TILDES_C = """
Acessório Aérea Aplicações Ardósia Área Balão Balcão Balísticos Báscula Botões Braço Centrífuga Cilíndrica Cimentícia
Colchão Cônica Construção Corrimão Diluído Divisão Dobradiça Elastomérica Eletrônico Elevação Extensível Gás Guarnição
Incluída Iniciação Inoxidável Inspeção Lâmpadas Latão Lítio Maçaneta Maçaranduba Marítimo Mármore Máxima Média Médio
Metálicos Módulo Mourão Móveis Múltiplas Núcleo Número Penetração Pivô Plásticas Poços Polímero Portão Precisão Reforçado
Régua Reservatório Roliço Roscável Seção Semiflexível Séptica Sépticas Série Soldável Sólido Sucção Superfícies Tráfego
Transferência Treliça Vinílica Translúcida Elétricas Sintético Sintética Cerâmicas Mecânica Hidráulicas Térmica Acústica
""".split()
for _w in TILDES_C:
    fa.TILDES_SA.setdefault(fa.sin_acento(_w.lower()), _w)


def leer_adaptadas(p):
    L = io.open(p, encoding="utf-8").read().split("\n")
    i = L.index("## ADAPTADA")
    j = next(n for n in range(i + 1, len(L)) if L[n].startswith("## "))
    out = {}
    for l in L[i:j]:
        m = re.match(r"\| ([A-Z]{2}\d{3}BR) ", l)
        if not m: continue
        c = [x.strip() for x in l.strip().strip("|").split("|")]
        out[m.group(1)] = {"comp": c[2], "nota": c[3]}
    return out


def _clave(k):
    """"1287" → ("ICD", "1287"); "C:88309" → ("CCD", "88309")."""
    k = str(k)
    return ("CCD", k[2:]) if k.startswith("C:") else ("ICD", k)


class CtxC(fb.Ctx):
    def __init__(self, R, libro_path):
        super().__init__(R, libro_path)
        self.desc_an = {}  # descripción y unidad de cada hoja según el Analítico (para insumos que no están en el ICD)
        for c in self.comp.values():
            for tipo, ci, d, u, k in c["l"]:
                self.desc_an.setdefault(("ICD" if tipo == "INSUMO" else "CCD", ci), (d, u))
        self.por_ciudad = [(c["nombre"], {x["idCanonico"]: x for x in c["precios"]}) for c in self.precios_doc["ciudades"]]
        # insumo BR → su código SINAPI (para escribir la referencia con códigos SINAPI y no con ids de ArqOn)
        self.sinapi_de = {r["idCanonico"]: r["codigoSinapi"] for r in csv.DictReader(io.open(R["mapa"], encoding="utf-8"))}

    def desc(self, h, ci):
        s = self.hojas[h].get(ci)
        return s["d"] if s else self.desc_an.get((h, ci), ("(no está en el libro)", ""))[0]

    def tipo_ccd(self, ci):
        d = self.desc("CCD", ci)
        if fa.es_mo(d): return "MANO_DE_OBRA"
        if fa.es_eq(d): return "HERRAMIENTA"
        raise ValueError(f"CCD {ci} no es mano de obra ni costo horario de equipo: va como parte, no como hoja")

    def buscar(self, acc, k, que):
        h, ci = _clave(k)
        ks = [x for x in acc if x[0] == h and x[1] == ci]
        if not ks: raise ValueError(f"{que}: la hoja {h} {ci} no está en las partes")
        return ks[0]

    def armar_c(self, codigo, spec):
        """Aplana y adapta la receta `spec` del ítem. Devuelve líneas, costos, controles y referencia, o lanza ValueError."""
        desconocidas = set(spec) - {"partes", "cambios", "escala", "fijar", "quitar", "extras", "sin_ccd", "regla", "nota"}
        if desconocidas: raise ValueError(f"claves desconocidas en la receta: {sorted(desconocidas)}")
        if not spec.get("regla"): raise ValueError("la receta no trae `regla`")
        acc, orden, ctrl = {}, [], []
        sin_ccd = spec.get("sin_ccd", {})
        for pc, q, como, fm, fmo, feq in spec["partes"]:
            if pc not in self.comp: raise ValueError(f"la composição {pc} no está en el Analítico {self.mes}")
            try:
                a1, o1 = fa.aplanar(pc, self.comp, 1.0, 0, {}, [])
            except (KeyError, ValueError) as ex:
                raise ValueError(f"no se pudo aplanar {pc}: {ex}")
            v = self.psp("CCD", pc)
            if not v:
                if pc not in sin_ccd:
                    raise ValueError(f"la composição {pc} no tiene costo en SP en {self.mes} (CCD vacío) y la receta no la declara en sin_ccd")
                ctrl.append((pc, None, None, None))
            else:
                if pc in sin_ccd: raise ValueError(f"{pc} está en sin_ccd pero SÍ tiene costo CCD en SP")
                falt = [f"{h} {ci}" for (h, ci, t) in o1 if not self.psp(h, ci)]
                if falt: raise ValueError(f"{pc}: hojas sin precio SP: {', '.join(falt)}")
                s1 = sum(a1[k] * self.psp(k[0], k[1]) for k in o1)
                dif = s1 / v - 1
                if abs(dif) > TOL: raise ValueError(f"el aplanado de {pc} da {s1:.2f} en SP y el CCD publica {v:.2f} ({dif:+.1%})")
                ctrl.append((pc, s1, v, dif))
            F = {"MATERIAL": fm, "MANO_DE_OBRA": fmo, "HERRAMIENTA": feq}
            for k in o1:
                qq = a1[k] * q * F[k[2]]
                if not qq: continue
                if k not in acc: orden.append(k)
                acc[k] = acc.get(k, 0.0) + qq
        for k0 in spec.get("quitar", {}):
            k = self.buscar(acc, k0, "quitar")
            acc.pop(k); orden.remove(k)
        for k0, (hoja, nuevo, factor, _) in spec.get("cambios", {}).items():
            k = self.buscar(acc, k0, "cambios")
            q = acc.pop(k) * float(factor)
            pos = orden.index(k); orden.remove(k)
            if hoja == "COMP":
                if nuevo not in self.comp: raise ValueError(f"la composição {nuevo} no está en el Analítico")
                v = self.psp("CCD", nuevo)
                if not v: raise ValueError(f"la composição {nuevo} (cambio) no tiene costo en SP")
                a1, o1 = fa.aplanar(nuevo, self.comp, 1.0, 0, {}, [])
                s1 = sum(a1[x] * (self.psp(x[0], x[1]) or 0) for x in o1)
                if abs(s1 / v - 1) > TOL: raise ValueError(f"el aplanado de {nuevo} da {s1:.2f} y el CCD publica {v:.2f}")
                ctrl.append((nuevo, s1, v, s1 / v - 1))
                for x in o1:
                    if x not in acc: orden.append(x)
                    acc[x] = acc.get(x, 0.0) + a1[x] * q
            else:
                kn = (hoja, str(nuevo), "MATERIAL" if hoja == "ICD" else self.tipo_ccd(str(nuevo)))
                if hoja not in ("ICD", "CCD"): raise ValueError(f"cambios: hoja desconocida {hoja}")
                if str(nuevo) not in self.hojas[hoja]: raise ValueError(f"cambios: {hoja} {nuevo} no está en el libro")
                if kn not in acc: orden.insert(pos, kn)
                acc[kn] = acc.get(kn, 0.0) + q
        for k0, (factor, _) in spec.get("escala", {}).items():
            k = self.buscar(acc, k0, "escala")
            acc[k] *= float(factor)
        for k0, (cant, _) in spec.get("fijar", {}).items():
            k = self.buscar(acc, k0, "fijar")
            acc[k] = float(cant)
        extras = spec.get("extras", [])
        faltan = [f"{h} {ci} ({self.desc(h, ci)[:50]})" for (h, ci, t) in orden if not self.psp(h, ci)]
        for h, ci, q, _ in extras:
            if h == "BR":
                x = self.sp_por_id.get(ci)
                if not x or not x.get("nota", "").startswith("REFERENCIA: SINAPI") or not x.get("precio"):
                    faltan.append(f"BR {ci} (sin precio SINAPI)")
            elif h in ("ICD", "CCD"):
                if not self.psp(h, str(ci)): faltan.append(f"{h} {ci}")
            else:
                raise ValueError(f"extras: hoja desconocida {h}")
        if faltan: raise ValueError("sin precio SINAPI en SP para: " + ", ".join(faltan))
        lineas, costo_sin, costo_nuevo = [], 0.0, 0.0
        for n, key in enumerate(orden):
            h, ci, tipo = key
            q = acc[key]
            if q <= 0: raise ValueError(f"cantidad ≤ 0 en {h} {ci}")
            costo_sin += q * self.psp(h, ci)
            base, rend, precio = self.linea(h, ci, tipo, q, codigo)
            costo_nuevo += rend * precio
            lineas.append((fa.ORDEN_TIPO.get(base["tipoInsumo"], 9), n, base, rend))
        for k, (h, ci, q, _) in enumerate(extras):
            if q <= 0: raise ValueError(f"extras: cantidad ≤ 0 en {h} {ci}")
            if h == "BR":
                x = self.sp_por_id[ci]
                base = {k2: x[k2] for k2 in ("nombre", "unidad", "tipoInsumo", "categoria", "idCanonico", "codigo")}
                rend, precio = q, x["precio"]
                costo_sin += q * precio
            else:
                tipo = "MATERIAL" if h == "ICD" else self.tipo_ccd(str(ci))
                base, rend, precio = self.linea(h, str(ci), tipo, q, codigo)
                costo_sin += q * self.psp(h, str(ci))
            costo_nuevo += rend * precio
            lineas.append((fa.ORDEN_TIPO.get(base["tipoInsumo"], 9), len(orden) + k, base, rend))
        juntas, pos = [], {}
        for o, n, base, rend in sorted(lineas, key=lambda t: (t[0], t[1])):
            if base["idCanonico"] in pos: juntas[pos[base["idCanonico"]]][1] += rend; continue
            pos[base["idCanonico"]] = len(juntas); juntas.append([base, rend])
        out = [{"nombre": b["nombre"], "unidad": b["unidad"], "tipoInsumo": b["tipoInsumo"], "categoria": b["categoria"],
                "rendimiento": float(f"{r:.7g}"), "precio": 0, "tipoCalculo": "DIRECTO", "baseCalculo": "",
                "idCanonico": b["idCanonico"], "codigo": b["codigo"]} for b, r in juntas]
        if not out: raise ValueError("la receta quedó sin líneas")
        # insumos BR ya existentes: precio SINAPI > 0 en las 10 ciudades
        malos = []
        for l in out:
            if l["idCanonico"] not in self.sp_por_id: continue  # nuevo: lo pone precios-sinapi-br.py (UF o SP)
            for nom, por_id in self.por_ciudad:
                x = por_id.get(l["idCanonico"])
                if not x or not x.get("precio") or not x.get("nota", "").startswith("REFERENCIA: SINAPI"):
                    malos.append(f"{l['idCanonico']}@{nom}")
        if malos: raise ValueError("insumos BR sin precio SINAPI en alguna ciudad: " + ", ".join(malos[:4]))
        if abs(costo_nuevo / costo_sin - 1) > 0.01:
            raise ValueError(f"la receta con precios ArqOn da {costo_nuevo:.2f} y con precios SINAPI {costo_sin:.2f}: revisar factores del mapa")
        txt = " + ".join(f"{pc}{'' if q == 1 else '×' + fb.fmtq(q)}" for pc, q, *_ in spec["partes"])
        for v, (hoja, n, f, _) in spec.get("cambios", {}).items():
            txt += f" ({str(v).replace('C:', '')}→{n})"
        if extras: txt += " + insumo " + ", ".join(str(self.sinapi_de.get(ci, ci) if h == "BR" else ci) for h, ci, _, _ in extras)
        ref = f"adaptado de SINAPI {txt} · {self.mes}"
        return {"lineas": out, "costo_sin": costo_sin, "costo_nuevo": costo_nuevo, "ctrl": ctrl, "ref": ref, "txt": txt,
                "dif": max((abs(c[3]) for c in ctrl if c[3] is not None), default=0.0)}


def calcular(R, libro, tablas=None, solo=None):
    ctx = CtxC(R, libro)
    listo, decision, no_conv = tablas or (LISTO, DECISION, NO_CONVIENE)
    adapt = leer_adaptadas(R["analisis"])
    universo = list(adapt) + [c for c in SALTEADOS_A if c not in adapt]
    todos = set(listo) | set(decision) | set(no_conv)
    assert len(listo) + len(decision) + len(no_conv) == len(todos), \
        f"un ítem está en dos clases: {sorted((set(listo) & set(decision)) | (set(listo) & set(no_conv)) | (set(decision) & set(no_conv)))}"
    if solo is None:
        assert todos == set(universo), f"la tabla no cubre la fase C: faltan {sorted(set(universo) - todos)}, sobran {sorted(todos - set(universo))}"
        assert not (set(ELEGIDAS) - set(decision)), f"ELEGIDAS con ítems que no son decisión: {sorted(set(ELEGIDAS) - set(decision))}"
    else:
        assert todos <= set(universo), f"ítems que no son de la fase C: {sorted(todos - set(universo))}"
        universo = [c for c in universo if c in todos]
    filas, convertidos, fallos = [], [], []
    for cod in universo:
        it = ctx.items[cod]
        hoy = fb.costo_hoy(ctx, it)
        f = {"codigo": cod, "item": it, "hoy": hoy, "origen": "ADAPTADA" if cod in adapt else "SALTEADO_A",
             "analisis": adapt.get(cod, {})}
        if cod in listo:
            spec = listo[cod]
            f.update(clase="LISTO", spec=spec)
            try:
                r = ctx.armar_c(cod, spec)
                f.update(r)
                convertidos.append((it, r))
            except ValueError as ex:
                f.update(clase="LISTO (FALLA)", error=str(ex)); fallos.append((cod, str(ex)))
        elif cod in decision:
            d = decision[cod]
            f.update(clase="NECESITA_DECISION", opciones={}, d=d)
            assert d["recomendada"] in d["opciones"], cod
            for k, spec in d["opciones"].items():
                if spec is None:
                    f["opciones"][k] = {"actual": True, "costo_nuevo": hoy}
                    continue
                n0 = dict(ctx.nuevos)
                try:
                    r = ctx.armar_c(cod, spec)
                    f["opciones"][k] = {**r, "spec": spec}
                    if ELEGIDAS.get(cod) == k:
                        convertidos.append((it, r))
                except ValueError as ex:
                    f["opciones"][k] = {"error": str(ex)}; fallos.append((f"{cod}/{k}", str(ex)))
                if ELEGIDAS.get(cod) != k:  # los insumos nuevos de opciones no elegidas no entran
                    for idc in list(ctx.nuevos):
                        if idc not in n0: ctx.nuevos[idc].setdefault("solo_opcion", set()).add(f"{cod}/{k}")
        else:
            f.update(clase="NO_CONVIENE", motivo=no_conv[cod])
        filas.append(f)
    usados = {l["idCanonico"] for _, r in convertidos for l in r["lineas"]}
    nuevos = {k: v for k, v in ctx.nuevos.items() if k in usados}
    nuevos_opcion = {k: v for k, v in ctx.nuevos.items() if k not in usados}
    conv = [{"item": it, "lineas": r["lineas"], "ref": r["ref"],
             "cambia": it["insumos"] != r["lineas"] or it.get("referencia") != r["ref"]} for it, r in convertidos]
    return ctx, filas, conv, nuevos, nuevos_opcion, fallos


def duplicados(ctx, filas):
    """Grupos de ítems del catálogo BR que quedan con la MISMA receta (mismos insumos y rendimientos) si se aplica
    la fase C (LISTO + la opción recomendada de cada decisión). Sólo grupos con algún ítem de la fase C."""
    receta = {c: it["insumos"] for c, it in ctx.items.items()}
    de_c, como = set(), {}
    for f in filas:
        if f["clase"] == "LISTO":
            receta[f["codigo"]] = f["lineas"]; de_c.add(f["codigo"]); como[f["codigo"]] = "LISTO"
        elif f["clase"] == "NECESITA_DECISION":
            k = ELEGIDAS.get(f["codigo"], f["d"]["recomendada"])
            op = f["opciones"].get(k, {})
            if "lineas" in op:
                receta[f["codigo"]] = op["lineas"]; de_c.add(f["codigo"]); como[f["codigo"]] = f"opción {k}"
    grupos = {}
    for c, ls in receta.items():
        firma = tuple(sorted((l["idCanonico"], round(l["rendimiento"], 6)) for l in ls))
        grupos.setdefault((ctx.items[c]["unidadResultado"], firma), []).append(c)
    return [(sorted(g), como) for g in grupos.values() if len(g) > 1 and set(g) & de_c]


# ═════════════════════════════ resumen ═════════════════════════════
fmt = fa.fmt
BANDAS = [("< 0,5", lambda r: r < 0.5), ("0,5–0,8", lambda r: 0.5 <= r < 0.8), ("0,8–1,25", lambda r: 0.8 <= r <= 1.25),
          ("1,25–2", lambda r: 1.25 < r <= 2), ("> 2", lambda r: r > 2)]


def _detalle(ctx, spec):
    o = []
    for pc, q, como, fm, fmo, feq in spec["partes"]:
        esc = "".join(f", {n} ×{fb.fmtq(v)}" for n, v in (("materiales", fm), ("mano de obra", fmo), ("equipo", feq)) if v != 1)
        o.append(f"- {pc} × {fb.fmtq(q)}{esc} — {como} (_{ctx.comp[pc]['d'][:110]}_ [{ctx.comp[pc]['u']}])")
    for v, m in spec.get("sin_ccd", {}).items(): o.append(f"- {v} sin costo CCD en SP: {m}")
    for v, m in spec.get("quitar", {}).items(): o.append(f"- se quita {v} ({ctx.desc(*_clave(v))[:60]}): {m}")
    for v, (h, n, f, m) in spec.get("cambios", {}).items():
        dn = ctx.comp[n]["d"] if h == "COMP" else ctx.desc(h, str(n))
        o.append(f"- cambio {v} ({ctx.desc(*_clave(v))[:60]}) → {n} ({dn[:60]}) × {fb.fmtq(f)}: {m}")
    for v, (f, m) in spec.get("escala", {}).items(): o.append(f"- {v} ({ctx.desc(*_clave(v))[:60]}) × {fb.fmtq(f)}: {m}")
    for v, (c, m) in spec.get("fijar", {}).items(): o.append(f"- {v} ({ctx.desc(*_clave(v))[:60]}) = {fb.fmtq(c)}: {m}")
    for h, ci, q, m in spec.get("extras", []):
        d = ctx.sp_por_id[ci]["nombre"] if h == "BR" else ctx.desc(h, str(ci))
        o.append(f"- más {h} {ci} ({d[:60]}) × {fb.fmtq(q)}: {m}")
    return o


def _cel(s):
    return str(s).replace("|", "/").replace("\n", " ")


def resumen(ctx, filas, conv, nuevos, nuevos_opcion, fallos):
    mes = ctx.mes
    o = [f"# Brasil, fase C: los 153 ítems ADAPTADA y los 12 salteados de la fase A (resumen, {datetime.date.today():%d-%m-%Y})\n"]
    o.append(f"Herramienta: `tools/fase-c-composicoes-br.py` (sin `--aplicar` no toca datos; reusa las funciones de las fases A y B). "
             f"Fuente: SINAPI (Caixa/IBGE) {mes}, hojas Analítico e ICD/CCD (COM desoneração), libro nacional sha256 "
             f"`{ctx.sha[:8]}…{ctx.sha[-6:]}`. Publicado hoy: catalogo_BR `{ctx.items_doc['version']}`, precios_BR "
             f"`{ctx.precios_doc['version']}`. Al aplicar: catalogo_BR `{version_catalogo(ctx.items_doc['version'])}`; precios_BR "
             f"sube una letra (`{_letra_siguiente(ctx.precios_doc['version'])}`) sólo si entran insumos nuevos.\n")
    o.append("Cada ítem toma la composição SINAPI **más cercana** y se adapta a SU alcance con una regla escrita (columna «Regla»). "
             "Todos quedan con `referencia: \"adaptado de SINAPI … · " + mes + "\"`. Sólo cambian `insumos` y `referencia`; la identidad "
             "del ítem no se toca. Aplanado igual que en las fases A y B (M.O. «com encargos complementares» y equipo CHP/CHI = una "
             "línea con costo CCD; auxiliares abiertas; insumos nuevos `br_sinapi_<hoja>_<código>` con precio SINAPI por UF). "
             "Costos: 1 unidad en São Paulo, sin cargas ni BDI; «Hoy» = receta publicada × precios publicados; «Nuevo» = receta "
             "adaptada × precios SINAPI SP.\n")
    o.append("### Reglas de adaptación\n")
    o.append("- **Otra medida (espesor, sección, diámetro, altura)**: los materiales se escalan por la razón (espesor, área, masa por "
             "metro). La mano de obra se escala sólo donde el propio SINAPI la escala con esa medida (se dice en la regla); si no "
             "se sabe, queda la mano de obra SINAPI tal cual.\n"
             "- **Otro material de la misma familia**: se cambia el insumo por el SINAPI más cercano y las piezas por unidad se "
             "recalculan por geometría (piezas/m² = 1 ÷ [(largo + junta) × (alto + junta)]).\n"
             "- **Otra unidad**: conversión exacta (m² de cara por m, m³ por m² con el espesor, piezas por m).\n"
             "- **Cantidades propias del ítem** (kg de acero, m de cable o tubo, espesores): salen de su receta publicada; las "
             "piezas se redondean al entero.\n"
             "- **Decisiones de Oscar que ya valen**: hormigón hecho en obra = 94965 × 1,103; fôrma por la geometría del ítem; "
             "transporte con DMT 5 km.\n"
             "- Lo que cambia lo que el ítem ES (un ladrillo que en Brasil no existe, un tanque de otro tamaño, una chapa que no se "
             "vende) queda en NECESITA_DECISION.\n")
    clases = ["LISTO", "NECESITA_DECISION", "NO_CONVIENE"]
    cnt = {k: sum(1 for f in filas if f["clase"] == k) for k in clases}
    o.append("## Cuántos\n")
    o.append("| Clase | ADAPTADA | Salteados de la fase A | Total |\n|---|---:|---:|---:|")
    for k in clases:
        a = sum(1 for f in filas if f["clase"] == k and f["origen"] == "ADAPTADA")
        o.append(f"| {k} | {a} | {cnt[k] - a} | {cnt[k]} |")
    nf = sum(1 for f in filas if f["clase"] == "LISTO (FALLA)")
    if nf: o.append(f"| LISTO que fallan un control | | | {nf} |")
    o.append(f"| **Total** | **{sum(1 for f in filas if f['origen'] == 'ADAPTADA')}** | "
             f"**{sum(1 for f in filas if f['origen'] != 'ADAPTADA')}** | **{len(filas)}** |\n")
    cats = {}
    for f in filas: cats.setdefault(f["item"]["categoria"], {}).setdefault(f["clase"], 0); cats[f["item"]["categoria"]][f["clase"]] += 1
    o.append("| Categoría | LISTO | NECESITA_DECISION | NO_CONVIENE | Total |\n|---|---:|---:|---:|---:|")
    for c, v in sorted(cats.items(), key=lambda kv: -sum(kv[1].values())):
        o.append(f"| {c} | {v.get('LISTO', 0)} | {v.get('NECESITA_DECISION', 0)} | {v.get('NO_CONVIENE', 0)} | {sum(v.values())} |")
    o.append("")
    # distribución
    lis = [f for f in filas if f["clase"] == "LISTO"]
    rat = [f["costo_nuevo"] / f["hoy"] for f in lis if f["hoy"]]
    o.append("## Cambio del costo directo (LISTO, São Paulo)\n")
    if len(rat) >= 2:
        q = statistics.quantiles(rat, n=4)
        o.append(f"- Cociente nuevo / hoy: mediana **{fmt(statistics.median(rat))}**, cuartiles {fmt(q[0])}–{fmt(q[2])}, "
                 f"rango {fmt(min(rat))}–{fmt(max(rat))} ({len(rat)} ítems).")
        o.append(f"- Suma (1 unidad de cada LISTO): hoy {fmt(sum(f['hoy'] for f in lis))} → nuevo {fmt(sum(f['costo_nuevo'] for f in lis))}.")
        o.append("- Por banda: " + " · ".join(f"{b}: {sum(1 for r in rat if fn(r))}" for b, fn in BANDAS) + ".")
        porcat = {}
        for f in lis: porcat.setdefault(f["item"]["categoria"], []).append(f["costo_nuevo"] / f["hoy"])
        o.append("- Mediana por categoría: " + " · ".join(f"{c} {fmt(statistics.median(v))} ({len(v)})" for c, v in sorted(porcat.items())) + ".\n")
        ext = sorted([f for f in lis if f["hoy"] and not 0.5 <= f["costo_nuevo"] / f["hoy"] <= 2], key=lambda f: f["costo_nuevo"] / f["hoy"])
        o.append(f"### Extremos: cociente < 0,5 o > 2 ({len(ext)})\n")
        if ext:
            o.append("| Ítem | Unidad | Hoy SP | Nuevo SP | ratio | Por qué |\n|---|---|---:|---:|---:|---|")
            for f in ext:
                o.append(f"| {f['codigo']} {f['item']['nombre']} | {f['item']['unidadResultado']} | {fmt(f['hoy'])} | {fmt(f['costo_nuevo'])} | "
                         f"{fmt(f['costo_nuevo'] / f['hoy'])} | {_cel(f['spec'].get('nota', ''))} |")
        o.append("")
    # tabla por ítem
    o.append("## Por ítem\n")
    o.append("| Ítem | Unidad | Base SINAPI | Regla de adaptación | Hoy SP | Nuevo SP | ratio | clase |\n|---|---|---|---|---:|---:|---:|---|")
    for f in sorted(filas, key=lambda f: (f["item"]["categoria"], f["codigo"])):
        it = f["item"]
        nom = f"{f['codigo']} {it['nombre']}" + (" *(salteado fase A)*" if f["origen"] != "ADAPTADA" else "")
        if f["clase"] == "LISTO":
            o.append(f"| {nom} | {it['unidadResultado']} | {f['txt']} | {_cel(f['spec']['regla'])} | {fmt(f['hoy'])} | {fmt(f['costo_nuevo'])} | "
                     f"{fmt(f['costo_nuevo'] / f['hoy']) if f['hoy'] else '—'} | LISTO |")
        elif f["clase"] == "NECESITA_DECISION":
            d = f["d"]
            parts, costos = [], []
            for k, op in f["opciones"].items():
                if op.get("actual"): parts.append(f"{k}: receta actual"); costos.append(f"{k} {fmt(op['costo_nuevo'])}")
                elif "error" in op: parts.append(f"{k}: ERROR"); costos.append(f"{k} —")
                else: parts.append(f"{k}: {op['txt']}"); costos.append(f"{k} {fmt(op['costo_nuevo'])}")
            rk = d["recomendada"]; rop = f["opciones"][rk]
            ratio = fmt(rop["costo_nuevo"] / f["hoy"]) if f["hoy"] and "costo_nuevo" in rop else "—"
            o.append(f"| {nom} | {it['unidadResultado']} | {' · '.join(parts)} | {_cel(d['pregunta'])} | {fmt(f['hoy'])} | "
                     f"{' · '.join(costos)} | {ratio} ({rk}) | NECESITA_DECISION |")
        elif f["clase"] == "NO_CONVIENE":
            o.append(f"| {nom} | {it['unidadResultado']} | — | {_cel(f['motivo'])} | {fmt(f['hoy'])} | — | — | NO_CONVIENE |")
        else:
            o.append(f"| {nom} | {it['unidadResultado']} | — | {_cel(f.get('error', ''))} | {fmt(f['hoy'])} | — | — | {f['clase']} |")
    o.append("")
    # decisiones
    dec = sorted([f for f in filas if f["clase"] == "NECESITA_DECISION"],
                 key=lambda f: (TEMA_DE.get(f["d"].get("grupo"), "9"), f["d"].get("grupo", "Otros"), f["codigo"]))
    o.append(f"## NECESITA_DECISION: lo que Oscar tiene que elegir ({len(dec)})\n")
    o.append("Para aplicar una opción: agregarla a `ELEGIDAS` en la herramienta (p. ej. `\"MP001BR\": \"A\"`) y correr con `--aplicar`; "
             "para aplicar todas las recomendadas, `ELEGIDAS = {c: d[\"recomendada\"] for c, d in DECISION.items()}` (como en la fase B). "
             "«Receta actual» = no se toca. Costo SP de 1 unidad. Agrupadas por tema y grupo: una respuesta suele valer para todo el grupo.\n")
    o.append("| Tema | Decisiones | Recomendada: pasar al SINAPI | Recomendada: dejar la receta actual |\n|---|---:|---:|---:|")
    for t in TEMAS:
        fs = [f for f in dec if TEMA_DE.get(f["d"].get("grupo")) == t]
        act = sum(1 for f in fs if f["d"]["opciones"][f["d"]["recomendada"]] is None)
        o.append(f"| {t} | {len(fs)} | {len(fs) - act} | {act} |")
    o.append("")
    grupo = tema = None
    for f in dec:
        d, it = f["d"], f["item"]
        if TEMA_DE.get(d.get("grupo")) != tema:
            tema = TEMA_DE.get(d.get("grupo"))
            o.append(f"### {tema}\n")
        if d.get("grupo", "Otros") != grupo:
            grupo = d.get("grupo", "Otros")
            o.append(f"#### {grupo}\n")
        o.append(f"**{f['codigo']} {it['nombre']}** [{it['unidadResultado']}] — hoy {fmt(f['hoy'])}. {d['pregunta']} Recomendada: **{d['recomendada']}**.\n")
        for k, op in f["opciones"].items():
            et = d.get("etiquetas", {}).get(k, "")
            if op.get("actual"):
                o.append(f"- **{k}** — receta actual (sin cambios){': ' + et if et else ''}: {fmt(op['costo_nuevo'])}")
            elif "error" in op:
                o.append(f"- **{k}** — no se puede armar: {op['error']}")
            else:
                o.append(f"- **{k}**{' — ' + et if et else ''}: {op['txt']} → **{fmt(op['costo_nuevo'])}** "
                         f"({fmt(op['costo_nuevo'] / f['hoy']) if f['hoy'] else '—'}× hoy). {op['spec']['regla']}")
        o.append("")
    o.append(f"## NO_CONVIENE: queda la receta actual ({cnt['NO_CONVIENE']})\n")
    for f in sorted([f for f in filas if f["clase"] == "NO_CONVIENE"], key=lambda f: f["codigo"]):
        o.append(f"- **{f['codigo']} {f['item']['nombre']}**: {f['motivo']}.")
    o.append("")
    # duplicados
    dup = duplicados(ctx, filas)
    o.append(f"## Duplicados: ítems que quedan con la misma receta ({len(dup)} grupos)\n")
    o.append("Misma unidad, mismos insumos y mismos rendimientos (con los LISTO y la opción recomendada de cada decisión). "
             "Oscar decide si los junta o saca alguno; la herramienta no borra ítems.\n")
    for g, como in sorted(dup):
        o.append("- " + " = ".join(f"**{c}** {ctx.items[c]['nombre']}" + (f" ({como[c]})" if como.get(c, "LISTO") != "LISTO" else "")
                                   + ("" if c in como else " (ya publicado)") for c in g))
    o.append("")
    # detalle
    o.append("## Recetas LISTO: de dónde sale cada cantidad\n")
    for f in sorted(lis, key=lambda f: f["codigo"]):
        it, spec = f["item"], f["spec"]
        o.append(f"**{f['codigo']} {it['nombre']}** [{it['unidadResultado']}] — `referencia`: «{f['ref']}» · {len(it['insumos'])} → "
                 f"{len(f['lineas'])} líneas · hoy {fmt(f['hoy'])} → {fmt(f['costo_nuevo'])}\n")
        o.append(f"Regla: {spec['regla']}{' — ' + spec['nota'] if spec.get('nota') else ''}\n")
        o += _detalle(ctx, spec)
        o.append("")
    o.append("## Recetas de las opciones (NECESITA_DECISION)\n")
    for f in sorted(dec, key=lambda f: f["codigo"]):
        for k, op in f["opciones"].items():
            if "spec" not in op: continue
            o.append(f"**{f['codigo']} opción {k}** — «{op['ref']}» → {fmt(op['costo_nuevo'])}\n")
            o += _detalle(ctx, op["spec"])
            o.append("")
    # insumos nuevos
    o.append(f"## Insumos nuevos que entran al aplicar ({len(nuevos)})\n")
    o.append("Id `br_sinapi_<hoja>_<código>`, en las 10 ciudades de `oficiales_BR.json` y en `mapa_sinapi_BR.csv`; "
             "`precios-sinapi-br.py` les pone el precio SINAPI de cada UF (si la UF no tiene, el de SP con la nota). "
             "Sólo los que usan los LISTO" + (" y las opciones elegidas" if ELEGIDAS else "") + ".\n")
    por_t = {}
    for x in nuevos.values(): por_t[x["tipoInsumo"]] = por_t.get(x["tipoInsumo"], 0) + 1
    o.append(" · ".join(f"{k}: {v}" for k, v in sorted(por_t.items())) + "\n")
    o.append("| idCanonico | Nombre | Unidad | Tipo | Categoría | Precio SP | UF con precio (de 10) | Ítems |\n|---|---|---|---|---|---:|---:|---|")
    ufs10 = set(fa.CIUDAD_UF.values())
    aplicados = {c["item"]["codigo"] for c in conv}
    for idc, x in sorted(nuevos.items(), key=lambda kv: (kv[1]["tipoInsumo"], kv[1]["categoria"], kv[1]["nombre"])):
        its = sorted(set(x["items"]) & aplicados)
        n_uf = len(ufs10 & set(ctx.hojas[x["hoja"]][x["codigoSinapi"]]["p"]))
        o.append(f"| `{idc}` | {x['nombre']} | {x['unidad']} | {x['tipoInsumo']} | {x['categoria']} | {fmt(x['precioSP'])} | {n_uf} | "
                 f"{', '.join(its[:5])}{' …+' + str(len(its) - 5) if len(its) > 5 else ''} |")
    if nuevos_opcion:
        o.append(f"\nAdemás, {len(nuevos_opcion)} insumos SINAPI que sólo usan opciones de NECESITA_DECISION (entran si se elige esa opción): "
                 + ", ".join(f"`{k}` ({', '.join(sorted(v.get('solo_opcion', [])))})" for k, v in sorted(nuevos_opcion.items())) + ".")
    o.append("")
    # controles
    est = sorted({l["idCanonico"] for c in conv for l in c["lineas"] if l["idCanonico"] in ctx.sp_por_id
                  and not ctx.sp_por_id[l["idCanonico"]].get("nota", "").startswith("REFERENCIA: SINAPI")})
    peor = max((f["dif"] for f in lis), default=0)
    sinccd = sorted({pc for f in lis for pc in f["spec"].get("sin_ccd", {})})
    o.append("## Controles de la herramienta\n")
    o.append(f"- La tabla cubre exactamente los {sum(1 for f in filas if f['origen'] == 'ADAPTADA')} ADAPTADA del análisis y los "
             f"{len(SALTEADOS_A)} salteados de la fase A (ni falta ni sobra ninguno).")
    o.append(f"- LISTO armados sin error: {cnt['LISTO']}; fallas: {len(fallos)}{' (' + '; '.join(f'{a}: {b}' for a, b in fallos) + ')' if fallos else ''}.")
    o.append(f"- Toda composição usada existe en el Analítico {mes}; mayor diferencia entre el aplanado SIN adaptar y el costo CCD SP "
             f"publicado: {peor:.2%} (tolerancia 5 %).")
    o.append(f"- Composições sin costo CCD en SP armadas desde sus líneas: {len(sinccd)}{' (' + ', '.join(sinccd) + ')' if sinccd else ''}.")
    o.append(f"- Insumos ESTIMADOS en las recetas nuevas: {len(est)}{' — ' + ', '.join(est) if est else ' (ninguno)'}.")
    o.append("- Toda línea de las recetas nuevas tiene precio SINAPI > 0 en SP; los insumos BR ya existentes, además, en las 10 ciudades "
             "(los nuevos reciben el de su UF o, si falta, el de SP con la nota).")
    o.append(f"- Con `--aplicar` sólo se escriben los LISTO{' y las opciones de ELEGIDAS' if ELEGIDAS else ''} ({len(conv)} ítems; "
             f"{sum(1 for c in conv if c['cambia'])} con cambios pendientes). Antes de escribir se comprueba que ningún precio publicado "
             "cambia y que sólo cambian ítems de esta fase; si no, no se escribe nada.\n")
    return "\n".join(o) + "\n", est


# ═════════════════════════════ aplicar ═════════════════════════════
def _ver(v):
    m = re.match(r"v(\d{8})([a-z]?)(-.*)?$", v or "")
    return (m.group(1), m.group(2)) if m else ("", "")


def _letra_siguiente(v):
    m = re.match(r"v(\d{8})([a-z]?)(-.*)$", v)
    if not m: return v
    hoy = datetime.date.today().strftime("%Y%m%d")
    if hoy > m.group(1): return f"v{hoy}{m.group(3)}"
    return f"v{m.group(1)}{chr(ord(m.group(2)) + 1) if m.group(2) else 'b'}{m.group(3)}"


def version_catalogo(publicada):
    """La versión nunca baja: si la publicada ya es ≥ VERSION_CATALOGO, la letra siguiente a la publicada."""
    if _ver(publicada) < _ver(VERSION_CATALOGO): return VERSION_CATALOGO
    f, l = _ver(publicada)
    hoy = datetime.date.today().strftime("%Y%m%d")
    if hoy > f: return f"v{hoy}-br-sinapi-fase-c"
    return f"v{f}{chr(ord(l) + 1) if l else 'b'}-br-sinapi-fase-c"


def precios_estables(R, libro):
    """Lo que haría `precios-sinapi-br.py` sobre los precios YA publicados: lista de (ciudad, insumo) que cambiarían."""
    viejo = sys.stdout
    spec = importlib.util.spec_from_file_location("precios_sinapi", R["tool_precios"])
    ps = importlib.util.module_from_spec(spec); spec.loader.exec_module(ps)
    sys.stdout.flush(); _envuelto = sys.stdout  # (el módulo vuelve a envolver stdout al cargarse: se deja el de antes)
    sys.stdout = viejo
    try: _envuelto.detach()
    except Exception: pass
    libro_p, mes = ps.leer_libro(libro)
    of = json.load(io.open(R["precios"], encoding="utf-8"))
    mapa = list(csv.DictReader(io.open(R["mapa"], encoding="utf-8")))
    cambian = []
    for c in of["ciudades"]:
        uf = ps.CIUDAD_UF[c["nombre"]]
        por_id = {x["idCanonico"]: x for x in c["precios"]}
        for r in mapa:
            x = por_id.get(r["idCanonico"])
            s = libro_p[r["hoja"]].get(r["codigoSinapi"])
            if not x or not s: continue
            f = float(r["factor"])
            v, de = s["p"].get(uf), uf
            if not v: v, de = s["p"].get("SP"), "SP"
            if not v: continue
            unid = f'{s["u"]}' + (f", fator {f:g}" if f != 1 else "")
            nota = (f"REFERENCIA: SINAPI (Caixa/IBGE) ref. {mes}, {uf}, COM desoneração, código {r['codigoSinapi']} "
                    f"({unid}) - {s['d'][:90]}.")
            if de != uf: nota += f" Sem preço em {uf} no SINAPI {mes}: preço de SP."
            nuevo = round(v * f, 4 if f != 1 else 2)
            if x.get("precio") != nuevo or x.get("nota") != nota: cambian.append(f"{c['nombre']}:{r['idCanonico']}")
    return cambian


def aplicar(R, ctx, conv, nuevos, libro, permitidos):
    fuera = sorted(c["item"]["codigo"] for c in conv if c["item"]["codigo"] not in permitidos)
    if fuera: sys.exit(f"Cambiarían ítems que no son de esta fase ({', '.join(fuera)}): no aplico.")
    mal = [c["item"]["codigo"] for c in conv if c["cambia"] and c["item"].get("referencia")
           and not c["item"]["referencia"].startswith("adaptado de SINAPI")]
    if mal: sys.exit(f"Ítems que ya tienen una `referencia` de otra fase ({', '.join(mal)}): no aplico.")
    pend = [c for c in conv if c["cambia"]]
    if nuevos:  # sólo entonces corre precios-sinapi-br.py, que reescribe TODOS los precios mapeados
        cambian = precios_estables(R, libro)
        if cambian:
            sys.exit(f"precios-sinapi-br.py cambiaría {len(cambian)} precios ya publicados (p. ej. {cambian[:5]}): no aplico.")
    if not pend and not nuevos:
        print("nada que aplicar: los datos ya están al día"); return
    fa.VERSION_CATALOGO = version_catalogo(ctx.items_doc["version"])
    fa.aplicar(R, {"convertidos": conv, "nuevos": nuevos, "correcciones": []}, libro)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--libro", default=fa.LIBRO_DEF)
    ap.add_argument("--raiz", default=os.path.dirname(AQUI))
    ap.add_argument("--resumen")
    ap.add_argument("--aplicar", action="store_true")
    a = ap.parse_args()
    R = fa.rutas(os.path.abspath(a.raiz))
    ctx, filas, conv, nuevos, nuevos_opcion, fallos = calcular(R, a.libro)
    md, est = resumen(ctx, filas, conv, nuevos, nuevos_opcion, fallos)
    dest = a.resumen or os.path.join(os.path.abspath(a.raiz), "catalogo", "fuentes", "fase_c_BR_20260928.md")
    pend = [c for c in conv if c["cambia"]]
    if pend or nuevos or not os.path.exists(dest):
        if os.path.exists(dest):
            viejo = io.open(dest, encoding="utf-8").read()
            if "\n## Validación" in viejo: md += viejo[viejo.index("\n## Validación") + 1:]
        io.open(dest, "w", encoding="utf-8", newline="\n").write(md)
        print("resumen:", dest)
    else:
        print("nada pendiente: el resumen existente no se pisa")
    cl = {k: sum(1 for f in filas if f["clase"] == k) for k in ("LISTO", "NECESITA_DECISION", "NO_CONVIENE")}
    print(f"FASE C {len(filas)} · LISTO {cl['LISTO']} · NECESITA_DECISION {cl['NECESITA_DECISION']} · NO_CONVIENE {cl['NO_CONVIENE']} · "
          f"fallas {len(fallos)} · a aplicar {len(conv)} (pendientes {len(pend)}) · insumos nuevos {len(nuevos)} · estimados {len(est)}")
    for x in fallos: print("  FALLA", *x)
    if a.aplicar:
        if est: sys.exit("Hay insumos ESTIMADOS en las recetas nuevas: no aplico.")
        if any(not x[0].count("/") for x in fallos): sys.exit("Hay LISTO que fallan un control: no aplico.")
        malas = [x[0] for x in fallos if x[0].count("/") and ELEGIDAS.get(x[0].split("/")[0]) == x[0].split("/")[1]]
        if malas: sys.exit(f"Hay opciones elegidas que fallan un control ({', '.join(malas)}): no aplico.")
        aplicar(R, ctx, conv, nuevos, a.libro, {f["codigo"] for f in filas})


if __name__ == "__main__":
    main()
