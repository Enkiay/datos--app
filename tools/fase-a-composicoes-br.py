"""
BRASIL, FASE A: LAS RECETAS «EQUIVALENTE» PASAN A SER LA COMPOSICIÓN SINAPI (28-sep-2026).

Uso:
  python tools/fase-a-composicoes-br.py [--libro <SINAPI_Referencia_AAAA_MM.xlsx>] [--aplicar]
                                        [--raiz <copia del repo>] [--resumen <archivo.md>]

Sin --aplicar (lo normal): NO toca los datos. Calcula todo y escribe el resumen
`catalogo/fuentes/fase_a_BR_20260928.md` (si no hay nada que cambiar y el resumen ya existe, no lo pisa).
Con --aplicar: además escribe items_BR.json, oficiales_BR.json, mapa_sinapi_BR.csv y manifest.json.
No hace commit ni publica. `--raiz` permite probarlo sobre una copia del repo.

QUÉ HACE
  Toma los ítems clasificados EQUIVALENTE en `catalogo/fuentes/analisis_composicoes_BR_20260928.md`
  (tabla «## EQUIVALENTE»: ítem ↔ composición SINAPI) y, para cada uno, cambia SÓLO su lista `insumos`
  por las líneas de la composición (coeficiente SINAPI → rendimiento) y le agrega
  `referencia: "SINAPI NNNNN · MM/AAAA"`. La identidad del ítem no se toca (codigo, nombre, categoria,
  unidadResultado, parametros, formulaResultado, tipoCalculo, tipoIfc, inputPrincipalLabel, verificado…).
  Los loaders del PC (catalogo-oficial.ts copia campos por nombre) y de la APK (kotlinx con
  ignoreUnknownKeys = true) ignoran `referencia` sin romperse.

REGLA DE APLANADO (líneas COMPOSICAO dentro de la composición)
  · «… COM ENCARGOS COMPLEMENTARES» (pedreiro 88309, servente 88316…) → UNA línea MANO_DE_OBRA,
    con el costo CCD de esa composición por UF. No se abre en salario/EPI/transporte.
  · Costo horario de equipo (descripción con «CHP» o «CHI») → UNA línea HERRAMIENTA (Maquinaria), costo CCD.
  · Cualquier otra composición auxiliar (argamassa, concreto preparado en obra, armação, concretagem…)
    se abre en sus ítems con coeficiente × coeficiente, recursivamente hasta llegar a INSUMOS o a una
    de las dos anteriores, y los repetidos se suman.
  · Cada hoja (INSUMO → hoja ICD, MO/equipo → hoja CCD) se busca en `precios/fuentes/mapa_sinapi_BR.csv`
    (codigoSinapi + hoja). Si ya hay un insumo BR mapeado se reusa (idCanonico, codigo, nombre, unidad,
    categoría) y el rendimiento es coef ÷ factor del mapa. Si no, se crea `br_sinapi_<hoja>_<codigo>`
    con nombre portugués del SINAPI, se agrega a las 10 ciudades de oficiales_BR.json y al mapa, y
    `tools/precios-sinapi-br.py` le pone el precio (UF de la ciudad; si no hay, el de SP).
    Unidades nuevas: M→m, M2→m2, M3→m3, KG→Kg, H/CHP/CHI→Hr, UN/CJ/JG→Pza, L→L; CENTO→Pza con factor 0,01
    (precio por pieza, rendimiento ×100); alquileres «M×MES»/«UN×MES» quedan como m×mes / Pza×mes.
    Insumos del ICD «EQUIPAMENTO (LOCAÇÃO)» van como HERRAMIENTA (Herramientas).

SE SALTEA (y se informa)
  · la composición no está en el Analítico o no tiene costo CCD en SP en el mes;
  · alguna hoja no tiene precio en SP (el precio no podría salir del SINAPI);
  · la unidad no coincide (m2/M2, m3/M3, m/M, Kg/KG, Pza/UN, Glb/UN) o la tabla pide un factor de unidad;
  · el costo SP de la receta aplanada difiere > 5 % del costo CCD publicado (el aplanado no reproduce la
    composición; entre 1 y 5 % se informa como aviso).
"""
import argparse, csv, datetime, hashlib, io, json, os, re, statistics, subprocess, sys, unicodedata
import openpyxl

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
AQUI = os.path.dirname(os.path.abspath(__file__))
VERSION_CATALOGO = "v20260928b-br-sinapi-fase-a"
LIBRO_DEF = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp", "sinapi", "SINAPI_Referencia_2026_08.xlsx")
CIUDAD_UF = {
    "São Paulo": "SP", "Rio de Janeiro": "RJ", "Belo Horizonte": "MG", "Brasília": "DF", "Curitiba": "PR",
    "Porto Alegre": "RS", "Salvador": "BA", "Recife": "PE", "Fortaleza": "CE", "Manaus": "AM",
}
UNID = {"M": "m", "M2": "m2", "M3": "m3", "KG": "Kg", "H": "Hr", "UN": "Pza", "L": "L"}
UNID_ITEM_OK = {("m2", "M2"), ("m3", "M3"), ("m", "M"), ("Kg", "KG"), ("Pza", "UN"), ("Glb", "UN")}
ORDEN_TIPO = {"MATERIAL": 0, "MANO_DE_OBRA": 1, "HERRAMIENTA": 2}
TOL_AVISO, TOL_SALTO = 0.01, 0.05


def rutas(raiz):
    return {
        "items": os.path.join(raiz, "catalogo", "v1.0", "items_BR.json"),
        "precios": os.path.join(raiz, "precios", "v1.0", "oficiales_BR.json"),
        "mapa": os.path.join(raiz, "precios", "fuentes", "mapa_sinapi_BR.csv"),
        "fuente": os.path.join(raiz, "precios", "fuentes", "sinapi_BR.json"),
        "analisis": os.path.join(raiz, "catalogo", "fuentes", "analisis_composicoes_BR_20260928.md"),
        "manifest": os.path.join(raiz, "manifest.json"),
        "resumen": os.path.join(raiz, "catalogo", "fuentes", "fase_a_BR_20260928.md"),
        "tool_precios": os.path.join(raiz, "tools", "precios-sinapi-br.py"),
    }


# ───────────────────────── lectura ─────────────────────────
def leer_json(p):
    raw = io.open(p, encoding="utf-8", newline="").read()
    return json.loads(raw), ("\r\n" in raw), raw.endswith("\n")


