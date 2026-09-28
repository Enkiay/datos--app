"""
BRASIL, FASE B: LOS 80 ÍTEMS «PARCIAL» COMO COMBINACIÓN DE COMPOSIÇÕES SINAPI (28-sep-2026).

Uso:
  python tools/fase-b-composicoes-br.py [--libro <SINAPI_Referencia_AAAA_MM.xlsx>] [--aplicar]
                                        [--raiz <copia del repo>] [--resumen <archivo.md>]

Sin --aplicar (lo normal): NO toca los datos. Calcula todo y escribe el resumen
`catalogo/fuentes/fase_b_BR_20260928.md` (una sección «## Validación» agregada a mano al final se conserva).
Con --aplicar: escribe items_BR.json, oficiales_BR.json, mapa_sinapi_BR.csv y manifest.json, SÓLO para los
ítems LISTO (y los de NECESITA_DECISION que tengan opción elegida en `ELEGIDAS`). No hace commit ni publica.
`--raiz` permite probarlo sobre una copia del repo.

QUÉ HACE
  Los ítems PARCIAL del análisis (`catalogo/fuentes/analisis_composicoes_BR_20260928.md`, tabla «## PARCIAL»)
  son el mismo servicio que el SINAPI, pero con otro alcance: el SINAPI lo parte en varias composições
  (hormigón armado = concretagem + fôrma + armação; revoque = chapisco + emboço; cubierta = telhamento +
  trama; «ponto» = aparato + cable/eletroduto por metro + caja…). Acá cada ítem se arma como SUMA de
  composições SINAPI con cantidades explícitas por unidad del ítem (tabla `LISTO` más abajo: composição,
  cantidad y de dónde sale la cantidad). La cantidad sale, siempre que se puede, de los datos del propio ítem
  (kg de acero, m de cable, m³ de piedra, espesor implícito en la arena o el cemento de su receta, sección de
  sus presets) para conservar su alcance; lo que no se puede deducir con fundamento queda en NECESITA_DECISION
  con opciones y su costo, y lo que el SINAPI no puede representar, en NO_CONVIENE (receta actual).

  Cada composição se aplana con las MISMAS reglas de la fase A (`tools/fase-a-composicoes-br.py`, se reusan sus
  funciones): M.O. «com encargos complementares» y equipo CHP/CHI = UNA línea con costo CCD; auxiliares abiertas
  recursivamente; insumos ya mapeados se reusan; los que faltan se crean como `br_sinapi_<hoja>_<código>`,
  se agregan a las 10 ciudades y al mapa y `tools/precios-sinapi-br.py` les pone el precio SINAPI por UF.
  Sólo cambian `insumos` y `referencia` («SINAPI a + b×q + c×q · MM/AAAA»; «adaptado de SINAPI …» cuando hay
  un cambio de insumo o un insumo suelto). Código, nombre, categoría, unidad, parámetros, fórmula, tipoIfc,
  etiqueta y «verificado» no se tocan.

  Además de las partes, una receta puede tener:
  · `cambios` {insumo ICD de una parte: ("ICD", otro insumo) | ("COMP", composição)}: se cambia ese insumo por
    otro insumo SINAPI o por una composição SINAPI (p. ej. el concreto usinado 38408 de la concretagem por el
    concreto hecho en obra 94965, porque la receta ArqOn usa hormigonera), con la MISMA cantidad.
  · `extras` [(hoja, código, cantidad, motivo)]: un insumo SINAPI suelto con la cantidad del ítem (cable UTP,
    soquete, lona…) cuando no hay composição que lo coloque; hoja "BR" = insumo BR existente con precio SINAPI.

CONTROLES (si falla uno, el ítem no se aplica y se informa)
  · toda composição usada está en el Analítico y tiene costo CCD en SP en el mes;
  · toda hoja (insumo ICD, M.O./equipo CCD) tiene precio SINAPI en SP;
  · el costo SP del aplanado difiere ≤ 5 % de Σ cantidad × CCD SP de las partes (+ diferencia de precio de
    los cambios + extras);
  · con --aplicar: todo insumo de las recetas nuevas tiene precio «REFERENCIA: SINAPI …» en las 10 ciudades
    (lo verifica `aplicar` de la fase A antes de escribir recetas).

VERSIONES al aplicar: catalogo_BR `v20260928d-br-sinapi-fase-b`; precios_BR sube una letra sobre la publicada
(`v20260928c-…` → `v20260928d-br-sinapi-202608`) sólo si entran insumos nuevos.
"""
import argparse, csv, datetime, hashlib, importlib.util, io, json, math, os, re, statistics, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("fase_a", os.path.join(AQUI, "fase-a-composicoes-br.py"))
fa = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fa)  # (la fase A ya deja sys.stdout en UTF-8)

VERSION_CATALOGO = "v20260928d-br-sinapi-fase-b"
TOL = 0.05


def P(comp, q, como):
    return (comp, float(q), como)


