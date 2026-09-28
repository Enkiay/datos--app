"""HORMIGONES DE BRASIL: LA CLASE QUE DICE EL NOMBRE (28-sep-2026).

Al pasar a SINAPI, varios ítems distintos quedaron con la MISMA receta porque la composição trae un solo hormigón:
el pilar «H-21» y el «H-25» usaban los dos C25, el radier «H-21» usaba C30 y las cuatro losas con vigueta eran
idénticas. Oscar (28-sep): «sí» a «empezaría por corregir los pilares y las losas, que es lo que está mal».

Qué hace (sólo Brasil):
 1. CLASE POR NOMBRE. H-21 (210 kg/cm²) = clase C20 de la NBR 8953; H-25 = C25. En cada ítem se cambia SÓLO el insumo
    de hormigón por el de su clase, con la misma cantidad y la misma modalidad de la composição (con o sin bombeo):
        OG004BR radier H-21           C30 c/bombeo (1525)  → C20 c/bombeo (1524)
        OG012BR ábaco H-21            C25 c/bombeo (1527)  → C20 c/bombeo (1524)
        OG015BR pilar H-21            C25 s/bombeo (38408) → C20 s/bombeo (34492; el SINAPI no publica C20 slump 190 sin bombeo)
        OG016BR pilar H-21 con bomba  C25 c/bombeo (1527)  → C20 c/bombeo (1524)
        OG023BR / OG024BR losa H-21   C25 c/bombeo (1527)  → C20 c/bombeo (1524)
    OG017BR (pilar H-25) y OG022BR (losa H-25) ya tenían C25: no cambian de receta.
 2. OG021BR (losa con vigueta, hormigón HECHO EN OBRA: su par boliviano lleva cemento, no premezclado): el usinado
    pasa a la composição 94965 (fck 25 en betoneira) aplanada, por el mismo volumen.
 3. NOMBRES: «H-21» → «C20» y «H-25» → «C25» en los ítems y en los insumos de hormigón (H-21/H-25 es nomenclatura
    boliviana). De paso, dos insumos dicen lo que su precio SINAPI es: `…h_21_m3` está ligado al 1523 (C15
    convencional) y `…h_21_con_bomba_m3` estaba en la categoría «Plomería».
 Quedan IGUALES entre sí OG023BR y OG024BR (en Brasil el usinado con bombeo es uno solo): se proponen para unificar.

Sólo cambian `insumos`, `referencia` y `nombre` de esos ítems, y `nombre`/`categoria` de tres insumos de la lista de
precios (NINGÚN precio). Uso:  python tools/corregir-hormigones-br.py [--aplicar]
"""
import io
import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
F_BR = RAIZ / "catalogo/v1.0/items_BR.json"
F_PR = RAIZ / "precios/v1.0/oficiales_BR.json"
F_MAN = RAIZ / "manifest.json"
V_CAT = "v20260928h-br-hormigones"
V_PRE = "v20260928g-br-sinapi-202608"

C20B = "br_hormigon_premezclado_h_21_con_bomba_m3"   # SINAPI 1524
C25B = "br_hormigon_premezclado_h_25_m3"             # SINAPI 1527
CAMBIOS = {   # ítem → (insumo que sale, insumo que entra, códigos SINAPI para la referencia)
    "OG004BR": ("br_sinapi_icd_1525", C20B, "1525→1524"),
    "OG012BR": (C25B, C20B, "1527→1524"),
    "OG015BR": ("br_sinapi_icd_38408", "br_sinapi_icd_34492", "38408→34492"),
    "OG016BR": (C25B, C20B, "1527→1524"),
    "OG023BR": (C25B, C20B, "1527→1524"),
    "OG024BR": (C25B, C20B, "1527→1524"),
}
# 94965 (concreto fck 25 en betoneira 400 L), aplanada, por m³: (código SINAPI, hoja) → coeficiente.
EN_OBRA = {("88831", "CCD"): 0.7103, ("88830", "CCD"): 0.7534, ("88377", "CCD"): 1.4637, ("88316", "CCD"): 2.3117,
           ("4721", "ICD"): 0.5934, ("1379", "ICD"): 362.658, ("370", "ICD"): 0.7229}
NOMBRES_INSUMO = {
    "br_hormigon_premezclado_h_21_m3": ("Concreto Usinado C15 Convencional (Não Bombeável)", None),
    C20B: ("Concreto Usinado C20 Bombeado", "Cemento y Cal"),
    C25B: ("Concreto Usinado C25 Bombeado", None),
}
CLASE = {"21": "C20", "25": "C25"}


def leer(p):
    raw = io.open(p, encoding="utf-8", newline="").read()
    return raw, json.loads(raw)


def escribir(p, raw_antes, doc):
    txt = json.dumps(doc, ensure_ascii=False, indent=2) + "\n"
    if "\r\n" in raw_antes:
        txt = txt.replace("\n", "\r\n")
    io.open(p, "w", encoding="utf-8", newline="").write(txt)


def redondo(v):
    r = float(f"{v:.6g}")
    return int(r) if r == int(r) else r