def escribir_json(p, obj, crlf, fin):
    t = json.dumps(obj, ensure_ascii=False, indent=2) + ("\n" if fin else "")
    io.open(p, "w", encoding="utf-8", newline="").write(t.replace("\n", "\r\n") if crlf else t)


def cod(v):
    if v is None: return None
    if isinstance(v, float): v = int(v)
    s = str(v).strip()
    m = re.search(r"MATCH\((\d{2,7})", s)
    return m.group(1) if m else s


def leer_libro(xlsx):
    """ICD/CCD {codigo: {d,u,clas,p{UF:precio}}}, Analítico {codigo: {d,u,sit,l[(tipo,cod,d,u,coef)]}}, mes."""
    wb = openpyxl.load_workbook(xlsx, read_only=True, data_only=False)
    hojas, mes = {}, None
    for h in ("ICD", "CCD"):
        filas = wb[h].iter_rows(values_only=True)
        cab = [next(filas) for _ in range(10)]
        for r in cab[:6]:
            for c in r:
                m = re.search(r"\b(\d{2}/\d{4})\b", str(c or ""))
                if m and not mes: mes = m.group(1)
        fila_uf = cab[9] if h == "ICD" else cab[8]
        ufs = {i: str(c).strip() for i, c in enumerate(fila_uf) if re.fullmatch(r"[A-Z]{2}", str(c or "").strip())}
        d = {}
        for r in filas:
            c = cod(r[1])
            if not c or not re.fullmatch(r"\d{2,7}", c): continue
            p = {}
            for i, uf in ufs.items():
                v = r[i] if i < len(r) else None
                try:
                    v = float(v) if v not in (None, "", "-") else None
                except (TypeError, ValueError):
                    v = None
                if v: p[uf] = v
            d[c] = {"d": str(r[2] or "").strip(), "u": str(r[3] or "").strip(), "clas": str(r[0] or "").strip(), "p": p}
        hojas[h] = d
    comp = {}
    for i, r in enumerate(wb["Analítico"].iter_rows(values_only=True)):
        if i < 10: continue
        r = (list(r) + [None] * 8)[:8]
        _, cc, tipo, ci, desc, u, coef, sit = r
        cc = cod(cc)
        if not cc: continue
        if tipo is None:
            comp[cc] = {"d": str(desc or "").strip(), "u": str(u or "").strip(), "sit": sit, "l": []}
        elif cc in comp:
            comp[cc]["l"].append((str(tipo).strip(), cod(ci), str(desc or "").strip(), str(u or "").strip(), float(coef or 0)))
    wb.close()
    return hojas, comp, mes


def leer_equivalentes(p):
    L = io.open(p, encoding="utf-8").read().split("\n")
    i, j = L.index("## EQUIVALENTE"), L.index("## PARCIAL")
    out = []
    for l in L[i:j]:
        m = re.match(r"\| ([A-Z]{2}\d{3}BR) ", l)
        if not m: continue
        c = [x.strip() for x in l.strip().strip("|").split("|")]
        mc = re.fullmatch(r"(\d+)(?:\s*×\s*([\d.,]+))?", c[2])
        out.append({"codigo": m.group(1), "unidad": c[1], "comp": mc.group(1) if mc else c[2],
                    "factor": mc.group(2) if mc else None, "nota": c[3]})
    return out


# ───────────────────────── nombres, unidades y categorías ─────────────────────────
MIN = {"de", "da", "do", "das", "dos", "e", "em", "com", "para", "por", "a", "o", "as", "os", "ou", "sem", "na", "no",
       "nas", "nos", "ao", "aos", "à", "às", "até", "sob", "sobre", "entre", "tipo", "x"}
SIGLAS = {"PVC", "CP", "II", "III", "IV", "AC", "CA", "DN", "PBA", "JEI", "JE", "PEAD", "PE", "EPS", "LED", "PU", "ABNT",
          "NBR", "BWG", "UV", "CPVC", "PPR", "MDF", "OSB", "ST", "RU", "RF", "HP", "KVA", "CV", "CHP", "CHI", "PP", "PET",
          "EPDM", "NR", "SDR", "PN", "ABS", "GLP", "TV", "HDPE", "PEX", "CFTV", "ISO", "FCK", "UTP", "IP", "AWG", "XLPE",
          "EPR", "HEPR", "BTU", "PTFE", "AWS", "PBT", "VPT", "ZN", "AL", "PS1"}
UNID_TXT = {"MM": "mm", "CM": "cm", "M": "m", "M2": "m²", "M3": "m³", "KN": "kN", "KGF": "kgf", "KG": "kg", "GR": "g",
            "KV": "kV", "W": "W", "V": "V", "L": "L", "MPA": "MPa", "TM": "t·m", "T": "t", "MM2": "mm²"}
# El SINAPI escribe los insumos sin tildes: se reponen las palabras frecuentes (portugués de Brasil).
TILDES = {w.lower(): w for w in """
Aço Aços Água Águas Alumínio Automático Automática Ação Adição Aplicação Asfáltica Asfáltico Até Basáltica Bombeável
Cabeça Calcário Calçamento Cerâmica Cerâmico Cimentícios Cimentício Colocação Compressão Conexões Contínuos Diâmetro
Dilatação Dimensões Distribuição Elástica Elastômeros Emulsão Epóxi Espaçador Fêmea Fixação Flexível Geotêxtil Grão
Granítica Granulométrica Holandês Impermeabilização Instalação Ipê Isolação Ladrão Lâmina Látex Acrílica Acrílico Ligação
Líquida Líquido Locação Louça Maciça Maciço Mão Metálica Metálico Mictório Mínimo Máximo Não Óleo Orgânico Paralelepípedo
Pavimentação Peça Peças Plástica Plástico Poliédrico Poliéster Potência Pressão Pré Pirenópolis Rápida Região Regulável
Reforçada Reforço Resistência Rodízios Saída Sanitária Serviço Sifão Tábua Tampão Telescópica Tensão Tração Trifásico
Trifásica Tripé Vão Vedação Vergalhão Válvula Lavatório Acessórios Gabião Pó Três Tomé São Luminária Elétrico Elétrica
Hidráulico Hidráulica Operação Proteção Manutenção Rotação Distância Carga Útil Líq Mín Máx Caçamba Tração
Esgoto Borracha Anéis Anel Tubulação Conexão Junção Redução Válvulas Sifonada Hexagonal Quadrangular Losangular Grelha
Rodapé Sintético Sanitário Mínima Diluídos Elétricos Hidráulicos Cimentício Galvanização Espécie Pé Rígido Rígida
""".split()}