# ═════════════════════════════ RECETAS (28-sep-2026) ═════════════════════════════
# Convenciones para derivar cantidades (todas por 1 unidad del ítem):
#  · CONCRETO EN OBRA: la receta ArqOn usa 350 kg de cemento por m³ colocado (hormigonera). Se toma la
#    concretagem SINAPI del elemento y su concreto usinado se cambia por 94965 (fck 25, betoneira 400 L) con la
#    misma cantidad (1,103 m³/m³: pérdidas del SINAPI). Si la concretagem SINAPI es sólo «com bomba» y el ítem
#    es de hormigonera, se usa 103670 (lançamento com baldes) + 94965 × 1,103 (= 103669 con el cambio).
#  · ACERO: los kg del ítem, con la armação SINAPI del elemento (10 mm; losa maciza fina 6,3 mm).
#  · FÔRMA: la madera boliviana (p2, muchos reusos) no convierte a m² de fôrma SINAPI (daría 4 m²/m³ en un
#    pilar, geométricamente imposible). Se usa la GEOMETRÍA del propio ítem: presets o parámetros por defecto
#    (pilar 25×25 → perímetro/área = 16 m²/m³; cinta 25×20 sobre la pared → 2 caras = 8 m²/m³; sapata 60×60×30
#    → 4 lados = 6,67 m²/m³; muro e = 25 cm → 2 caras = 8 m²/m³; losa e → 1/e). Cuando la geometría no sale
#    del ítem, va a NECESITA_DECISION.
#  · ESPESORES de revoque/contrapiso: arena del ítem ÷ arena por m² de la composição SINAPI de referencia →
#    espesor más cercano publicado.
#  · PIEZAS (Pza/UN): la receta BR tiene una variación fija de ±3 % por línea (ajuste de rendimientos del
#    28-sep); no es alcance: se toma el entero (1 interruptor, 2 registros…). Metros y m³ se toman tal cual.
LISTO = {
    # ── Acabados ──
    "AC011BR": {"partes": [P("87879", 1, "chapisco interno"),
                           P("87535", 1, "emboço 17,5 mm: arena ArqOn 0,0514 m³/m² ≈ emboço 17,5 mm (0,0354) + lecho de asiento, que el SINAPI reemplaza por colante"),
                           P("87269", 1, "azulejo esmaltado ≤ 2025 cm² con colante AC I y rejunte (22×34 = 748 cm²)")],
                "nota": "revestimiento de pared = chapisco + emboço + cerámica con colante (práctica SINAPI)"},
    "AC012BR": {"partes": [P("87879", 1, "chapisco interno"),
                           P("87535", 1, "emboço 17,5 mm (arena ArqOn 0,0489 m³/m²)"),
                           P("87269", 1, "azulejo esmaltado ≤ 2025 cm² (20×30 = 600 cm²) con colante")],
                "nota": "igual que AC011; el SINAPI no distingue importado"},
    "AC016BR": {"partes": [P("87905", 1, "chapisco de fachada con vanos"),
                           P("87779", 1, "massa única 1:2:8 de fachada, 35 mm: arena ArqOn 0,0488 m³/m² ÷ 0,0366 (87775, 25 mm) × 25 = 33 mm → 35 mm")],
                "nota": "revoque externo = chapisco + massa única con el espesor de la receta"},
    "AC021BR": {"partes": [P("100322", 0.126, "lastro granular: 0,15 m³ de piedra ArqOn ÷ 1,19 m³ de piedra por m³ de lastro (SINAPI) = 0,126 m³/m²"),
                           P("96620", 0.0679, "contrapiso de concreto magro: 20 kg de cemento ArqOn ÷ 294,57 kg/m³ (96620) = 0,068 m³/m² (≈ 7 cm)")],
                "cambios": {"4722": ("ICD", "4730", "brita n.º 3 → pedra de mão/rachão (el ítem es lastro de piedra)")},
                "nota": "lastro de pedra de mão + contrapiso de concreto magro"},
    "AC022BR": {"partes": [P("87630", 1, "contrapiso 1:4 aderido 3 cm: arena ArqOn 0,0515 m³/m² ≈ 0,0589 del 87630 (3 cm)"),
                           P("87248", 1, "piso cerámico esmaltado 35×35 con colante AC I y rejunte")],
                "nota": "el mortero ArqOn (regularización + asiento) = contrapiso + colante en el SINAPI"},
    "AC024BR": {"partes": [P("87630", 1, "contrapiso 3 cm (arena ArqOn 0,0512 m³/m²)"),
                           P("87248", 1, "piso cerámico esmaltado 35×35 con colante")],
                "nota": "igual que AC022; el SINAPI no distingue importado"},
    "AC028BR": {"partes": [P("87630", 1, "contrapiso 3 cm (arena ArqOn 0,0486 m³/m²)"),
                           P("101726", 1, "piso de ladrilho hidráulico con colante AC III, rejunte y resina")],
                "cambios": {"3733": ("ICD", "38138", "ladrilho 20×20 Copacabana → 30×30 (el mayor del SINAPI; ArqOn 40×40 marmolado)")},
                "nota": "ladrilho hidráulico marmolado ≈ ladrilho hidráulico SINAPI 30×30"},
    "AC036BR": {"partes": [P("101751", 1, "piso de taco de madera ipê con cola"),
                           P("102499", 1, "enceramento")],
                "nota": "el selador para parquete ArqOn no tiene insumo SINAPI (se omite); el taco ipê SINAPI cuesta 292,64/m² contra 40,80 estimado"},
    "AC055BR": {"partes": [P("102214", 1, "verniz alquídico interno 2 demãos"), P("102193", 1, "lixamento de madeira")],
                "nota": "el selador para madeira (102195) no tiene costo SP ni insumo: se omite"},
    "AC067BR": {"partes": [P("95626", 1, "látex acrílica externa 2 demãos"), P("88415", 1, "fundo selador acrílico externo")],
                "nota": "corrige la receta ArqOn (0,037 L de tinta/m², 10× menos de lo normal)"},
    "UA001BR": {"partes": [P("87879", 1, "chapisco interno"),
                           P("104958", 1, "massa única 10 mm: arena ArqOn 0,0153 m³/m² ≈ 7 mm → 10 mm (el menor en argamassa de obra)")],
                "nota": "revoque = chapisco + massa única"},
    # ── Carpintería ──
    "CR004BR": {"partes": [P("100693", 1, "kit porta maciça tipo mexicana (almofadada) 80×210 con fechadura, dobradiças y batente"),
                           P("102214", 4.06, "verniz 2 demãos: 2 caras × 0,80 × 2,10 = 3,36 m² + batente (≈ 5,0 m × 0,14 m = 0,70) = 4,06 m²")],
                "nota": "puerta + barniz de las dos caras y el marco"},
    "CR007BR": {"partes": [P("90844", 1, "kit porta semi-oca 90×210 con fechadura, dobradiças y batente"),
                           P("102214", 4.51, "verniz: 2 × 0,90 × 2,10 = 3,78 m² + batente (5,1 m × 0,14 m = 0,73) = 4,51 m²")],
                "nota": "puerta moldurada interna + el acabado de la receta ArqOn (barniz)"},
    # ── Cubiertas ──
    "CU002BR": {"partes": [P("94213", 1, "telhamento con telha metálica 0,5 mm"),
                           P("92543", 1, "trama de madera (terças) por m² de cubierta: ArqOn incluye la madera de apoyo")],
                "cambios": {"7243": ("ICD", "25007", "telha trapezoidal → ondulada de aço zincado 0,5 mm (la más fina del SINAPI; ArqOn N.º 28)")},
                "nota": "telha ondulada de aço + terças"},
    "UC001BR": {"partes": [P("94213", 1, "telhamento con telha metálica 0,5 mm"), P("92543", 1, "trama de terças")],
                "cambios": {"7243": ("ICD", "25007", "trapezoidal → ondulada de aço zincado 0,5 mm")},
                "nota": "mismo servicio que CU002BR (queda con la misma receta)"},
    "CU009BR": {"partes": [P("94207", 1, "telha ondulada de fibrocimento 6 mm"), P("92543", 1, "trama de terças (ArqOn incluye la madera)")],
                "nota": "telhamento + terças"},
    "CU011BR": {"partes": [P("94201", 1, "telha cerâmica colonial capa-canal"), P("92539", 1, "trama de ripas, caibros y terças")],
                "extras": [("ICD", "3777", 1.1225, "lona plástica (subcobertura) de la receta ArqOn: 1,12 m²/m² (insumo BR `br_polietileno_m2`)")],
                "nota": "telhamento + trama + la subcobertura que el SINAPI no trae"},
    # ── Inst. Eléctricas (el SINAPI 08/2026 no tiene «ponto»: aparato + cable/eletroduto por m + caja) ──
    # Cable: calibre del mapa de precios (12 AWG → 4 mm², 14 AWG → 2,5 mm², 10 AWG → 6 mm², 8 AWG → 10 mm²).
    "IE001BR": {"partes": [P("91953", 1, "interruptor simples com placa"),
                           P("91928", 11.74, "cabo 4 mm² (12 AWG del ítem): 11,74 m de la receta"),
                           P("91940", 1, "caixa 4×2 média")],
                "nota": "sin eletroduto ni caja de techo, igual que la receta ArqOn"},
    "IE002BR": {"partes": [P("92008", 1, "tomada baixa 2 módulos 2P+T 10 A com placa"),
                           P("91928", 9.76, "cabo 4 mm² (12 AWG): 9,76 m de la receta"),
                           P("91941", 1, "caixa 4×2 baixa")],
                "nota": "sin eletroduto, igual que la receta ArqOn"},
    "IE003BR": {"partes": [P("101876", 1, "quadro PVC de embutir 6 disjuntores (sin disjuntores, igual que ArqOn)"),
                           P("91928", 5.86, "cabo 4 mm² (12 AWG): 5,86 m de la receta")],
                "nota": "quadro + cableado interno de la receta"},
    "IE009BR": {"partes": [P("91987", 1, "campainha cigarra com placa"), P("91985", 1, "pulsador de campainha"),
                           P("91940", 1, "caixa 4×2"),
                           P("91852", 24.39, "eletroduto flexível 20 mm (ArqOn PVC 5/8\"): 24,39 m de la receta"),
                           P("98280", 24.40, "cabo telefônico CCI 1 par (ArqOn UD 2×22): 24,40 m de la receta")],
                "nota": "cable de campainha = cabo de 1 par (el SINAPI no tiene UD 2×22)"},
    "IE014BR": {"partes": [P("91953", 1, "interruptor simples com placa"),
                           P("91926", 13.69, "cabo 2,5 mm² (14 AWG): 13,69 m"),
                           P("91852", 6.86, "eletroduto 20 mm (5/8\"): 6,86 m"),
                           P("91940", 1, "caixa 4×2"), P("91936", 1, "caixa octogonal de laje")],
                "extras": [("ICD", "12296", 1, "soquete de porcelana E27 de teto"),
                           ("ICD", "38194", 1, "lâmpada LED E27 10 W (la mayor del SINAPI en formato tradicional; ArqOn 14 W)")],
                "nota": "punto de luz completo + soquete y lámpara como insumos (no hay composição que los coloque)"},
    "IE015BR": {"partes": [P("98307", 1, "tomada RJ45"),
                           P("91854", 14.39, "eletroduto 25 mm (3/4\"): 14,39 m"), P("91940", 1, "caixa 4×2")],
                "extras": [("ICD", "43972", 13.62, "cabo UTP cat. 5e: 13,62 m de la receta (sin composição SINAPI 08/2026)")],
                "nota": "los conectores sueltos ArqOn quedan dentro de la tomada RJ45"},
    "IE016BR": {"partes": [P("98300", 14.69, "cabo coaxial RG6: 14,69 m"),
                           P("91852", 14.65, "eletroduto 20 mm (5/8\"): 14,65 m"), P("91940", 1, "caixa 4×2")],
                "extras": [("ICD", "38084", 1, "tomada de TV montada (placa + suporte + módulo); ArqOn con splitter")],
                "nota": "cable + eletroduto + caja + tomada de TV"},
    "IE018BR": {"partes": [P("91928", 22.63, "cabo 4 mm² (12 AWG): 22,63 m"),
                           P("91854", 10.69, "eletroduto 25 mm (3/4\"): 10,69 m"),
                           P("91939", 1, "caixa 4×2 alta (salida del split)"),
                           P("93664", 1, "disjuntor bipolar 32 A (ArqOn 2×30 A)")],
                "nota": "circuito exclusivo de aire acondicionado"},
    "IE019BR": {"partes": [P("98308", 1, "tomada RJ11"), P("98280", 13.67, "cabo CCI 1 par: 13,67 m"),
                           P("91852", 6.79, "eletroduto 20 mm (5/8\"): 6,79 m"),
                           P("91940", 1, "caixa 4×2"), P("91936", 1, "caixa octogonal")],
                "nota": "punto de teléfono completo"},
    "IE020BR": {"partes": [P("91930", 3.91, "cabo 6 mm² (10 AWG): 3,91 m"),
                           P("91854", 1.94, "eletroduto 25 mm (3/4\"): 1,94 m"),
                           P("91939", 1, "caixa 4×2 alta"), P("93665", 1, "disjuntor bipolar 40 A")],
                "nota": "circuito de ducha con las cantidades ArqOn (3,9 m de cable es poco, pero es su alcance)"},
    "IE024BR": {"partes": [P("96985", 1, "haste de aterramento 5/8\" × 3 m (norma BR; ArqOn haste de cobre de 0,80 m)"),
                           P("91932", 9.74, "cabo 10 mm² (8 AWG): 9,74 m"),
                           P("91854", 5.12, "eletroduto flexível 25 mm (ArqOn manguera PE 3/4\"): 5,12 m")],
                "nota": "haste + conductor + protección"},
    # ── Inst. Sanitarias ──
    "IS006BR": {"partes": [P("106772", 1, "pia de aço inox 0,55×1,20 com 1 cuba"), P("86908", 1, "misturador de mesa para pia")],
                "nota": "el cemento blanco ArqOn queda dentro de la instalación SINAPI"},
    "IS014BR": {"partes": [P("95657", 1, "kit cavalete PPR 3/4\" para 1 medidor"), P("95675", 1, "hidrômetro 3/4\" 5 m³/h")],
                "nota": "ramal de entrada = cavalete + hidrômetro (la conexión a la red pública no está en ninguno de los dos)"},
    "IS017BR": {"partes": [P("94495", 1, "registro de gaveta 1\""), P("92906", 1, "união galvanizada 1\"")],
                "nota": "niple y cinta, despreciables (dentro de la instalación SINAPI)"},
    "IS020BR": {"partes": [P("92341", 1, "tubo galvanizado 2\" rosqueado"),
                           P("92676", 0.82, "conexiones: 0,82 piezas/m de la receta ArqOn, como joelho 90° 2\"")],
                "nota": "tubo + conexiones por metro"},
    "IS039BR": {"partes": [P("94495", 2, "2 registros de gaveta 1\""), P("99620", 2, "2 válvulas de retenção 1\""),
                           P("92906", 2, "2 uniões galvanizadas 1\""), P("94797", 1, "torneira de boia 1\""),
                           P("89357", 4.89, "tubo PVC 32 mm: 4,89 m (ArqOn PVC roscável 1\": sin composição SINAPI)"),
                           P("89367", 5, "joelho 90° PVC 32 mm: 5 (ArqOn 4,89 roscáveis 1\")"),
                           P("89398", 3, "tê PVC 32 mm: 3 (ArqOn 3,09)"),
                           P("104059", 2, "luva PVC roscável 1\": 2")],
                "nota": "instalación del reservatório elevado; tubería PVC soldável 32 mm como la del SINAPI para reservação"},
    # ── Obra Gruesa ──
    "OG007BR": {"partes": [P("103670", 1, "lançamento com baldes, adensamento e acabamento"),
                           P("94965", 1.103, "concreto fck 25 feito em obra (betoneira, como ArqOn) con las pérdidas SINAPI"),
                           P("92411", 8, "fôrma: muro e = 25 cm, 2 caras → 2 ÷ 0,25 = 8 m²/m³"),
                           P("92919", 60, "armação 60 kg/m³ de la receta ArqOn")],
                "nota": "muro de concreto armado = concretagem + fôrma + armação"},
    "OG012BR": {"partes": [P("103675", 1, "concretagem de lajes com bomba (usinado C25; ArqOn H-21 bombeado)"),
                           P("92484", 5, "fôrma de laje: fondo del ábaco, 1 ÷ e (0,20 por defecto) = 5 m²/m³"),
                           P("92771", 58.77, "armação de laje 10 mm: 58,77 kg/m³ de la receta")],
                "extras": [("ICD", "156", 0.9761, "adhesivo epóxi estructural fluido (ArqOn Sikadur 32): 0,976 kg/m³ de la receta")],
                "nota": "ábaco = concretagem + fôrma + armação + puente de adherencia epóxi"},
    "OG015BR": {"partes": [P("103669", 1, "concretagem de pilares com baldes, usinado C25 (ArqOn H-21 ≈ C20)"),
                           P("92411", 16, "fôrma de pilar: sección 25×25 (preset central de UH007BR) → 4 × 0,25 ÷ 0,0625 = 16 m²/m³"),
                           P("92762", 125, "armação de pilar 125 kg/m³ de la receta")],
                "nota": "el aditivo acelerante ArqOn no tiene insumo SINAPI: se omite"},
    "OG016BR": {"partes": [P("103672", 1, "concretagem de pilares com bomba, usinado C25"),
                           P("92411", 16, "fôrma 25×25 → 16 m²/m³"), P("92762", 125, "armação 125 kg/m³")],
                "nota": "igual que OG015 con bomba"},
    "OG017BR": {"partes": [P("103669", 1, "concretagem de pilares com baldes, usinado C25 = H-25"),
                           P("92411", 16, "fôrma 25×25 → 16 m²/m³"), P("92762", 125, "armação 125 kg/m³")],
                "nota": "igual que OG015"},
    "OG025BR": {"partes": [P("103682", 1, "concretagem de vigas com baldes"),
                           P("92411", 8, "fôrma lateral: cinta 25×20 sobre la pared (preset central de UH008BR), 2 caras → 2 ÷ 0,25 = 8 m²/m³, sin escoramento (fôrma de pilares e estruturas similares)"),
                           P("92762", 90, "armação 90 kg/m³ de la receta")],
                "cambios": {"38408": ("COMP", "94965", "concreto usinado → feito em obra fck 25 (ArqOn usa hormigonera)")},
                "nota": "cinta de amarração = concretagem + fôrma + armação"},
    "OG039BR": {"partes": [P("92216", 1, "tubo de concreto DN 1000 fornecimento e assentamento"),
                           P("96624", 0.672, "berço de brita: 0,80 m³ ArqOn ÷ 1,19 = 0,672 m³/m"),
                           P("100323", 0.336, "berço de areia: 0,40 m³ ArqOn ÷ 1,19 = 0,336 m³/m")],
                "nota": "tubo + berço granular de la receta"},
    "OG040BR": {"partes": [P("96385", 1, "execução e compactação de aterro com rolo pé de carneiro")],
                "extras": [("ICD", "6081", 1.2127, "suelo para aterro con transporte (ArqOn tierra seleccionada 1,21 m³/m³ compactado)")],
                "nota": "el SINAPI excluye el material: se suma el suelo de la receta"},
    "OG041BR": {"partes": [P("95995", 0.05, "CBUQ capa de rolamento: e = 5 cm → 0,05 m³/m²")],
                "nota": "excluye carga, transporte y pintura de ligação, igual que la receta ArqOn (que tampoco las trae)"},
    "OG063BR": {"partes": [P("103682", 1, "concretagem de lajes com baldes"),
                           P("92484", 5, "fôrma de laje: 1 ÷ e (0,20 por defecto) = 5 m²/m³")],
                "cambios": {"38408": ("COMP", "94965", "usinado → feito em obra fck 25 (ArqOn hormigonera)")},
                "nota": "«concreto simples»: el acero va aparte (OG065BR); se quitan el arame y el armador de la receta"},
    "UH006BR": {"partes": [P("96556", 1, "concretagem de sapata, concreto feito em obra fck 30 con jerica"),
                           P("96532", 6.67, "fôrma: sapata 60×60×30 (preset central), 4 lados → 4 ÷ 0,60 = 6,67 m²/m³"),
                           P("104919", 55, "armação de sapata 55 kg/m³ de la receta")],
                "nota": "sapata = concretagem + fôrma + armação"},
    "UH007BR": {"partes": [P("103670", 1, "lançamento com baldes (pilares)"),
                           P("94965", 1.103, "concreto fck 25 feito em obra con las pérdidas SINAPI (= 103669 con 94965 en lugar del usinado)"),
                           P("92411", 16, "fôrma: presets 20×20 / 25×25 / 30×30 / 20×30 → 20 / 16 / 13,3 / 16,7 m²/m³; se toma 16"),
                           P("92762", 125, "armação 125 kg/m³ de la receta")],
                "nota": "pilar de concreto armado con hormigonera"},
    "UH008BR": {"partes": [P("103682", 1, "concretagem de vigas com baldes"),
                           P("92411", 8, "fôrma lateral: presets 20×20 / 25×20 / 35×20 → 10 / 8 / 5,7 m²/m³ (2 caras, sobre la pared); se toma 8"),
                           P("92762", 60, "armação 60 kg/m³ de la receta")],
                "cambios": {"38408": ("COMP", "94965", "usinado → feito em obra fck 25")},
                "nota": "cinta superior = concretagem + fôrma lateral + armação"},
    "UH025BR": {"partes": [P("103682", 0.0714, "concretagem: 25 kg de cemento ArqOn ÷ 350 kg/m³ = 0,0714 m³/m² (e ≈ 7 cm)"),
                           P("92484", 1, "fôrma de laje maciça: 1 m²/m²"),
                           P("92769", 10, "armação de laje 6,3 mm: 10 kg/m² de la receta")],
                "cambios": {"38408": ("COMP", "94965", "usinado → feito em obra fck 25")},
                "nota": "losa maciza por m²"},
    "UH026BR": {"partes": [P("103670", 0.0857, "lançamento: 30 kg de cemento ArqOn ÷ 350 kg/m³ = 0,0857 m³/m² (e ≈ 8,6 cm)"),
                           P("94965", 0.0945, "concreto fck 25 feito em obra: 0,0857 × 1,103"),
                           P("92411", 2, "fôrma: 2 caras por m² de pared"),
                           P("92919", 8, "armação 8 kg/m² de la receta")],
                "nota": "pared de concreto por m²"},
    # ── Otros ──
    "OT019BR": {"partes": [P("93358", 1, "escavação manual de vala"),
                           P("104482", 0.2778, "esgotamento com bomba submersível: 0,2778 h/m³ de la receta")],
                "nota": "excavación + bombeo"},
    "OT028BR": {"partes": [P("98504", 1, "plantio de grama em placas"),
                           P("105521", 3.77, "espalhamento de terra vegetal: 0,0487 m³/m² ArqOn ÷ 0,0129 del SINAPI = 3,77")],
                "nota": "turba y estiércol ArqOn sin insumo SINAPI: se omiten"},
    "OT032BR": {"partes": [P("106468", 1, "tela de alambrado 14 BWG malha 8×8 (ArqOn 7×7 n.º 12)"),
                           P("106480", 0.162, "mourão de concreto 10×10, h 2,30-2,50: 0,389 m/m² ArqOn ÷ 2,40 m = 0,162 un/m²")],
                "nota": "tela + mourões"},
}

