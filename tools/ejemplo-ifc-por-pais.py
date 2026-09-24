"""EL IFC DE EJEMPLO, ADAPTADO A CADA PAÍS (Oscar, 24-sep-2026: «el archivo de ejemplo IFC de Bolivia tiene
ítems con códigos para Bolivia, ¿se puede modificar para que cada país lo tenga adaptado con sus ítems
equivalentes?»).

El modelo (recursos/ejemplo1.ifc, Vectorworks) trae el código del ítem en los nombres/clases: 'UH009',
'UH009 Muro de ladrillo 6H'… El programa asigna por ese código embebido, así que en otro país el modelo
llegaba sin ningún ítem. Acá se reescribe cada texto con el código —y el nombre— del ítem equivalente:

  · países del generador (EC, CO, CL, AR, PY, BR, MX): el MISMO ítem con el sufijo del país (UH009 → UH009EC);
  · Perú y España: la tabla EQUIV, elegida a mano entre los ítems publicados.

Sale recursos/ejemplo1_XX.ifc y recursos/index_XX.json (el genérico con la URL del ejemplo del país): el
programa busca primero index_XX.json. Si un código no está en el catálogo del país, NO se escribe nada.
"""
import io, json, os, re, sys, copy

DATOS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REC = os.path.join(DATOS, "recursos")
BASE = "https://raw.githubusercontent.com/Enkiay/datos--app/main/recursos/"
CODIGOS = ["AC018", "UA001", "UH009", "UH007", "CA001", "UH006", "UA003", "OG021", "AC019", "AC001",
           "CA002", "UH004", "CR010"]   # estos tres vienen en minúsculas en el modelo
DERIVADOS = ["EC", "CO", "CL", "AR", "PY", "BR", "MX"]
# Países cuyo ejemplo ya lo armó Oscar con el Traductor IFC (24-sep-2026: «sube el de Perú para que aparezca en
# Perú, y el de Bolivia sólo en Bolivia»): este script NO los regenera.
A_MANO = {"PE"}
NOMBRE = {"EC": "Ecuador", "CO": "Colombia", "CL": "Chile", "AR": "Argentina", "PY": "Paraguay", "BR": "Brasil",
          "MX": "México", "PE": "Perú", "ES": "España"}
# OJO: index_XX.json es una COPIA del genérico. Si cambia recursos/index.json, volver a correr este script.
EQUIV = {
    "PE": {"AC018": "AC0224", "UA001": "AC0001", "UH009": "MP0001", "UH007": "OG0002", "CA001": "CR0020",
           "UH006": "OG0001", "UA003": "AC0021", "OG021": "OG0056", "AC019": "AC0003", "AC001": "AC0015",
           "CA002": "CR0044", "UH004": "OG0015", "CR010": "CR0053"},
    "ES": {"AC018": "10CEE00080", "UA001": "10CEE00003", "UH009": "06BHC80316", "UH007": "05HHP00003",
           "CA001": "11MPB00151", "UH006": "03HAZ00002", "UA003": "10SCS00003", "OG021": "05FUW80050",
           "AC019": "10SSS00001", "AC001": "10TMT00002",
           "CA002": "11LVA00126", "UH004": "03HMW00101", "CR010": "12NTI80110"},
}


def items(pais):
    d = json.load(io.open(os.path.join(DATOS, "catalogo", "v1.0", f"items_{pais}.json"), encoding="utf-8"))
    lista = d if isinstance(d, list) else next(v for v in d.values() if isinstance(v, list))
    return {x["codigo"].upper(): x for x in lista}


def ifc_texto(s):
    """Texto → cadena STEP: apóstrofo doblado, barra invertida doblada, lo no-ASCII como \\X2\\hhhh\\X0\\."""
    out = []
    for ch in s:
        if ch == "'": out.append("''")
        elif ch == chr(92): out.append(chr(92) * 2)
        elif ord(ch) < 128: out.append(ch)
        else: out.append(chr(92) + "X2" + chr(92) + f"{ord(ch):04X}" + chr(92) + "X0" + chr(92))
    return "".join(out)


def adaptar(texto, cambio):
    """cambio: código BO → (código país, nombre país). 'COD' queda 'NUEVO'; 'COD <nombre>' queda 'NUEVO <nombre país>'."""
    alt = "|".join(sorted(cambio, key=len, reverse=True))
    # el separador puede ser un espacio o un tabulador codificado (\X\09)
    sep = re.escape(chr(92) + "X" + chr(92) + "09")
    rx = re.compile(r"'(" + alt + r")((?: |" + sep + r")[^']*)?'", re.IGNORECASE)
    cuenta = {}
    def rep(m):
        cod = m.group(1).upper(); nuevo, nombre = cambio[cod]
        cuenta[cod] = cuenta.get(cod, 0) + 1
        return f"'{nuevo}'" if not m.group(2) else f"'{nuevo} {ifc_texto(nombre)}'"
    return rx.sub(rep, texto), cuenta


def main():
    fuente = io.open(os.path.join(REC, "ejemplo1.ifc"), encoding="latin-1", newline="").read()
    indice = json.load(io.open(os.path.join(REC, "index.json"), encoding="utf-8"))
    _, base_cuenta = adaptar(fuente, {c: (c, "") for c in CODIGOS})
    for pais in DERIVADOS + list(EQUIV):
        if pais in A_MANO:
            print(f"{pais}: su ejemplo lo armó Oscar a mano (recursos/ejemplo1_{pais}.ifc): no se toca"); continue
        cat = items(pais)
        eq = EQUIV.get(pais) or {c: f"{c}{pais}" for c in CODIGOS}
        faltan = [f"{c}→{n}" for c, n in eq.items() if n.upper() not in cat]
        if faltan:
            print(f"{pais}: NO se escribe, faltan en el catálogo: {', '.join(faltan)}"); continue
        nuevo, cuenta = adaptar(fuente, {c: (n, cat[n.upper()]["nombre"]) for c, n in eq.items()})
        if cuenta != base_cuenta:
            print(f"{pais}: NO se escribe, reemplazos distintos del original: {cuenta} vs {base_cuenta}"); continue
        archivo = f"ejemplo1_{pais}.ifc"
        io.open(os.path.join(REC, archivo), "w", encoding="latin-1", newline="").write(nuevo)
        idx = copy.deepcopy(indice)
        for r in idx["recursos"]:
            if r.get("url", "").endswith("/ejemplo1.ifc"):
                r["url"] = BASE + archivo
                r["descripcion"] = (r.get("descripcion", "").strip() +
                                    f" — con los ítems de {NOMBRE[pais]} ya asignados por código.").strip(" —")
        json.dump(idx, io.open(os.path.join(REC, f"index_{pais}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"{pais}: {archivo} ({sum(cuenta.values())} textos) + index_{pais}.json")


if __name__ == "__main__":
    sys.exit(main())