def sin_acento(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


TILDES_SA = {sin_acento(k): v for k, v in TILDES.items()}


def _palabra(p, primera):
    up = p.upper()
    if up in SIGLAS: return up
    if up in UNID_TXT and not primera: return UNID_TXT[up]
    if re.search(r"\d", p):
        if re.match(r"^[A-Za-z]{1,3}-?\d", p): return up           # CA-60, S10, E6013, H16
        m = re.fullmatch(r"(\d+(?:[.,]\d+)?)([A-Za-z]+\d?)", p)    # 20MM, 5HP
        if m and m.group(2).upper() in UNID_TXT: return m.group(1) + UNID_TXT[m.group(2).upper()]
        if m and m.group(2).upper() in SIGLAS: return m.group(1) + " " + m.group(2).upper()
        return p.lower()
    low = p.lower()
    if low in MIN and not primera: return low
    t = TILDES_SA.get(sin_acento(low))
    if t: return t
    return low[:1].upper() + low[1:]


def nombre_pt(desc, quitar_encargos=False, largo=140):
    s = re.sub(r"\s*AF_\d{2}/\d{4}.*$", "", desc).replace("*", "")
    if quitar_encargos: s = re.sub(r"\s*COM ENCARGOS COMPLEMENTARES\s*$", "", s)
    s = re.sub(r"\s+", " ", s).strip(" .,-")
    out = []
    for k, w in enumerate(s.split(" ")):
        partes = re.split(r"([/(),\-'])", w)
        res = [p if (not p or re.fullmatch(r"[/(),\-']", p)) else _palabra(p, k == 0 and n == 0)
               for n, p in enumerate(partes)]
        out.append("".join(res))
    s = " ".join(out)
    if len(s) > largo:  # se corta en una coma, sin partir un dato
        cortes = [m.start() for m in re.finditer(r", ", s) if m.start() <= largo]
        if cortes: s = s[:cortes[-1]]
    return s


def nombre_equipo(desc, hojas, elegido, sp_por_id):
    """CHP/CHI nuevo: nombre corto; si su par (CHP<->CHI) ya es insumo BR, se usa el nombre de ese insumo."""
    d = desc.upper()
    esp = "CHI" if re.search(r"\bCHI\b", d) else "CHP"
    otro = re.sub(r"\bCH[PI]\b", "CHP" if esp == "CHI" else "CHI", d)
    par = next((c for c, v in hojas["CCD"].items() if v["d"].upper() == otro), None)
    suf = " (CHI, hora improdutiva)" if esp == "CHI" else " (CHP, hora produtiva)"
    if par and ("CCD", par) in elegido:
        return sp_por_id[elegido[("CCD", par)]["idCanonico"]]["nombre"] + suf
    base = re.split(r"\s+-\s+CH[PI]\b", desc)[0]
    return nombre_pt(base.split(",")[0]) + suf


CAT_PALABRAS = [  # (regex sobre la descripción SINAPI sin tildes, categoría ArqOn) — antes que lo aprendido del mapa
    (r"^(CAIXA SIFONADA|CAIXA DE GORDURA|RALO)", "Plomería"),
    (r"^(HASTE RETA PARA GANCHO|TELHA|CUMEEIRA|RUFO|CALHA)", "Cubiertas"),
    (r"^(CIMENTO|CAL |CAL HIDRATADA|GESSO|ARGAMASSA|REJUNTE|CONCRETO USINADO|GRAUTE|MASSA DE REJUNTE)", "Cemento y Cal"),
    (r"^(AREIA|PEDRA|BRITA|PO DE PEDRA|SOLO|SAIBRO|ARGILA|CASCALHO|RACHAO)", "Agregados"),
    (r"^(TINTA|SELADOR|MASSA (ACRILICA|CORRIDA)|FUNDO|ESMALTE|VERNIZ|LIXA|SOLVENTE|DILUENTE|TEXTURA|ZARCAO|DESMOLDANTE)", "Pinturas"),
    (r"^(ADITIVO|IMPERMEABILIZANTE|EMULSAO|MANTA|PRIMER|ASFALTO|SELANTE)", "Impermeabilización"),
    (r"^(ADESIVO|COLA)", "Adhesivos"),
    (r"^(TABUA|SARRAFO|PONTALETE|VIGA [0-9,]+ X|VIGA DE MADEIRA|CAIBRO|RIPA|MADEIRA|CHAPA/PAINEL DE MADEIRA|COMPENSADO|BATENTE|TACO|ASSOALHO|RODAPE DE MADEIRA)", "Madera"),
    (r"^(BLOCO|TIJOLO|BLOQUETE|LADRILHO|REVESTIMENTO CERAMICO|PISO CERAMICO|PORCELANATO|AZULEJO|PASTILHA|CERAMICA)", "Ladrillos y Cerámicos"),
    (r"^(LAJE PRE-MOLDADA|VIGOTA)", "Obras Civiles"),
    (r"^(ACO |VERGALHAO|TELA|ARAME|PERFIL|CHAPA|CANTONEIRA|BARRA|PARAFUSO|PINO|GRAMPO|CHUMBADOR|GABIAO|COLCHAO|ELETRODO|ESPACADOR|PREGO|SUPORTE|PENDURAL)", "Acero y Metal"),
    (r"^(CABO|FIO|ELETRODUTO|DISJUNTOR|INTERRUPTOR|TOMADA|LUMINARIA|LAMPADA|QUADRO|CAIXA DE PASSAGEM|TRANSFORMADOR|CONDULETE|PLAFON|TERMINAL|FITA ISOLANTE|CONDICIONADOR|AR CONDICIONADO)", "Eléctrico"),
    (r"^(TUBO|JOELHO|CURVA|LUVA|TE |REGISTRO|VALVULA|SIFAO|ENGATE|BACIA|LAVATORIO|MICTORIO|TORNEIRA|ADAPTADOR|NIPLE|UNIAO|TAMPAO|ANEL|REDUCAO|ASSENTO|CUBA|MISTURADOR|KIT DE ACESSORIOS|PASTA LUBRIFICANTE|FITA VEDA)", "Plomería"),
    (r"^(BUCHA|GEOTEXTIL|JUNTA PLASTICA|FITA DE PAPEL)", "Ferretería"),
]


def categoria_nueva(desc, tipo, clas, cats_por_palabra):
    d = sin_acento(desc.upper())
    if tipo == "MANO_DE_OBRA":
        return "No Calificada" if re.match(r"^(SERVENTE|AJUDANTE|AUXILIAR)", d) else "Calificada"
    if tipo == "HERRAMIENTA": return "Herramientas" if "LOCACAO" in sin_acento(clas.upper()) else "Maquinaria"
    if clas.upper().startswith("SERVI"): return "Obras Civiles"
    for rx, cat in CAT_PALABRAS:
        if re.match(rx, d): return cat
    w = d.split(" ")[0].strip(",")
    return cats_por_palabra.get(w, "Ferretería")


# unidad SINAPI → (unidad ArqOn, factor del mapa: precio ArqOn = precio SINAPI × factor; rendimiento = coef ÷ factor)
UNID_NUEVA = {"M": ("m", 1), "M2": ("m2", 1), "M3": ("m3", 1), "KG": ("Kg", 1), "H": ("Hr", 1), "CHP": ("Hr", 1),
              "CHI": ("Hr", 1), "UN": ("Pza", 1), "L": ("L", 1), "CJ": ("Pza", 1), "JG": ("Pza", 1), "PAR": ("Pza", 1),
              "CENTO": ("Pza", 0.01), "MIL": ("Pza", 0.001), "MXMES": ("m×mes", 1), "UNXMES": ("Pza×mes", 1)}


def unidad_nueva(u):
    return UNID_NUEVA.get(u.upper().replace(" ", ""), (u.lower(), 1))


# ───────────────────────── aplanado ─────────────────────────
def es_mo(desc):
    return "COM ENCARGOS COMPLEMENTARES" in desc.upper()


def es_eq(desc):
    return re.search(r"\bCH[PI]\b", desc.upper()) is not None


def aplanar(cc, comp, coef=1.0, prof=0, acc=None, orden=None, camino=()):
    """{(hoja, codigo): cantidad} por 1 unidad de la composición cc."""
    acc = {} if acc is None else acc
    orden = [] if orden is None else orden
    if cc in camino: raise ValueError(f"ciclo en {cc}")
    for tipo, ci, d, u, k in comp[cc]["l"]:
        q = coef * k
        if not q: continue
        if tipo == "INSUMO":
            key = ("ICD", ci, "MATERIAL")
        elif es_mo(d):
            key = ("CCD", ci, "MANO_DE_OBRA")
        elif es_eq(d):
            key = ("CCD", ci, "HERRAMIENTA")
        else:
            if ci not in comp: raise KeyError(f"composición auxiliar {ci} no está en el Analítico")
            aplanar(ci, comp, q, prof + 1, acc, orden, camino + (cc,))
            continue
        if key not in acc: orden.append(key)
        acc[key] = acc.get(key, 0.0) + q
    return acc, orden


# ───────────────────────── núcleo ─────────────────────────
def calcular(R, libro_path):
    fuente = json.load(io.open(R["fuente"], encoding="utf-8"))
    sha = hashlib.sha256(open(libro_path, "rb").read()).hexdigest()
    if sha != fuente.get("sha256"):
        sys.exit(f"El libro {libro_path} (sha256 {sha[:12]}…) no es el registrado en sinapi_BR.json ({fuente.get('sha256','')[:12]}…). Paro.")
    hojas, comp, mes = leer_libro(libro_path)
    items_doc, _, _ = leer_json(R["items"])
    precios_doc, _, _ = leer_json(R["precios"])
    mapa = list(csv.DictReader(io.open(R["mapa"], encoding="utf-8")))
    equiv = leer_equivalentes(R["analisis"])
    ref_txt = lambda c: f"SINAPI {c} · {mes}"

    sp = next(c for c in precios_doc["ciudades"] if c["nombre"] == "São Paulo")
    sp_por_id = {x["idCanonico"]: x for x in sp["precios"]}
    items = {x["codigo"]: x for x in items_doc["items"]}
    uso = {}
    for it in items_doc["items"]:
        for l in it["insumos"]: uso[l["idCanonico"]] = uso.get(l["idCanonico"], 0) + 1

    # hoja+código → insumo BR ya mapeado (se prefiere factor 1, luego el más usado, luego el id)
    por_cod = {}
    for r in mapa:
        if r["idCanonico"] not in sp_por_id: continue
        por_cod.setdefault((r["hoja"], r["codigoSinapi"]), []).append(r)
    elegido, ambiguos = {}, {}
    for k, rs in por_cod.items():
        rs.sort(key=lambda r: (float(r["factor"]) != 1.0, -uso.get(r["idCanonico"], 0), r["idCanonico"]))
        # Varios insumos BR con el mismo código SINAPI y NINGUNO en su unidad (p. ej. barras de Ø12 y Ø16 del
        # mismo «CA-50 12,5 OU 16 MM» por kg): elegir uno sería inventar el diámetro → insumo nuevo en la unidad SINAPI.
        if float(rs[0]["factor"]) != 1.0 and len({r["factor"] for r in rs}) > 1:
            ambiguos[k] = [r["idCanonico"] for r in rs]
            continue
        elegido[k] = rs[0]
    # primera palabra de la descripción SINAPI → categoría BR (de lo ya mapeado)
    cnt = {}
    for r in mapa:
        x = sp_por_id.get(r["idCanonico"])
        if not x or x["tipoInsumo"] != "MATERIAL": continue
        w = sin_acento(r["descripcionSinapi"].upper()).split(" ")[0].strip(",")
        cnt.setdefault(w, {}).setdefault(x["categoria"], 0)
        cnt[w][x["categoria"]] += 1
    cats_por_palabra = {w: max(c.items(), key=lambda kv: (kv[1], kv[0]))[0] for w, c in cnt.items()}
    codigos_existentes = {x["codigo"] for x in sp["precios"]}
    nombres_usados = {x["nombre"]: x["idCanonico"] for x in sp["precios"]}

    convertidos, saltados, nuevos = [], [], {}
    for e in equiv:
        it = items.get(e["codigo"])
        c = e["comp"]
        if not it:
            saltados.append((e, "el ítem no está en items_BR.json")); continue
        if e["factor"]:
            saltados.append((e, f"unidad distinta: la tabla pide factor ×{e['factor']} ({it['unidadResultado']} ↔ {comp.get(c, {}).get('u', '?')}); decidir aparte")); continue
        if c not in comp:
            saltados.append((e, f"la composición {c} no está en el Analítico {mes}")); continue
        cu = comp[c]["u"].upper()
        if (it["unidadResultado"], cu) not in UNID_ITEM_OK:
            saltados.append((e, f"unidad distinta: ítem {it['unidadResultado']} ↔ composición {cu}")); continue
        ccd_sp = hojas["CCD"].get(c, {}).get("p", {}).get("SP")
        if not ccd_sp:
            saltados.append((e, f"la composición {c} no tiene costo en SP en {mes} (CCD vacío)")); continue
        try:
            acc, orden = aplanar(c, comp)
        except (KeyError, ValueError) as ex:
            saltados.append((e, f"no se pudo aplanar: {ex}")); continue
        faltan = [f"{h} {ci}" for (h, ci, t) in orden if not hojas[h].get(ci, {}).get("p", {}).get("SP")]
        if faltan:
            saltados.append((e, "sin precio SINAPI en SP para: " + ", ".join(faltan))); continue
        lineas, costo_sin, costo_nuevo = [], 0.0, 0.0
        for n, key in enumerate(orden):
            h, ci, tipo = key
            q = acc[key]
            s = hojas[h][ci]
            costo_sin += q * s["p"]["SP"]
            m = elegido.get((h, ci))
            if m:
                x = sp_por_id[m["idCanonico"]]
                f = float(m["factor"])
                rend = q / f
                base = {"nombre": x["nombre"], "unidad": x["unidad"], "tipoInsumo": x["tipoInsumo"], "categoria": x["categoria"],
                        "idCanonico": x["idCanonico"], "codigo": x["codigo"]}
                precio_sp = x["precio"]
                es_nuevo = False
            else:
                idc = f"br_sinapi_{h.lower()}_{ci}"
                codigo = f"BR_S{'I' if h == 'ICD' else 'C'}{ci}"
                assert codigo not in codigos_existentes or idc in sp_por_id, codigo
                if h == "ICD":
                    clas = sin_acento(s["clas"].upper())
                    if clas.startswith("EQUIPAMENTO (LOCACAO"): tipo = "HERRAMIENTA"
                    elif clas.startswith("MAO DE OBRA"): tipo = "MANO_DE_OBRA"
                if tipo == "HERRAMIENTA" and h == "CCD":
                    nombre = nombre_equipo(s["d"], hojas, elegido, sp_por_id)
                else:
                    nombre = nombre_pt(s["d"], quitar_encargos=(tipo == "MANO_DE_OBRA"))
                if nombre in nombres_usados and nombres_usados[nombre] != idc:
                    nombre = nombre_pt(s["d"], quitar_encargos=(tipo == "MANO_DE_OBRA"), largo=10 ** 4)
                nombres_usados.setdefault(nombre, idc)
                unidad, f = unidad_nueva(s["u"])
                base = {"nombre": nombre, "unidad": unidad, "tipoInsumo": tipo,
                        "categoria": categoria_nueva(s["d"], tipo, s["clas"], cats_por_palabra),
                        "idCanonico": idc, "codigo": codigo}
                if idc in sp_por_id:  # ya creado en una corrida anterior
                    x = sp_por_id[idc]
                    base.update({k: x[k] for k in ("nombre", "unidad", "tipoInsumo", "categoria", "codigo")})
                rend, precio_sp, es_nuevo = q / f, round(s["p"]["SP"] * f, 4 if f != 1 else 2), idc not in sp_por_id
                if es_nuevo:
                    nuevos.setdefault(idc, {**base, "hoja": h, "codigoSinapi": ci, "unidadSinapi": s["u"], "factor": f,
                                            "descripcionSinapi": s["d"], "precioSP": precio_sp, "items": []})
                    nuevos[idc]["items"].append(it["codigo"])
            costo_nuevo += rend * precio_sp
            lineas.append((ORDEN_TIPO.get(base["tipoInsumo"], 9), n, {
                "nombre": base["nombre"], "unidad": base["unidad"], "tipoInsumo": base["tipoInsumo"],
                "categoria": base["categoria"], "rendimiento": float(f"{rend:.7g}"), "precio": 0,
                "tipoCalculo": "DIRECTO", "baseCalculo": "", "idCanonico": base["idCanonico"], "codigo": base["codigo"]}))
        lineas = [l for _, _, l in sorted(lineas, key=lambda t: (t[0], t[1]))]
        dif = costo_sin / ccd_sp - 1
        if abs(dif) > TOL_SALTO:
            saltados.append((e, f"el aplanado da {costo_sin:.2f} en SP y el CCD publica {ccd_sp:.2f} ({dif:+.1%})")); continue
        costo_hoy = sum(l["rendimiento"] * sp_por_id.get(l["idCanonico"], {}).get("precio", 0) for l in it["insumos"])
        convertidos.append({"e": e, "item": it, "lineas": lineas, "ref": ref_txt(c), "ccd_sp": ccd_sp,
                            "costo_sin": costo_sin, "costo_nuevo": costo_nuevo, "costo_hoy": costo_hoy, "dif": dif,
                            "comp_d": comp[c]["d"], "comp_u": cu,
                            "cambia": it["insumos"] != lineas or it.get("referencia") != ref_txt(c)})
    return {"mes": mes, "sha": sha, "ambiguos": ambiguos, "convertidos": convertidos, "saltados": saltados, "nuevos": nuevos,
            "items_doc": items_doc, "precios_doc": precios_doc, "sp_por_id": sp_por_id, "equiv": equiv}


# ───────────────────────── aplicar ─────────────────────────
PENDIENTE = "PENDIENTE: lo pone tools/precios-sinapi-br.py."


def aplicar(R, res, libro_path):
    """Orden seguro: 1) insumos nuevos a precios + mapa, 2) precio SINAPI por UF, 3) comprobar que TODO insumo de
    las recetas nuevas tiene precio SINAPI en las 10 ciudades, 4) recién entonces se escriben las recetas."""
    nuevos = res["nuevos"]
    precios_doc, crlf_p, fin_p = leer_json(R["precios"])
    version_antes = precios_doc["version"]
    if nuevos:
        for c in precios_doc["ciudades"]:
            ya = {x["idCanonico"] for x in c["precios"]}
            for idc, x in sorted(nuevos.items()):
                if idc in ya: continue
                c["precios"].append({"idCanonico": idc, "nombre": x["nombre"], "categoria": x["categoria"], "unidad": x["unidad"],
                                     "tipoInsumo": x["tipoInsumo"], "codigo": x["codigo"], "precio": 0, "nota": PENDIENTE})
        escribir_json(R["precios"], precios_doc, crlf_p, fin_p)
        raw = io.open(R["mapa"], encoding="utf-8", newline="").read()
        ya = {r["idCanonico"] for r in csv.DictReader(io.StringIO(raw))}
        campos = ["idCanonico", "codigoSinapi", "hoja", "factor", "unidadArqon", "unidadSinapi", "descripcionSinapi"]
        buf = io.StringIO()
        w = csv.DictWriter(buf, fieldnames=campos, lineterminator="\n")
        for idc, x in sorted(nuevos.items()):
            if idc in ya: continue
            w.writerow({"idCanonico": idc, "codigoSinapi": x["codigoSinapi"], "hoja": x["hoja"], "factor": repr(float(x["factor"])),
                        "unidadArqon": x["unidad"], "unidadSinapi": x["unidadSinapi"], "descripcionSinapi": x["descripcionSinapi"][:120]})
        io.open(R["mapa"], "w", encoding="utf-8", newline="").write(raw + ("" if raw.endswith("\n") else "\n") + buf.getvalue())
    pendientes = any(x.get("nota") == PENDIENTE for c in precios_doc["ciudades"] for x in c["precios"])
    if nuevos or pendientes:
        # precio SINAPI por UF (misma regla de siempre: UF de la ciudad; si falta, SP)
        env = dict(os.environ, PYTHONIOENCODING="utf-8")
        r = subprocess.run([sys.executable, "-B", R["tool_precios"], libro_path], capture_output=True, text=True,
                           encoding="utf-8", errors="replace", env=env)
        print((r.stdout or "").strip(), (r.stderr or "").strip())
        if r.returncode: sys.exit("precios-sinapi-br.py falló: las recetas NO se escribieron")
        precios_doc, crlf_p, fin_p = leer_json(R["precios"])
        if precios_doc["version"] == version_antes:  # mismo día que la corrida anterior: la app no bajaría los precios
            m = re.match(r"v(\d{8})([a-z]?)(-.*)", version_antes)
            letra = chr(ord(m.group(2)) + 1) if m.group(2) else "b"
            precios_doc["version"] = f"v{m.group(1)}{letra}{m.group(3)}"
            escribir_json(R["precios"], precios_doc, crlf_p, fin_p)
        set_manifest(R["manifest"], "precios_BR", precios_doc["version"])
        print(f"oficiales_BR.json: +{len(nuevos)} insumos en las 10 ciudades · versión {precios_doc['version']}")
    else:
        print("oficiales_BR.json: sin insumos nuevos (no se toca)")

    # 3) todo insumo de las recetas nuevas, con precio SINAPI en cada ciudad
    malos = []
    usados = {l["idCanonico"] for cv in res["convertidos"] for l in cv["lineas"]}
    for c in precios_doc["ciudades"]:
        por_id = {x["idCanonico"]: x for x in c["precios"]}
        for idc in sorted(usados):
            x = por_id.get(idc)
            if not x or not x.get("precio") or not x.get("nota", "").startswith("REFERENCIA: SINAPI"):
                malos.append(f"{c['nombre']}:{idc}")
    if malos:
        sys.exit(f"{len(malos)} insumos sin precio SINAPI (p. ej. {malos[:5]}): las recetas NO se escribieron")

    # 4) recetas
    items_doc, crlf_i, fin_i = leer_json(R["items"])
    por_cod = {x["codigo"]: x for x in items_doc["items"]}
    n = 0
    for cv in res["convertidos"]:
        if not cv["cambia"]: continue
        it = por_cod[cv["item"]["codigo"]]
        it["insumos"] = cv["lineas"]
        it["referencia"] = cv["ref"]
        n += 1
    if n:
        items_doc["version"] = VERSION_CATALOGO
        escribir_json(R["items"], items_doc, crlf_i, fin_i)
        set_manifest(R["manifest"], "catalogo_BR", VERSION_CATALOGO)
    print(f"items_BR.json: {n} ítems convertidos · versión {items_doc['version']}")


def set_manifest(p, clave, version):
    raw = io.open(p, encoding="utf-8", newline="").read()
    nuevo = re.sub(r'("' + clave + r'"\s*:\s*\{[^}]*?"version"\s*:\s*")[^"]*(")', lambda m: m.group(1) + version + m.group(2), raw, count=1)
    assert f'"{clave}"' in raw, f"no encontré {clave} en el manifiesto"
    io.open(p, "w", encoding="utf-8", newline="").write(nuevo)


# ───────────────────────── resumen ─────────────────────────
def fmt(v, d=2):
    return f"{v:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def resumen(res):
    conv, salt, nuevos, sp = res["convertidos"], res["saltados"], res["nuevos"], res["sp_por_id"]
    mes = res["mes"]
    precio_sp = lambda idc: sp[idc]["precio"] if idc in sp else nuevos[idc]["precioSP"]
    o = []
    o.append(f"# Brasil, fase A: recetas EQUIVALENTE = composición SINAPI (resumen, {datetime.date.today():%d-%m-%Y})\n")
    o.append(f"Herramienta: `tools/fase-a-composicoes-br.py` (sin `--aplicar` no toca datos). Fuente: SINAPI (Caixa/IBGE) {mes}, "
             f"hojas Analítico (coeficientes) y ICD/CCD (COM desoneração), libro nacional sha256 `{res['sha'][:8]}…{res['sha'][-6:]}`. "
             f"Versión al aplicar: catalogo_BR `{VERSION_CATALOGO}`; precios_BR sube de versión porque entran insumos nuevos.\n")
    o.append("Sólo cambia la lista `insumos` de cada ítem convertido y se le agrega `referencia: \"SINAPI NNNNN · "
             f"{mes}\"`; código, nombre, categoría, unidad, parámetros, fórmula, tipoIfc, etiqueta y «verificado» quedan iguales. "
             "Mano de obra «com encargos complementares» y costo horario de equipo (CHP/CHI) van como UNA línea con el costo CCD; "
             "las auxiliares (argamassa, concreto, armação…) se abren en sus insumos. Los loaders del PC y de la APK ignoran "
             "`referencia` sin romperse (el PC copia campos por nombre; la APK decodifica con `ignoreUnknownKeys = true`): hoy no se "
             "muestra en pantalla.\n")
    pend = [c for c in conv if c["cambia"]]
    o.append("## Cuántos\n")
    o.append(f"| | Ítems |\n|---|---:|\n| EQUIVALENTE en el análisis | {len(res['equiv'])} |\n| Convertidos | {len(conv)} |"
             f"\n| … de ellos, con cambios pendientes | {len(pend)} |\n| Salteados | {len(salt)} |\n")
    cats = {}
    for c in conv: cats[c["item"]["categoria"]] = cats.get(c["item"]["categoria"], 0) + 1
    o.append("### Convertidos por categoría\n\n| Categoría | Ítems |\n|---|---:|")
    for k, v in sorted(cats.items(), key=lambda kv: -kv[1]): o.append(f"| {k} | {v} |")
    glb = [c["item"]["codigo"] for c in conv if c["item"]["unidadResultado"] == "Glb"]
    if glb:
        o.append(f"\nUnidad «Glb» del ítem tomada como 1 unidad (UN) de la composición: {', '.join(glb)}.")
    o.append("")
    o.append("## Salteados (no se tocan)\n\n| Ítem | Composición | Motivo |\n|---|---|---|")
    for e, why in salt:
        o.append(f"| {e['codigo']} {res['items_doc'] and next((x['nombre'] for x in res['items_doc']['items'] if x['codigo']==e['codigo']), '')} | {e['comp']} | {why} |")
    o.append("")
    avisos = [c for c in conv if abs(c["dif"]) > TOL_AVISO]
    if avisos:
        o.append(f"### Aviso: aplanado vs costo CCD publicado entre 1 y 5 % ({len(avisos)})\n")
        o.append("El SINAPI trunca cada línea a 2 decimales y redondea las auxiliares; diferencias chicas son esperables.\n")
        o.append("| Ítem | Composición | Aplanado SP | CCD SP | Dif. |\n|---|---|---:|---:|---:|")
        for c in avisos: o.append(f"| {c['item']['codigo']} | {c['e']['comp']} | {fmt(c['costo_sin'])} | {fmt(c['ccd_sp'])} | {c['dif']:+.1%} |")
        o.append("")
    # insumos nuevos
    o.append(f"## Insumos nuevos ({len(nuevos)})\n")
    o.append("Se crean con id `br_sinapi_<hoja>_<código>`, se agregan a las 10 ciudades de `oficiales_BR.json` y a "
             "`mapa_sinapi_BR.csv` (factor 1; «CENTO» pasa a Pza con factor 0,01), y `precios-sinapi-br.py` les pone el precio SINAPI de cada UF (si la UF no "
             "tiene, el de SP).\n")
    usados_amb = {k: v for k, v in res["ambiguos"].items() if f"br_sinapi_{k[0].lower()}_{k[1]}" in nuevos}
    if usados_amb:
        o.append("Códigos SINAPI con varios insumos BR mapeados en otra unidad (ninguno con factor 1): no se elige uno "
                 "(sería inventar la medida); se crea el insumo en la unidad SINAPI: " +
                 "; ".join(f"{h} {c} ({', '.join('`'+i+'`' for i in v)})" for (h, c), v in sorted(usados_amb.items())) + ".\n")
    por_t = {}
    for x in nuevos.values(): por_t[x["tipoInsumo"]] = por_t.get(x["tipoInsumo"], 0) + 1
    o.append(" · ".join(f"{k}: {v}" for k, v in sorted(por_t.items())) + "\n")
    o.append("| idCanonico | Nombre | Unidad | Tipo | Categoría | Precio SP | Ítems |\n|---|---|---|---|---|---:|---|")
    for idc, x in sorted(nuevos.items(), key=lambda kv: (kv[1]["tipoInsumo"], kv[1]["categoria"], kv[1]["nombre"])):
        its = sorted(set(x["items"]))
        o.append(f"| `{idc}` | {x['nombre']} | {x['unidad']} | {x['tipoInsumo']} | {x['categoria']} | {fmt(x['precioSP'])} | "
                 f"{', '.join(its[:4])}{' …+' + str(len(its) - 4) if len(its) > 4 else ''} |")
    o.append("")
    # costos
    rat = [c["costo_nuevo"] / c["costo_hoy"] for c in conv if c["costo_hoy"]]
    o.append("## Cambio del costo directo en São Paulo\n")
    o.append("«Hoy» = receta actual con los precios BR actuales; «SINAPI» = receta nueva con precios SINAPI SP "
             "(los mismos que quedarán en oficiales_BR.json). Sin cargas sociales ni BDI.\n")
    if rat:
        q = statistics.quantiles(rat, n=4)
        o.append(f"- Cociente SINAPI / hoy: mediana **{fmt(statistics.median(rat))}**, cuartiles {fmt(q[0])}–{fmt(q[2])}, "
                 f"rango {fmt(min(rat))}–{fmt(max(rat))} ({len(rat)} ítems).")
        o.append(f"- Suma de los ítems convertidos (1 unidad de cada uno): hoy {fmt(sum(c['costo_hoy'] for c in conv))} → "
                 f"SINAPI {fmt(sum(c['costo_nuevo'] for c in conv))}.")
        o.append(f"- Bajan > 50 %: {sum(r < 0.5 for r in rat)} · suben > 100 %: {sum(r > 2 for r in rat)}.\n")
    o.append("### Los 20 cambios más grandes (por |ln(SINAPI/hoy)|)\n")
    o.append("| Ítem | Unidad | Composición | Hoy | SINAPI | SINAPI/hoy |\n|---|---|---|---:|---:|---:|")
    import math
    top = sorted([c for c in conv if c["costo_hoy"] and c["costo_nuevo"]], key=lambda c: -abs(math.log(c["costo_nuevo"] / c["costo_hoy"])))[:20]
    for c in top:
        o.append(f"| {c['item']['codigo']} {c['item']['nombre']} | {c['item']['unidadResultado']} | {c['e']['comp']} | "
                 f"{fmt(c['costo_hoy'])} | {fmt(c['costo_nuevo'])} | {fmt(c['costo_nuevo'] / c['costo_hoy'])} |")
    o.append("\n### Todos los convertidos\n")
    o.append("| Ítem | Unidad | Composición | Líneas antes → después | Hoy | SINAPI | CCD SP publicado |\n|---|---|---|---|---:|---:|---:|")
    for c in sorted(conv, key=lambda c: c["item"]["codigo"]):
        o.append(f"| {c['item']['codigo']} {c['item']['nombre']} | {c['item']['unidadResultado']} | {c['e']['comp']} | "
                 f"{len(c['item']['insumos'])} → {len(c['lineas'])} | {fmt(c['costo_hoy'])} | {fmt(c['costo_nuevo'])} | {fmt(c['ccd_sp'])} |")
    o.append("")
    # ejemplos
    pref = ["AC019BR", "UA003BR", "MP002BR", "OG018BR", "OG021BR", "IS005BR", "IS053BR", "IE006BR", "CU015BR", "OT046BR"]
    por_c = {c["item"]["codigo"]: c for c in conv}
    ej = [por_c[k] for k in pref if k in por_c]
    for c in conv:
        if len(ej) >= 10: break
        if c not in ej: ej.append(c)
    o.append("## 10 ejemplos: receta antes y después\n")
    for c in ej[:10]:
        it = c["item"]
        o.append(f"### {it['codigo']} {it['nombre']} [{it['unidadResultado']}] ↔ SINAPI {c['e']['comp']} [{c['comp_u']}]\n")
        o.append(f"_{c['comp_d']}_\n")
        o.append("| Antes: insumo | unidad | rend. | | Después: insumo | unidad | rend. | P. SP |\n|---|---|---:|---|---|---|---:|---:|")
        a, d = it["insumos"], c["lineas"]
        for i in range(max(len(a), len(d))):
            x = a[i] if i < len(a) else None
            y = d[i] if i < len(d) else None
            o.append("| " + (f"{x['nombre']} | {x['unidad']} | {x['rendimiento']:g}" if x else " | | ") + " | | " +
                     (f"{y['nombre']}{' *(nuevo)*' if y['idCanonico'] in nuevos else ''} | {y['unidad']} | {y['rendimiento']:g} | {fmt(precio_sp(y['idCanonico']))}" if y else " | | | ") + " |")
        o.append(f"\nCosto SP: hoy {fmt(c['costo_hoy'])} → SINAPI {fmt(c['costo_nuevo'])} (CCD publicado {fmt(c['ccd_sp'])}).\n")
    # conteos de insumos
    antes = sum(len(c["item"]["insumos"]) for c in conv)
    despues = sum(len(c["lineas"]) for c in conv)
    ids_antes = {l["idCanonico"] for c in conv for l in c["item"]["insumos"]}
    ids_despues = {l["idCanonico"] for c in conv for l in c["lineas"]}
    todos = res["items_doc"]["items"]
    conv_cod = {c["item"]["codigo"] for c in conv}
    usados_resto = {l["idCanonico"] for it in todos if it["codigo"] not in conv_cod for l in it["insumos"]}
    huerfanos = sorted(ids_antes - ids_despues - usados_resto)
    o.append("## Insumos: conteos\n")
    o.append(f"- Líneas de receta en los ítems convertidos: {antes} → {despues}.")
    o.append(f"- Insumos distintos que usan esos ítems: {len(ids_antes)} → {len(ids_despues)} "
             f"({len(ids_despues & set(sp))} ya existentes + {len(ids_despues - set(sp))} nuevos).")
    o.append(f"- Lista de precios BR (por ciudad): {len(sp)} → {len(sp) + len(nuevos)} insumos.")
    o.append(f"- Insumos que dejan de usarse en todo el catálogo BR tras el cambio: {len(huerfanos)} (quedan en la lista de precios; "
             f"se sacarán en la fase de QUITAR){': ' + ', '.join('`'+h+'`' for h in huerfanos) if huerfanos else ''}.\n")
    # control ESTIMADO
    est = sorted({l["idCanonico"] for c in conv for l in c["lineas"]
                  if l["idCanonico"] in sp and not sp[l["idCanonico"]].get("nota", "").startswith(("REFERENCIA: SINAPI", PENDIENTE))})
    o.append("## Control: ningún insumo ESTIMADO en los ítems convertidos\n")
    o.append(("OK: todas las líneas de los ítems convertidos usan insumos con precio «REFERENCIA: SINAPI …» "
              "(los nuevos lo reciben de precios-sinapi-br.py al aplicar).") if not est else
             f"ATENCIÓN: {len(est)} insumos sin precio SINAPI: " + ", ".join(est))
    o.append("")
    return "\n".join(o) + "\n", est


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--libro", default=LIBRO_DEF)
    ap.add_argument("--raiz", default=os.path.dirname(AQUI))
    ap.add_argument("--resumen")
    ap.add_argument("--aplicar", action="store_true")
    # TANDA POR RANGO DE COSTO (28-sep-2026, Oscar: «publica los 74 y revisa los 25»): sólo se convierten los ítems
    # cuyo costo SINAPI/hoy (SP) cae en [--ratio-min, --ratio-max]; los demás pasan a «salteados» para revisarlos
    # uno por uno (alcance: sección, material incluido, espesor), y los insumos nuevos que sólo usan ellos no entran.
    ap.add_argument("--ratio-min", type=float)
    ap.add_argument("--ratio-max", type=float)
    a = ap.parse_args()
    R = rutas(os.path.abspath(a.raiz))
    res = calcular(R, a.libro)
    if a.ratio_min is not None or a.ratio_max is not None:
        lo, hi = a.ratio_min or 0.0, a.ratio_max or float("inf")
        quedan, fuera = [], []
        for c in res["convertidos"]:
            r = (c["costo_nuevo"] / c["costo_hoy"]) if c["costo_hoy"] else None
            (quedan if (r is not None and lo <= r <= hi) else fuera).append(c)
        for c in fuera:
            r = (c["costo_nuevo"] / c["costo_hoy"]) if c["costo_hoy"] else 0
            res["saltados"].append((c["e"], f"revisar alcance: costo SINAPI/hoy = {r:.2f} (fuera de {lo}–{hi})"))
        res["convertidos"] = quedan
        usados = {l["idCanonico"] for c in quedan for l in c["lineas"]}
        res["nuevos"] = {k: v for k, v in res["nuevos"].items() if k in usados}
        print(f"tanda por rango {lo}–{hi}: {len(quedan)} ítems · {len(fuera)} a revisar · {len(res['nuevos'])} insumos nuevos")
    md, est = resumen(res)
    pend = [c for c in res["convertidos"] if c["cambia"]]
    dest = a.resumen or R["resumen"]
    if pend or res["nuevos"] or not os.path.exists(dest):
        io.open(dest, "w", encoding="utf-8", newline="\n").write(md)
        print("resumen:", dest)
    else:
        print("nada pendiente: el resumen existente no se pisa")
    print(f"EQUIVALENTE {len(res['equiv'])} · convertibles {len(res['convertidos'])} (pendientes {len(pend)}) · "
          f"salteados {len(res['saltados'])} · insumos nuevos {len(res['nuevos'])} · estimados referenciados {len(est)}")
    if a.aplicar:
        if est: sys.exit("Hay insumos ESTIMADOS en las recetas nuevas: no aplico.")
        aplicar(R, res, a.libro)


if __name__ == "__main__":
    main()