# ── NECESITA_DECISION: Oscar elige. Cada opción es una receta (como en LISTO) o None = receta actual. ──
def _pilar_cr019(f):
    return {"partes": [P("94964", 0.0996, "concreto fck 20 feito em obra: 32,16 kg de cemento ArqOn ÷ 322,98 kg/m³"),
                       P("103670", 0.0903, "lançamento: 0,0996 ÷ 1,103"),
                       P("92411", f, "fôrma de las 2 caras del parapeto"),
                       P("92762", 29.27, "armação 29,27 kg/m de la receta")],
            "nota": "parapeto P-3 = concreto + lançamento + fôrma + armação; el aditivo ArqOn se omite"}


def _transporte(carga, transp, dmt, nota):
    return {"partes": [P(carga[0], 1, carga[1]), P(transp, dmt, f"transporte en m³×km: DMT {dmt:g} km")], "nota": nota}


DECISION = {
    "AC027BR": {"pregunta": "El SINAPI no tiene travertino: sólo piso de mármol blanco (98672, 560/m² la placa).",
                "opciones": {"A": {"partes": [P("87630", 1, "contrapiso 3 cm"), P("98672", 1, "piso de mármol interno, colante AC III + rejunte")],
                                   "nota": "mármol blanco SINAPI en lugar del travertino"},
                             "B": None}, "recomendada": "B"},
    "CR019BR": {"pregunta": "Guarda-corpo P-3 (tipología boliviana): 0,0996 m³/m de concreto; la fôrma depende del espesor, que el ítem no dice.",
                "opciones": {"A": _pilar_cr019(1.8), "B": _pilar_cr019(1.2)},
                "etiquetas": {"A": "e = 10 cm → h ≈ 0,90 m, 2 caras = 1,8 m²/m", "B": "e = 15 cm → h ≈ 0,60 m, 2 caras = 1,2 m²/m"},
                "recomendada": "A"},
    "CU003BR": {"pregunta": "Chapa N.º 33 (≈ 0,2 mm) no se usa en Brasil; la más fina del SINAPI es 0,5 mm.",
                "opciones": {"A": LISTO["CU002BR"], "B": None},
                "etiquetas": {"A": "igual que CU002BR (0,5 mm): el ítem queda duplicado"}, "recomendada": "A"},
    "CU004BR": {"pregunta": "No hay telha de policarbonato ondulada con precio en el SINAPI 08/2026; la translúcida que hay es de fibra de vidrio.",
                "opciones": {"A": {"partes": [P("94207", 1, "telhamento ondulado (fijación con tornillo y arandela)"), P("92543", 1, "trama de terças")],
                                   "cambios": {"7194": ("ICD", "7184", "fibrocimento 6 mm → telha de fibra de vidro ondulada translúcida")},
                                   "nota": "fibra de vidrio translúcida en lugar de policarbonato"},
                             "B": None}, "recomendada": "A"},
    "IE013BR": {"pregunta": "Lámpara incandescente de 100 W: obsoleta en Brasil, sin insumo SINAPI.",
                "opciones": {"A": {"partes": [P("91953", 1, "interruptor simples com placa"), P("91926", 13.59, "cabo 2,5 mm²: 13,59 m"),
                                              P("91852", 6.80, "eletroduto 20 mm: 6,80 m"), P("91940", 1, "caixa 4×2"), P("91936", 1, "caixa octogonal")],
                                   "extras": [("ICD", "12296", 1, "soquete E27 de teto"), ("ICD", "38194", 1, "lâmpada LED E27 10 W en lugar de la incandescente")],
                                   "nota": "punto de luz con LED (el nombre del ítem dice incandescente)"},
                             "B": None}, "recomendada": "A"},
    "IS001BR": {"pregunta": "Las «conexões de PVC» ArqOn son 1 global: el número de joelhos/tês por ponto no sale del ítem.",
                "opciones": {"A": {"partes": [P("89355", 5.86, "tubo PVC 20 mm: 5,86 m"), P("89358", 2, "2 joelhos 90° 20 mm"), P("89393", 1, "1 tê 20 mm")],
                                   "nota": "ponto típico: bajada con 2 codos + derivación"},
                             "B": {"partes": [P("89355", 5.86, "tubo PVC 20 mm: 5,86 m"), P("89358", 1, "1 joelho"), P("89393", 0.5, "½ tê (compartido)")],
                                   "nota": "propuesta del análisis"}},
                "recomendada": "A"},
    "IS002BR": {"pregunta": "Ponto de esgoto genérico: ¿DN 100 (vaso) o DN 50 (lavatorio, pileta, ducha)? ArqOn lo cotiza con tubo de 4\".",
                "opciones": {"A": {"partes": [P("89714", 3.91, "tubo esgoto DN 100: 3,91 m"), P("89744", 1, "joelho 90° DN 100")], "nota": "DN 100"},
                             "B": {"partes": [P("89712", 3.91, "tubo esgoto DN 50: 3,91 m"), P("89731", 1, "joelho 90° DN 50")], "nota": "DN 50"}},
                "recomendada": "A"},
    "IS021BR": {"pregunta": "El nombre dice PVC soldável 1/2\"; la receta ArqOn usa tubo PPR con conexiones galvanizadas.",
                "opciones": {"A": {"partes": [P("89355", 1, "tubo PVC soldável 20 mm"), P("89358", 0.51, "0,51 conexiones/m de la receta, como joelho 20 mm")], "nota": "según el nombre"},
                             "B": {"partes": [P("104194", 1, "tubo PPR DN 20 PN 20"), P("104199", 0.51, "0,51 joelhos PPR 20/m")], "nota": "según la receta"}},
                "recomendada": "A"},
    "IS022BR": {"pregunta": "Igual que IS021: nombre PVC soldável 3/4\", receta PPR.",
                "opciones": {"A": {"partes": [P("89356", 1, "tubo PVC soldável 25 mm"), P("89362", 0.51, "0,51 conexiones/m como joelho 90° 25 mm")], "nota": "según el nombre"},
                             "B": {"partes": [P("96635", 1, "tubo PPR DN 25 PN 20"), P("96637", 0.51, "0,51 joelhos PPR 25/m")], "nota": "según la receta"}},
                "recomendada": "A"},
    "IS036BR": {"pregunta": "ArqOn cotiza una bomba HIDRONEUMÁTICA (con tanque de presión, 3434 estimado); el SINAPI sólo tiene bomba centrífuga 1,5 CV.",
                "opciones": {"A": {"partes": [P("102116", 1, "bomba centrífuga trifásica 1,5 CV"), P("99620", 1, "válvula de retenção 1\""),
                                              P("89353", 1, "registro 3/4\""), P("92906", 1, "união 1\""), P("92905", 1, "união 3/4\""),
                                              P("102137", 1, "chave de boia")],
                                   "nota": "bomba centrífuga SINAPI + accesorios de la receta"},
                             "B": None}, "recomendada": "B"},
    "IS038BR": {"pregunta": "Misma bomba que IS036 (hidroneumática vs. centrífuga SINAPI); la caja del disyuntor no tiene composição.",
                "opciones": {"A": {"partes": [P("102116", 1, "bomba centrífuga 1,5 CV"), P("103011", 1, "válvula de pé com crivo 1\""),
                                              P("102137", 1, "chave de boia"), P("94495", 2, "2 registros 1\""), P("99620", 2, "2 retenções 1\""),
                                              P("92906", 2, "2 uniões 1\""), P("89357", 9.80, "tubo PVC 32 mm: 9,80 m (ArqOn roscável 1\")"),
                                              P("89367", 10, "10 joelhos 32 mm"), P("89398", 6, "6 tês 32 mm")],
                                   "nota": "conjunto de recalque SINAPI; sin caja de disyuntor"},
                             "B": None}, "recomendada": "B"},
    "IS087BR": {"pregunta": "La base de ducha 0,80×0,80 (y su asiento) no existe en el SINAPI.",
                "opciones": {"A": {"partes": [P("89354", 1, "misturador monocomando de chuveiro"),
                                              P("92687", 5.13, "tubo galvanizado 1/2\": 5,13 m"), P("92699", 3, "3 joelhos galvanizados 1/2\"")],
                                   "extras": [("ICD", "6294", 2, "2 tês galvanizados 1/2\" (insumo `br_tee_galvanizado_1_2_pza`; sin composição)")],
                                   "nota": "sin la base de ducha"},
                             "B": None}, "recomendada": "B"},
    "OG003BR": {"pregunta": "Fôrma del radier: sólo el borde; su m²/m³ depende del tamaño de la losa, que el ítem no fija.",
                "opciones": {"A": {"partes": [P("97096", 1, "concretagem de radier"), P("97086", 0.45, "borde de un radier típico 8×10 m, e = 0,20: 36 m × 0,20 ÷ 16 m³"),
                                              P("107281", 100, "armação 100 kg/m³")],
                                   "cambios": {"1525": ("COMP", "94965", "usinado C30 → feito em obra fck 25 (ArqOn hormigonera)")}, "nota": "geometría típica"},
                             "B": {"partes": [P("97096", 1, "concretagem de radier"), P("97086", 3, "3 m²/m³ (estimado del análisis desde la madera ArqOn)"),
                                              P("107281", 100, "armação 100 kg/m³")],
                                   "cambios": {"1525": ("COMP", "94965", "usinado → feito em obra fck 25")}, "nota": "madera ArqOn"}},
                "etiquetas": {"A": "borde de radier 8×10 m (0,45 m²/m³)", "B": "3 m²/m³ (análisis)"}, "recomendada": "A"},
    "OG004BR": {"pregunta": "Igual que OG003 (radier usinado).",
                "opciones": {"A": {"partes": [P("97096", 1, "concretagem de radier (usinado C30 bombeado)"), P("97086", 0.45, "borde de radier 8×10 m"),
                                              P("107281", 50, "armação 50 kg/m³")], "nota": "geometría típica"},
                             "B": {"partes": [P("97096", 1, "concretagem de radier"), P("97086", 1.5, "1,5 m²/m³ (análisis)"),
                                              P("107281", 50, "armação 50 kg/m³")], "nota": "madera ArqOn"}},
                "etiquetas": {"A": "borde de radier 8×10 m (0,45 m²/m³)", "B": "1,5 m²/m³ (análisis)"}, "recomendada": "A"},
    "OG006BR": {"pregunta": "Se llama «concreto ciclópico» pero la receta (0,8 m³ de piedra + 100 kg de cemento + 0,35 m³ de arena) es piedra con mortero.",
                "opciones": {"A": {"partes": [P("102487", 1, "concreto ciclópico fck 15, 30 % pedra de mão"),
                                              P("92411", 3.33, "fôrma 2 caras de un muro e = 0,60 m")], "nota": "según el nombre"},
                             "B": {"partes": [P("103800", 1, "pedra argamassada 1:3, 40 % de argamassa")], "nota": "según la receta (sin fôrma)"}},
                "recomendada": "B"},
    "OG036BR": {"pregunta": "La receta trae 0,15 m³ de pedra de mão Y 0,15 m³ de brita bajo la calzada de 4 cm: ¿una capa o dos?",
                "opciones": {"A": {"partes": [P("94990", 0.04, "calzada de concreto e = 4 cm"),
                                              P("100322", 0.126, "lastro de pedra de mão: 0,15 ÷ 1,19")],
                                   "cambios": {"4722": ("ICD", "4730", "brita 3 → pedra de mão")}, "nota": "una capa (la brita rellena el empedrado)"},
                             "B": {"partes": [P("94990", 0.04, "calzada e = 4 cm"), P("100322", 0.126, "lastro de pedra de mão"),
                                              P("100324", 0.126, "más una capa de brita: 0,15 ÷ 1,19")],
                                   "cambios": {"4722": ("ICD", "4730", "brita 3 → pedra de mão")}, "nota": "dos capas"}},
                "recomendada": "A"},
    "OG062BR": {"pregunta": "Encontros de puente: la fôrma depende del espesor del estribo, que el ítem no dice (ideal: SICRO, no SINAPI).",
                "opciones": {"A": {"partes": [P("103670", 1, "lançamento com baldes"), P("94965", 1.103, "concreto fck 25 feito em obra"),
                                              P("92411", 2, "fôrma 2 caras, e = 1,0 m")], "nota": "estribo macizo"},
                             "B": {"partes": [P("103670", 1, "lançamento"), P("94965", 1.103, "concreto fck 25"),
                                              P("92411", 4, "fôrma 2 caras, e = 0,5 m")], "nota": "estribo de 50 cm"}},
                "etiquetas": {"A": "e = 1,0 m (2 m²/m³)", "B": "e = 0,5 m (4 m²/m³)"}, "recomendada": "A"},
    "UH005BR": {"pregunta": "Baldrame ciclópico 20×30: ¿fôrma en las 2 caras (práctica SINAPI) o casi sin fôrma (vaciado contra la zanja, como sugiere la poca madera ArqOn)?",
                "opciones": {"A": {"partes": [P("102487", 1, "concreto ciclópico con lançamento"), P("96533", 10, "fôrma de baldrame 2 caras: 2 × 0,30 ÷ (0,20 × 0,30) = 10 m²/m³")],
                                   "nota": "2 caras"},
                             "B": {"partes": [P("102487", 1, "concreto ciclópico"), P("96533", 1.0, "10,78 p2 de madera ArqOn = 0,0254 m³ ÷ 0,0249 m³ de madera por m² del 96533 ≈ 1 m²/m³")],
                                   "nota": "madera ArqOn"}},
                "etiquetas": {"A": "2 caras (10 m²/m³)", "B": "≈ 1 m²/m³ (madera ArqOn)"}, "recomendada": "A"},
    "OT015BR": {"pregunta": "El transporte SINAPI es por m³×km: hay que fijar la distancia (DMT). ArqOn carga a mano; el SINAPI, con excavadora.",
                "opciones": {"A": _transporte(("100981", "carga de entulho em caminhão basculante"), "97914", 5, "carga + 5 km"),
                             "B": _transporte(("100981", "carga"), "97914", 10, "carga + 10 km")},
                "etiquetas": {"A": "DMT 5 km", "B": "DMT 10 km"}, "recomendada": "A"},
    "OT020BR": {"pregunta": "Excavación con retro + transporte por m³×km: hay que fijar la DMT.",
                "opciones": {"A": _transporte(("90105", "escavação mecanizada de vala com retroescavadeira"), "95875", 5, "excavación + 5 km"),
                             "B": _transporte(("90105", "escavação mecanizada"), "95875", 10, "excavación + 10 km")},
                "etiquetas": {"A": "DMT 5 km", "B": "DMT 10 km"}, "recomendada": "A"},
    "OT027BR": {"pregunta": "Carga + transporte de entulho por m³×km: hay que fijar la DMT.",
                "opciones": {"A": _transporte(("100981", "carga de entulho"), "97914", 5, "carga + 5 km"),
                             "B": _transporte(("100981", "carga"), "97914", 10, "carga + 10 km")},
                "etiquetas": {"A": "DMT 5 km", "B": "DMT 10 km"}, "recomendada": "A"},
    "OT038BR": {"pregunta": "Igual que OT027 (limpieza y retiro de entulho).",
                "opciones": {"A": _transporte(("100981", "carga de entulho"), "97914", 5, "carga + 5 km"),
                             "B": _transporte(("100981", "carga"), "97914", 10, "carga + 10 km")},
                "etiquetas": {"A": "DMT 5 km", "B": "DMT 10 km"}, "recomendada": "A"},
}