def main(aplicar):
    raw_i, cat = leer(F_BR)
    raw_p, pre = leer(F_PR)
    sp = {x["idCanonico"]: x for x in pre["ciudades"][0]["precios"]}
    # código SINAPI → insumo BR, leyendo la nota de la lista de precios («código 1524 (M3)»).
    por_codigo = {}
    for x in pre["ciudades"][0]["precios"]:
        m = re.search(r"código (\d+) \(", x.get("nota") or "")
        if m and "SINAPI" in x["nota"]:
            hoja = "CCD" if x["tipoInsumo"] != "MATERIAL" else "ICD"
            por_codigo.setdefault((m.group(1), hoja), []).append(x["idCanonico"])
    items = {i["codigo"]: i for i in cat["items"]}
    usados = {l["idCanonico"] for i in cat["items"] for l in i["insumos"]}

    def linea(idc, rend):
        x = sp[idc]
        assert "SINAPI" in x["nota"] and x["precio"] > 0, idc
        return {"nombre": x["nombre"], "unidad": x["unidad"], "tipoInsumo": x["tipoInsumo"], "categoria": x["categoria"],
                "rendimiento": redondo(rend), "precio": 0, "tipoCalculo": "DIRECTO", "baseCalculo": "",
                "idCanonico": idc, "codigo": x["codigo"]}

    def costo(i):
        return sum(l["rendimiento"] * sp[l["idCanonico"]]["precio"] for l in i["insumos"])

    informe = []
    # 3a. nombres de los insumos (lista de precios, todas las ciudades, y líneas de los ítems).
    for c in pre["ciudades"]:
        for x in c["precios"]:
            if x["idCanonico"] in NOMBRES_INSUMO:
                n, k = NOMBRES_INSUMO[x["idCanonico"]]
                x["nombre"] = n
                if k:
                    x["categoria"] = k
    sp = {x["idCanonico"]: x for x in pre["ciudades"][0]["precios"]}
    for i in cat["items"]:
        for l in i["insumos"]:
            if l["idCanonico"] in NOMBRES_INSUMO:
                l["nombre"], l["categoria"] = sp[l["idCanonico"]]["nombre"], sp[l["idCanonico"]]["categoria"]
    # 1. clase por nombre.
    for cod, (sale, entra, ref) in CAMBIOS.items():
        i = items[cod]
        antes = costo(i)
        ls = [l for l in i["insumos"] if l["idCanonico"] == sale]
        if not ls:
            if any(l["idCanonico"] == entra for l in i["insumos"]):
                continue                                   # ya corregido
            sys.exit(f"{cod}: no tiene {sale}. Paro.")
        assert len(ls) == 1 and not any(l["idCanonico"] == entra for l in i["insumos"]), cod
        k = i["insumos"].index(ls[0])
        i["insumos"][k] = linea(entra, ls[0]["rendimiento"])
        r = i.get("referencia", "")
        base = re.sub(r"^adaptado de ", "", r)
        primero, resto = (base.split(" + ", 1) + [""])[:2] if " + " in base else (base.rsplit(" · ", 1)[0], "")
        if " + " in base:
            nueva = f"adaptado de {primero} ({ref}) + {resto}"
        else:
            nueva = f"adaptado de {primero} ({ref}) · {base.rsplit(' · ', 1)[1]}"
        i["referencia"] = nueva
        informe.append((cod, i["nombre"], antes, costo(i), nueva))
    # 2. OG021BR: hormigón hecho en obra.
    i = items["OG021BR"]
    ls = [l for l in i["insumos"] if l["idCanonico"] == C25B]
    if ls:
        antes = costo(i)
        vol = ls[0]["rendimiento"]
        i["insumos"].remove(ls[0])
        for (codigo, hoja), coef in EN_OBRA.items():
            ids = por_codigo.get((codigo, hoja)) or sys.exit(f"sin insumo BR para SINAPI {codigo} ({hoja}). Paro.")
            idc = next((x for x in ids if any(l["idCanonico"] == x for l in i["insumos"])), None) \
                or next((x for x in ids if x in usados), ids[0])
            ya = next((l for l in i["insumos"] if l["idCanonico"] == idc), None)
            if ya:
                ya["rendimiento"] = redondo(ya["rendimiento"] + coef * vol)
            else:
                i["insumos"].append(linea(idc, coef * vol))
        i["referencia"] = "adaptado de SINAPI 106058 (1527→94965) · 08/2026"
        informe.append(("OG021BR", i["nombre"], antes, costo(i), i["referencia"]))
    # 3b. nombres de los ítems.
    renombrados = []
    for i in cat["items"]:
        n = re.sub(r"\bH-(21|25)\b", lambda m: CLASE[m.group(1)], i["nombre"])
        if n != i["nombre"]:
            renombrados.append((i["codigo"], i["nombre"], n))
            i["nombre"] = n
    otros = [(i["codigo"], i["nombre"]) for i in cat["items"] if re.search(r"\bH-\d\d\b", i["nombre"])]

    print("RECETAS (costo directo São Paulo, R$):")
    for cod, nom, a, d, ref in informe:
        print(f"  {cod} {nom[:52]:52} {a:>9.2f} → {d:>9.2f}   {ref}")
    print("\nNOMBRES DE ÍTEMS:")
    for cod, a, d in renombrados:
        print(f"  {cod}: {a}  →  {d}")
    if otros:
        print("  (quedan con otra «H-»:", otros, ")")
    print("\nNOMBRES DE INSUMOS:", {k: v[0] for k, v in NOMBRES_INSUMO.items()})
    if not informe and not renombrados:
        print("\nNada que cambiar.")
        return
    if not aplicar:
        print("\n(Simulación: no se escribió nada.)")
        return
    cat["version"] = V_CAT
    pre["version"] = V_PRE
    escribir(F_BR, raw_i, cat)
    escribir(F_PR, raw_p, pre)
    raw_m, man = leer(F_MAN)
    man["resources"]["catalogo_BR"]["version"] = V_CAT
    man["resources"]["precios_BR"]["version"] = V_PRE
    escribir(F_MAN, raw_m, man)
    print("\nEscrito:", V_CAT, "·", V_PRE)


if __name__ == "__main__":
    main("--aplicar" in sys.argv)