NO_CONVIENE = {
    "AC056BR": "el SINAPI no tiene raspado a máquina de piso de madera (sinteco); lixamento para pintura + enceramento (6,94) no es el mismo servicio",
    "CU005BR": "107142 (telhamento con telha de PVC) no tiene costo en SP en 08/2026: su telha (insumo 45753) no está en el ICD",
    "CU023BR": "107143 (policarbonato 6 mm) y 107144 (perfil U) sin costo en SP en 08/2026",
    "IE023BR": "poste de aço cônico h = 5 m (105960) sin costo en SP; la base de concreto armado enterrada no tiene composição",
    "IS068BR": "la junta por termofusión DE 160 (103443) no tiene costo en SP en 08/2026 (máquina de termofusión sin precio)",
    "IS069BR": "la junta por termofusión DE 200 (103445) no tiene costo en SP en 08/2026",
    "IS070BR": "tubo PEAD DE 250 (103381) y su junta (103447) sin costo en SP en 08/2026",
}

# Opciones elegidas por Oscar para los NECESITA_DECISION: {"ítem": "A" | "B"}. Una opción None = receta actual.
# 28-sep-2026 — Oscar: «publica los 51 y aplica las 22 recomendadas» → en cada decisión se toma la opción
# RECOMENDADA del informe (las que recomiendan dejar la receta actual quedan sin tocar).
ELEGIDAS = {cod: d["recomendada"] for cod, d in DECISION.items()}


# ═════════════════════════════ cálculo ═════════════════════════════
# Categoría de los insumos nuevos: antes que las reglas de la fase A (que por la primera palabra ponían la haste
# de aterramento en Cubiertas o la pia en Ferretería). Sobre la descripción SINAPI sin tildes.
CAT_EXTRA = [
    (r"^(HASTE DE ATERRAMENTO|CAMPAINHA|PULSADOR|CAIXA OCTOGONAL|TOMADA|INTERRUPTOR|SOQUETE|LAMPADA)", "Eléctrico"),
    (r"^(BANCADA/BANCA/PIA|HIDROMETRO|BUCHA DE REDUCAO, PPR|MISTURADOR|TORNEIRA)", "Plomería"),
    (r"^(RESINA ACRILICA|CERA LIQUIDA)", "Pinturas"),
    (r"^(PORTA DE |GUARNICAO|TACO DE MADEIRA)", "Madera"),
    (r"^(MOURAO|TUBO DE CONCRETO)", "Obras Civiles"),
    (r"^GRAMA ", "Agregados"),
]


def leer_parciales(p):
    L = io.open(p, encoding="utf-8").read().split("\n")
    i, j = L.index("## PARCIAL"), L.index("## ADAPTADA")
    return [re.match(r"\| ([A-Z]{2}\d{3}BR) ", l).group(1) for l in L[i:j] if re.match(r"\| [A-Z]{2}\d{3}BR ", l)]


class Ctx:
    """Lo mismo que prepara `calcular` de la fase A: libro, precios SP, insumos mapeados y nombres/códigos usados."""

    def __init__(self, R, libro_path):
        fuente = json.load(io.open(R["fuente"], encoding="utf-8"))
        self.sha = hashlib.sha256(open(libro_path, "rb").read()).hexdigest()
        if self.sha != fuente.get("sha256"):
            sys.exit(f"El libro {libro_path} no es el registrado en sinapi_BR.json. Paro.")
        self.hojas, self.comp, self.mes = fa.leer_libro(libro_path)
        self.items_doc, _, _ = fa.leer_json(R["items"])
        self.precios_doc, _, _ = fa.leer_json(R["precios"])
        mapa = list(csv.DictReader(io.open(R["mapa"], encoding="utf-8")))
        sp = next(c for c in self.precios_doc["ciudades"] if c["nombre"] == "São Paulo")
        self.sp_por_id = {x["idCanonico"]: x for x in sp["precios"]}
        self.items = {x["codigo"]: x for x in self.items_doc["items"]}
        uso = {}
        for it in self.items_doc["items"]:
            for l in it["insumos"]: uso[l["idCanonico"]] = uso.get(l["idCanonico"], 0) + 1
        por_cod = {}
        for r in mapa:
            if r["idCanonico"] in self.sp_por_id: por_cod.setdefault((r["hoja"], r["codigoSinapi"]), []).append(r)
        self.elegido = {}
        for k, rs in por_cod.items():
            rs.sort(key=lambda r: (float(r["factor"]) != 1.0, -uso.get(r["idCanonico"], 0), r["idCanonico"]))
            if float(rs[0]["factor"]) != 1.0 and len({r["factor"] for r in rs}) > 1: continue  # ambiguo → insumo nuevo
            self.elegido[k] = rs[0]
        cnt = {}
        for r in mapa:
            x = self.sp_por_id.get(r["idCanonico"])
            if not x or x["tipoInsumo"] != "MATERIAL": continue
            w = fa.sin_acento(r["descripcionSinapi"].upper()).split(" ")[0].strip(",")
            cnt.setdefault(w, {}).setdefault(x["categoria"], 0); cnt[w][x["categoria"]] += 1
        self.cats = {w: max(c.items(), key=lambda kv: (kv[1], kv[0]))[0] for w, c in cnt.items()}
        self.codigos = {x["codigo"] for x in sp["precios"]}
        self.nombres = {x["nombre"]: x["idCanonico"] for x in sp["precios"]}
        self.nuevos = {}

    def psp(self, h, c):
        return self.hojas[h].get(c, {}).get("p", {}).get("SP")

    def linea(self, h, ci, tipo, q, item):
        """Línea de receta (formato del catálogo) para q unidades SINAPI de la hoja (h, ci). Devuelve (línea, precio SP ArqOn)."""
        s = self.hojas[h][ci]
        m = self.elegido.get((h, ci))
        if m:
            x = self.sp_por_id[m["idCanonico"]]
            f = float(m["factor"])
            base = {k: x[k] for k in ("nombre", "unidad", "tipoInsumo", "categoria", "idCanonico", "codigo")}
            precio = x["precio"]
        else:
            idc, codigo = f"br_sinapi_{h.lower()}_{ci}", f"BR_S{'I' if h == 'ICD' else 'C'}{ci}"
            assert codigo not in self.codigos or idc in self.sp_por_id, codigo
            if h == "ICD":
                clas = fa.sin_acento(s["clas"].upper())
                if clas.startswith("EQUIPAMENTO (LOCACAO"): tipo = "HERRAMIENTA"
                elif clas.startswith("MAO DE OBRA"): tipo = "MANO_DE_OBRA"
            if tipo == "HERRAMIENTA" and h == "CCD":
                nombre = fa.nombre_equipo(s["d"], self.hojas, self.elegido, self.sp_por_id)
            else:
                nombre = fa.nombre_pt(s["d"], quitar_encargos=(tipo == "MANO_DE_OBRA"))
            if nombre in self.nombres and self.nombres[nombre] != idc:
                nombre = fa.nombre_pt(s["d"], quitar_encargos=(tipo == "MANO_DE_OBRA"), largo=10 ** 4)
            self.nombres.setdefault(nombre, idc)
            unidad, f = fa.unidad_nueva(s["u"])
            d0 = fa.sin_acento(s["d"].upper())
            cat = next((c for rx, c in CAT_EXTRA if tipo == "MATERIAL" and re.match(rx, d0)), None) \
                or fa.categoria_nueva(s["d"], tipo, s["clas"], self.cats)
            base = {"nombre": nombre, "unidad": unidad, "tipoInsumo": tipo,
                    "categoria": cat, "idCanonico": idc, "codigo": codigo}
            if idc in self.sp_por_id:
                x = self.sp_por_id[idc]
                base.update({k: x[k] for k in ("nombre", "unidad", "tipoInsumo", "categoria", "codigo")})
            precio = round(s["p"]["SP"] * f, 4 if f != 1 else 2)
            if idc not in self.sp_por_id:
                n = self.nuevos.setdefault(idc, {**base, "hoja": h, "codigoSinapi": ci, "unidadSinapi": s["u"], "factor": f,
                                                 "descripcionSinapi": s["d"], "precioSP": precio, "items": []})
                n["items"].append(item)
        return base, q / f, precio

    def armar(self, codigo, spec):
        """Aplana la receta `spec` del ítem. Devuelve dict con líneas, costos y referencia, o lanza ValueError."""
        acc, orden, ref_sp, adapt = {}, [], 0.0, False
        for pc, q, _ in spec["partes"]:
            if pc not in self.comp: raise ValueError(f"la composição {pc} no está en el Analítico {self.mes}")
            v = self.psp("CCD", pc)
            if not v: raise ValueError(f"la composição {pc} no tiene costo en SP en {self.mes} (CCD vacío)")
            ref_sp += q * v
            fa.aplanar(pc, self.comp, q, 0, acc, orden)
        for viejo, (hoja, nuevo, _) in spec.get("cambios", {}).items():
            kv = ("ICD", viejo, "MATERIAL")
            if kv not in acc: raise ValueError(f"el insumo {viejo} no está en las partes")
            q = acc.pop(kv); orden.remove(kv); adapt = True
            if hoja == "ICD":
                kn = ("ICD", nuevo, "MATERIAL")
                if kn not in acc: orden.append(kn)
                acc[kn] = acc.get(kn, 0.0) + q
                ref_sp += q * ((self.psp("ICD", nuevo) or 0) - (self.psp("ICD", viejo) or 0))
            else:
                if not self.psp("CCD", nuevo): raise ValueError(f"la composição {nuevo} no tiene costo en SP")
                fa.aplanar(nuevo, self.comp, q, 0, acc, orden)
                ref_sp += q * (self.psp("CCD", nuevo) - (self.psp("ICD", viejo) or 0))
        faltan = [f"{h} {ci}" for (h, ci, t) in orden if not self.psp(h, ci)]
        extras = spec.get("extras", [])
        for h, ci, q, _ in extras:
            adapt = True
            if h == "BR":
                x = self.sp_por_id.get(ci)
                if not x or not x.get("nota", "").startswith("REFERENCIA: SINAPI"): faltan.append(f"BR {ci} (sin precio SINAPI)")
            elif not self.psp(h, ci): faltan.append(f"{h} {ci}")
        if faltan: raise ValueError("sin precio SINAPI en SP para: " + ", ".join(faltan))
        lineas, costo_sin, costo_nuevo = [], 0.0, 0.0
        for n, key in enumerate(orden):
            h, ci, tipo = key
            q = acc[key]
            costo_sin += q * self.psp(h, ci)
            base, rend, precio = self.linea(h, ci, tipo, q, codigo)
            costo_nuevo += rend * precio
            lineas.append((fa.ORDEN_TIPO.get(base["tipoInsumo"], 9), n, base, rend))
        for k, (h, ci, q, _) in enumerate(extras):
            if h == "BR":
                x = self.sp_por_id[ci]
                base = {k2: x[k2] for k2 in ("nombre", "unidad", "tipoInsumo", "categoria", "idCanonico", "codigo")}
                rend, precio = q, x["precio"]
                costo_sin += q * precio; ref_sp += q * precio
            else:
                base, rend, precio = self.linea(h, ci, "MATERIAL", q, codigo)
                costo_sin += q * self.psp(h, ci); ref_sp += q * self.psp(h, ci)
            costo_nuevo += rend * precio
            lineas.append((fa.ORDEN_TIPO.get(base["tipoInsumo"], 9), len(orden) + k, base, rend))
        # líneas repetidas (mismo insumo BR desde dos hojas SINAPI): se suman
        juntas, pos = [], {}
        for o, n, base, rend in sorted(lineas, key=lambda t: (t[0], t[1])):
            if base["idCanonico"] in pos: juntas[pos[base["idCanonico"]]][1] += rend; continue
            pos[base["idCanonico"]] = len(juntas); juntas.append([base, rend])
        out = [{"nombre": b["nombre"], "unidad": b["unidad"], "tipoInsumo": b["tipoInsumo"], "categoria": b["categoria"],
                "rendimiento": float(f"{r:.7g}"), "precio": 0, "tipoCalculo": "DIRECTO", "baseCalculo": "",
                "idCanonico": b["idCanonico"], "codigo": b["codigo"]} for b, r in juntas]
        dif = costo_sin / ref_sp - 1
        if abs(dif) > TOL: raise ValueError(f"el aplanado da {costo_sin:.2f} en SP y las partes suman {ref_sp:.2f} ({dif:+.1%})")
        txt = " + ".join(f"{pc}{'' if q == 1 else '×' + fmtq(q)}" for pc, q, _ in spec["partes"])
        if spec.get("cambios"): txt += "".join(f" ({v}→{n})" for v, (_, n, _) in spec["cambios"].items())
        if extras: txt += " + insumo " + ", ".join(ci if h != "BR" else ci for h, ci, _, _ in extras)
        ref = f"{'adaptado de ' if adapt else ''}SINAPI {txt} · {self.mes}"
        return {"lineas": out, "costo_sin": costo_sin, "costo_nuevo": costo_nuevo, "ref_sp": ref_sp, "dif": dif, "ref": ref, "txt": txt}


def fmtq(q):
    return (f"{q:.4f}".rstrip("0").rstrip(".")).replace(".", ",")


def costo_hoy(ctx, it):
    return sum(l["rendimiento"] * ctx.sp_por_id.get(l["idCanonico"], {}).get("precio", 0) for l in it["insumos"])


def calcular(R, libro):
    ctx = Ctx(R, libro)
    parciales = leer_parciales(R["analisis"])
    todos = set(LISTO) | set(DECISION) | set(NO_CONVIENE)
    assert len(LISTO) + len(DECISION) + len(NO_CONVIENE) == len(todos), "un ítem está en dos clases"
    assert todos == set(parciales), f"la tabla no cubre los PARCIAL: faltan {set(parciales) - todos}, sobran {todos - set(parciales)}"
    filas, convertidos, fallos = [], [], []
    for cod in parciales:
        it = ctx.items[cod]
        hoy = costo_hoy(ctx, it)
        f = {"codigo": cod, "item": it, "hoy": hoy}
        if cod in LISTO:
            spec = LISTO[cod]
            f.update(clase="LISTO", spec=spec)
            try:
                r = ctx.armar(cod, spec)
                f.update(r)
                convertidos.append((it, r))
            except ValueError as ex:
                f.update(clase="LISTO (FALLA)", error=str(ex)); fallos.append((cod, str(ex)))
        elif cod in DECISION:
            d = DECISION[cod]
            f.update(clase="NECESITA_DECISION", opciones={})
            for k, spec in d["opciones"].items():
                if spec is None:
                    f["opciones"][k] = {"actual": True, "costo_nuevo": hoy}
                    continue
                n0 = dict(ctx.nuevos)
                try:
                    r = ctx.armar(cod, spec)
                    f["opciones"][k] = {**r, "spec": spec}
                    if ELEGIDAS.get(cod) == k:
                        convertidos.append((it, r))
                except ValueError as ex:
                    f["opciones"][k] = {"error": str(ex)}; fallos.append((f"{cod}/{k}", str(ex)))
                if ELEGIDAS.get(cod) != k:  # los insumos nuevos de opciones no elegidas no entran
                    for idc in list(ctx.nuevos):
                        if idc not in n0: ctx.nuevos[idc].setdefault("solo_opcion", set()).add(f"{cod}/{k}")
        else:
            f.update(clase="NO_CONVIENE", motivo=NO_CONVIENE[cod])
        filas.append(f)
    usados = {l["idCanonico"] for _, r in convertidos for l in r["lineas"]}
    nuevos = {k: v for k, v in ctx.nuevos.items() if k in usados}
    nuevos_opcion = {k: v for k, v in ctx.nuevos.items() if k not in usados}
    conv = [{"item": it, "lineas": r["lineas"], "ref": r["ref"],
             "cambia": it["insumos"] != r["lineas"] or it.get("referencia") != r["ref"]} for it, r in convertidos]
    return ctx, filas, conv, nuevos, nuevos_opcion, fallos


# ═════════════════════════════ resumen ═════════════════════════════
fmt = fa.fmt


def resumen(ctx, filas, conv, nuevos, nuevos_opcion, fallos):
    mes = ctx.mes
    o = [f"# Brasil, fase B: los 80 ítems PARCIAL como combinación de composições SINAPI (resumen, {datetime.date.today():%d-%m-%Y})\n"]
    o.append(f"Herramienta: `tools/fase-b-composicoes-br.py` (sin `--aplicar` no toca datos; reusa las funciones de "
             f"`tools/fase-a-composicoes-br.py`). Fuente: SINAPI (Caixa/IBGE) {mes}, hojas Analítico e ICD/CCD (COM desoneração), "
             f"libro nacional sha256 `{ctx.sha[:8]}…{ctx.sha[-6:]}`. Versiones al aplicar: catalogo_BR `{VERSION_CATALOGO}`; "
             f"precios_BR sube una letra sobre la publicada (`{ctx.precios_doc['version']}` → `v20260928d-br-sinapi-202608`).\n")
    o.append("Cada ítem PARCIAL es el mismo servicio que el SINAPI con otro alcance. Acá se arma como **suma de composições "
             "SINAPI con cantidad explícita por unidad del ítem**; cada composição se aplana con las reglas de la fase A (M.O. "
             "y equipo = una línea con costo CCD; auxiliares abiertas; insumos nuevos `br_sinapi_<hoja>_<código>` con precio "
             "SINAPI por UF). Sólo cambian `insumos` y `referencia`; la identidad del ítem no se toca. Costos: 1 unidad en "
             "São Paulo, sin cargas ni BDI; «Hoy» = receta publicada × precios publicados; «SINAPI» = receta nueva × precios "
             "SINAPI SP que quedan al aplicar.\n")
    o.append("### Cómo salen las cantidades\n")
    o.append("- **Concreto en obra**: la receta ArqOn usa 350 kg de cemento/m³ con hormigonera → concretagem SINAPI del elemento "
             "con su concreto usinado cambiado por **94965** (fck 25, betoneira) en la misma cantidad (1,103 m³/m³ = pérdidas SINAPI). "
             "Los ítems «usinado» conservan el usinado SINAPI.\n"
             "- **Acero**: los kg por m³ (o m²) de la receta, con la armação SINAPI del elemento.\n"
             "- **Fôrma**: la madera boliviana (p2, muchos reusos) no se puede convertir a m² de fôrma SINAPI (en un pilar daría "
             "≈ 4 m²/m³, geométricamente imposible). Se usa la **geometría del propio ítem** (presets o parámetros por defecto): "
             "pilar 25×25 → 16 m²/m³; cinta 25×20 sobre la pared → 8; sapata 60×60×30 → 6,67; muro e = 25 cm → 8; losa e = 20 cm → 5. "
             "Cuando la geometría no sale del ítem (radier, baldrame, encontros, P-3), el ítem queda en NECESITA_DECISION.\n"
             "- **Espesores** (revoques, contrapisos, lastros): arena/cemento/piedra del ítem ÷ consumo por m² de la composição → "
             "espesor publicado más cercano.\n"
             "- **Pontos eléctricos e hidráulicos**: el SINAPI 08/2026 no tiene «ponto»; se suman aparato + cable/eletroduto/tubo "
             "por metro + cajas/conexiones, con los metros de la receta ArqOn. El calibre del cable sigue el mapa de precios "
             "(12 AWG → 4 mm²).\n"
             "- **Piezas**: la receta BR tiene una variación fija de ±3 % por línea (ajuste del 28-sep); en piezas se toma el entero.\n")
    # conteos
    clases = ["LISTO", "NECESITA_DECISION", "NO_CONVIENE"]
    cnt = {k: sum(1 for f in filas if f["clase"] == k) for k in clases}
    o.append("## Cuántos\n")
    o.append("| Clase | Ítems |\n|---|---:|")
    for k in clases: o.append(f"| {k} | {cnt[k]} |")
    if fallos: o.append(f"| LISTO que fallan un control | {sum(1 for f in filas if f['clase'] == 'LISTO (FALLA)')} |")
    o.append(f"| **Total PARCIAL** | **{len(filas)}** |\n")
    cats = {}
    for f in filas: cats.setdefault(f["item"]["categoria"], {}).setdefault(f["clase"], 0); cats[f["item"]["categoria"]][f["clase"]] += 1
    o.append("| Categoría | LISTO | NECESITA_DECISION | NO_CONVIENE | Total |\n|---|---:|---:|---:|---:|")
    for c, v in sorted(cats.items(), key=lambda kv: -sum(kv[1].values())):
        o.append(f"| {c} | {v.get('LISTO', 0)} | {v.get('NECESITA_DECISION', 0)} | {v.get('NO_CONVIENE', 0)} | {sum(v.values())} |")
    o.append("")
    # distribución LISTO
    lis = [f for f in filas if f["clase"] == "LISTO"]
    rat = [f["costo_nuevo"] / f["hoy"] for f in lis if f["hoy"]]
    o.append("## Cambio del costo directo (LISTO, São Paulo)\n")
    if rat:
        q = statistics.quantiles(rat, n=4)
        o.append(f"- Cociente SINAPI / hoy: mediana **{fmt(statistics.median(rat))}**, cuartiles {fmt(q[0])}–{fmt(q[2])}, "
                 f"rango {fmt(min(rat))}–{fmt(max(rat))} ({len(rat)} ítems).")
        o.append(f"- Suma (1 unidad de cada LISTO): hoy {fmt(sum(f['hoy'] for f in lis))} → SINAPI {fmt(sum(f['costo_nuevo'] for f in lis))}.")
        bandas = [("< 0,5", lambda r: r < 0.5), ("0,5–0,8", lambda r: 0.5 <= r < 0.8), ("0,8–1,25", lambda r: 0.8 <= r <= 1.25),
                  ("1,25–2", lambda r: 1.25 < r <= 2), ("> 2", lambda r: r > 2)]
        o.append("- Por banda: " + " · ".join(f"{b}: {sum(1 for r in rat if fn(r))}" for b, fn in bandas) + ".")
        porcat = {}
        for f in lis: porcat.setdefault(f["item"]["categoria"], []).append(f["costo_nuevo"] / f["hoy"])
        o.append("- Mediana por categoría: " + " · ".join(f"{c} {fmt(statistics.median(v))} ({len(v)})" for c, v in sorted(porcat.items())) + ".\n")
        o.append("Las bajas vienen casi todas de la mano de obra (productividad SINAPI medida por la Caixa contra la boliviana); "
                 "las subidas, de la fôrma por geometría en pilares/cintas y de materiales que ArqOn tenía estimados bajos (taco de ipê).\n")
    # tabla por ítem
    o.append("## Por ítem\n")
    o.append("| Ítem | Unidad | Composições × cantidad | Hoy SP | SINAPI SP | ratio | clase | nota |\n|---|---|---|---:|---:|---:|---|---|")
    for f in sorted(filas, key=lambda f: (f["item"]["categoria"], f["codigo"])):
        it = f["item"]
        if f["clase"] == "LISTO":
            o.append(f"| {f['codigo']} {it['nombre']} | {it['unidadResultado']} | {f['txt']} | {fmt(f['hoy'])} | {fmt(f['costo_nuevo'])} | "
                     f"{fmt(f['costo_nuevo'] / f['hoy']) if f['hoy'] else '—'} | LISTO | {f['spec'].get('nota', '')} |")
        elif f["clase"] == "NECESITA_DECISION":
            d = DECISION[f["codigo"]]
            parts, costos = [], []
            for k, op in f["opciones"].items():
                if op.get("actual"): parts.append(f"{k}: receta actual"); costos.append(f"{k} {fmt(op['costo_nuevo'])}")
                elif "error" in op: parts.append(f"{k}: ERROR"); costos.append(f"{k} —")
                else: parts.append(f"{k}: {op['txt']}"); costos.append(f"{k} {fmt(op['costo_nuevo'])}")
            rk = d["recomendada"]; rop = f["opciones"][rk]
            ratio = fmt(rop["costo_nuevo"] / f["hoy"]) if f["hoy"] and "costo_nuevo" in rop else "—"
            o.append(f"| {f['codigo']} {it['nombre']} | {it['unidadResultado']} | {' · '.join(parts)} | {fmt(f['hoy'])} | "
                     f"{' · '.join(costos)} | {ratio} ({rk}) | NECESITA_DECISION | {d['pregunta']} |")
        elif f["clase"] == "NO_CONVIENE":
            o.append(f"| {f['codigo']} {it['nombre']} | {it['unidadResultado']} | — | {fmt(f['hoy'])} | — | — | NO_CONVIENE | {f['motivo']} |")
        else:
            o.append(f"| {f['codigo']} {it['nombre']} | {it['unidadResultado']} | — | {fmt(f['hoy'])} | — | — | {f['clase']} | {f.get('error', '')} |")
    o.append("")
    # detalle de cantidades LISTO
    o.append("## Recetas LISTO: de dónde sale cada cantidad\n")
    for f in sorted([f for f in filas if f["clase"] == "LISTO"], key=lambda f: f["codigo"]):
        it, spec = f["item"], f["spec"]
        o.append(f"**{f['codigo']} {it['nombre']}** [{it['unidadResultado']}] — `referencia`: «{f['ref']}» · aplanado vs partes {f['dif']:+.2%} · "
                 f"{len(it['insumos'])} → {len(f['lineas'])} líneas\n")
        for pc, q, como in spec["partes"]:
            o.append(f"- {pc} × {fmtq(q)} — {como} (_{ctx.comp[pc]['d'][:110]}_)")
        for v, (h, n, mot) in spec.get("cambios", {}).items():
            o.append(f"- cambio {v} → {n}: {mot}")
        for h, ci, q, mot in spec.get("extras", []):
            o.append(f"- insumo {ci} × {fmtq(q)} — {mot}")
        o.append("")
    # decisiones
    o.append("## NECESITA_DECISION: lo que Oscar tiene que elegir\n")
    o.append("Para aplicar una opción: agregarla a `ELEGIDAS` en la herramienta (p. ej. `\"OG003BR\": \"A\"`) y correr con `--aplicar` "
             "(si la fase B ya se publicó, subir antes `VERSION_CATALOGO` a la letra siguiente: la app sólo baja un catálogo con "
             "versión nueva). «Receta actual» = no se toca. Costo SP de 1 unidad.\n")
    for f in sorted([f for f in filas if f["clase"] == "NECESITA_DECISION"], key=lambda f: f["codigo"]):
        d, it = DECISION[f["codigo"]], f["item"]
        o.append(f"### {f['codigo']} {it['nombre']} [{it['unidadResultado']}] — hoy {fmt(f['hoy'])}\n")
        o.append(f"{d['pregunta']} Recomendada: **{d['recomendada']}**.\n")
        for k, op in f["opciones"].items():
            et = d.get("etiquetas", {}).get(k, "")
            if op.get("actual"):
                o.append(f"- **{k}** — receta actual (sin cambios): {fmt(op['costo_nuevo'])}")
            elif "error" in op:
                o.append(f"- **{k}** — no se puede armar: {op['error']}")
            else:
                o.append(f"- **{k}**{' — ' + et if et else ''}: {op['txt']} → **{fmt(op['costo_nuevo'])}** "
                         f"({fmt(op['costo_nuevo'] / f['hoy']) if f['hoy'] else '—'}× hoy). {op['spec'].get('nota', '')}")
        o.append("")
    o.append("## NO_CONVIENE (receta actual)\n")
    for f in sorted([f for f in filas if f["clase"] == "NO_CONVIENE"], key=lambda f: f["codigo"]):
        o.append(f"- **{f['codigo']} {f['item']['nombre']}**: {f['motivo']}.")
    o.append("")
    # insumos nuevos
    o.append(f"## Insumos nuevos que entran al aplicar ({len(nuevos)})\n")
    o.append("Id `br_sinapi_<hoja>_<código>`, en las 10 ciudades de `oficiales_BR.json` y en `mapa_sinapi_BR.csv`; "
             "`precios-sinapi-br.py` les pone el precio SINAPI de cada UF (si la UF no tiene, el de SP). Sólo los que usan los LISTO.\n")
    por_t = {}
    for x in nuevos.values(): por_t[x["tipoInsumo"]] = por_t.get(x["tipoInsumo"], 0) + 1
    o.append(" · ".join(f"{k}: {v}" for k, v in sorted(por_t.items())) + "\n")
    o.append("| idCanonico | Nombre | Unidad | Tipo | Categoría | Precio SP | Ítems |\n|---|---|---|---|---|---:|---|")
    for idc, x in sorted(nuevos.items(), key=lambda kv: (kv[1]["tipoInsumo"], kv[1]["categoria"], kv[1]["nombre"])):
        its = sorted(set(x["items"]) & {c["item"]["codigo"] for c in conv})
        o.append(f"| `{idc}` | {x['nombre']} | {x['unidad']} | {x['tipoInsumo']} | {x['categoria']} | {fmt(x['precioSP'])} | {', '.join(its)} |")
    if nuevos_opcion:
        o.append(f"\nAdemás, {len(nuevos_opcion)} insumos SINAPI que sólo usan opciones de NECESITA_DECISION (entran si se elige esa opción): "
                 + ", ".join(f"`{k}` ({', '.join(sorted(v.get('solo_opcion', [])))})" for k, v in sorted(nuevos_opcion.items())) + ".")
    o.append("")
    # controles
    est = sorted({l["idCanonico"] for c in conv for l in c["lineas"] if l["idCanonico"] in ctx.sp_por_id
                  and not ctx.sp_por_id[l["idCanonico"]].get("nota", "").startswith("REFERENCIA: SINAPI")})
    peor = max((abs(f["dif"]) for f in filas if f["clase"] == "LISTO"), default=0)
    o.append("## Controles de la herramienta\n")
    o.append(f"- La tabla cubre exactamente los {len(filas)} PARCIAL del análisis (ni falta ni sobra ninguno).")
    o.append(f"- LISTO armados sin error: {cnt['LISTO']}; fallas: {len(fallos)}{' (' + '; '.join(f'{a}: {b}' for a, b in fallos) + ')' if fallos else ''}.")
    o.append(f"- Mayor diferencia aplanado vs Σ partes CCD: {peor:.2%} (tolerancia 5 %).")
    o.append(f"- Insumos ESTIMADOS en las recetas nuevas: {len(est)}{' — ' + ', '.join(est) if est else ' (ninguno)'}.")
    o.append(f"- Con `--aplicar` sólo se escriben los LISTO{' y las opciones de ELEGIDAS' if ELEGIDAS else ''} ({len(conv)} ítems; "
             f"{sum(1 for c in conv if c['cambia'])} con cambios pendientes); antes de escribir recetas se exige precio «REFERENCIA: SINAPI …» "
             "en las 10 ciudades para todo insumo usado.\n")
    return "\n".join(o) + "\n", est


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
    dest = a.resumen or os.path.join(os.path.abspath(a.raiz), "catalogo", "fuentes", "fase_b_BR_20260928.md")
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
    print(f"PARCIAL {len(filas)} · LISTO {cl['LISTO']} · NECESITA_DECISION {cl['NECESITA_DECISION']} · NO_CONVIENE {cl['NO_CONVIENE']} · "
          f"fallas {len(fallos)} · a aplicar {len(conv)} (pendientes {len(pend)}) · insumos nuevos {len(nuevos)} · estimados {len(est)}")
    for x in fallos: print("  FALLA", *x)
    if a.aplicar:
        if est: sys.exit("Hay insumos ESTIMADOS en las recetas nuevas: no aplico.")
        if fallos and any(not x[0].count("/") for x in fallos): sys.exit("Hay LISTO que fallan un control: no aplico.")
        fa.VERSION_CATALOGO = VERSION_CATALOGO
        fa.aplicar(R, {"convertidos": conv, "nuevos": nuevos, "correcciones": []}, a.libro)


if __name__ == "__main__":
    main()
