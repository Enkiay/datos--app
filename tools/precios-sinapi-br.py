"""
PRECIOS DE BRASIL DESDE EL SINAPI, POR ESTADO (26-sep-2026).

Uso:  python tools/precios-sinapi-br.py <SINAPI_Referencia_AAAA_MM.xlsx> [--sembrar <libro del mes que originó los precios>]

El SINAPI (Caixa/IBGE) publica cada mes un solo libro nacional con el precio de cada insumo y composición
en las 27 capitales. Este script toma de ahí el precio de cada insumo de ArqOn que tiene su código SINAPI
en `precios/fuentes/mapa_sinapi_BR.csv` y lo escribe en `precios/v1.0/oficiales_BR.json`, ciudad por
ciudad, con la capital de su estado. Lo que no está en el mapa no se toca.

  · REGIME: COM desoneração (hojas ICD / CCD), el que eligió la caja brasileña.
  · FACTOR: el insumo de ArqOn puede venir en otra unidad que el del SINAPI (madera en p2 contra m³,
    teja por pieza contra el millar): precio ArqOn = precio SINAPI × factor.
  · UF SIN PRECIO: el SINAPI a veces deja la celda vacía. Entonces va el de São Paulo y la nota lo dice.
  · FUENTE: el libro se baja de la Caixa (caixa.gov.br/Downloads/sinapi-relatorios-mensais/…); desde
    fuera de Brasil la Caixa no responde y se usa una copia del libro SIN CAMBIOS (se registra su sha256
    en `precios/fuentes/sinapi_BR.json`). La fuente citada es siempre SINAPI (Caixa/IBGE), mes y código.

`--sembrar`: arma el mapa desde las notas actuales («SINAPI NNNN - …») — sólo la primera vez.
"""
import csv, hashlib, io, json, os, re, sys
import openpyxl

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OFICIALES = os.path.join(RAIZ, "precios", "v1.0", "oficiales_BR.json")
MAPA = os.path.join(RAIZ, "precios", "fuentes", "mapa_sinapi_BR.csv")
FUENTE = os.path.join(RAIZ, "precios", "fuentes", "sinapi_BR.json")
CIUDAD_UF = {
    "São Paulo": "SP", "Rio de Janeiro": "RJ", "Belo Horizonte": "MG", "Brasília": "DF", "Curitiba": "PR",
    "Porto Alegre": "RS", "Salvador": "BA", "Recife": "PE", "Fortaleza": "CE", "Manaus": "AM",
}


def leer_libro(xlsx, hojas=("ICD", "CCD")):
    """{hoja: {codigo: {"d": desc, "u": unidad, "p": {UF: precio}}}} y el mes («08/2026»)."""
    wb = openpyxl.load_workbook(xlsx, read_only=True, data_only=False)
    out, mes = {}, None
    for h in hojas:
        filas = wb[h].iter_rows(values_only=True)
        cab = [next(filas) for _ in range(10)]
        if mes is None:
            for r in cab[:6]:
                for c in r:
                    m = re.search(r"\b(\d{2}/\d{4})\b", str(c or ""))
                    if m: mes = m.group(1); break
                if mes: break
        fila_uf = cab[9] if h.startswith("I") else cab[8]
        ufs = {i: str(c).strip() for i, c in enumerate(fila_uf) if re.fullmatch(r"[A-Z]{2}", str(c or "").strip())}
        datos = {}
        for r in filas:
            m = re.search(r"MATCH\((\d{2,7})", str(r[1] or "")) or re.fullmatch(r"\s*(\d{2,7})(\.0)?\s*", str(r[1] or ""))
            if not m: continue
            p = {}
            for i, uf in ufs.items():
                v = r[i] if i < len(r) else None
                try: p[uf] = float(v) if v not in (None, "") else None
                except (TypeError, ValueError): p[uf] = None
            datos[m.group(1)] = {"d": str(r[2] or ""), "u": str(r[3] or ""), "p": {k: v for k, v in p.items() if v}}
        out[h] = datos
    return out, mes


def main():
    xlsx = sys.argv[1]
    libro, mes = leer_libro(xlsx)
    sha = hashlib.sha256(open(xlsx, "rb").read()).hexdigest()
    raw = io.open(OFICIALES, encoding="utf-8", newline="").read()
    crlf, fin = "\r\n" in raw, raw.endswith("\n")
    of = json.loads(raw)
    sp = next(c for c in of["ciudades"] if c["nombre"] == "São Paulo")

    if "--sembrar" in sys.argv:
        # La primera vez: el código sale de la nota; la hoja y el factor, de comparar el precio de hoy de
        # São Paulo con el del mes que lo originó (se pasa ese libro como 2º argumento).
        ref, _ = leer_libro(sys.argv[sys.argv.index("--sembrar") + 1])
        filas = []
        for x in sp["precios"]:
            m = re.search(r"SINAPI (\d{2,7}) - ", x.get("nota", ""))
            if not (x.get("nota", "").startswith("REFERENCIA") and m): continue
            cod = m.group(1)
            for h in ("ICD", "CCD"):
                v = ref[h].get(cod, {}).get("p", {}).get("SP")
                if v:
                    f = x["precio"] / v
                    f = 1.0 if abs(f - 1) < 0.001 else round(f, 6)
                    filas.append({"idCanonico": x["idCanonico"], "codigoSinapi": cod, "hoja": h, "factor": f,
                                  "unidadArqon": x["unidad"], "unidadSinapi": ref[h][cod]["u"], "descripcionSinapi": ref[h][cod]["d"][:120]})
                    break
            else:
                print("SIN PAR:", x["idCanonico"], cod)
        with open(MAPA, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(filas[0].keys()), lineterminator="\n")
            w.writeheader(); w.writerows(filas)
        print("mapa sembrado:", len(filas))

    mapa = list(csv.DictReader(open(MAPA, encoding="utf-8")))
    cambiados, sin_uf = 0, 0
    for c in of["ciudades"]:
        uf = CIUDAD_UF[c["nombre"]]
        por_id = {x["idCanonico"]: x for x in c["precios"]}
        for r in mapa:
            x = por_id.get(r["idCanonico"])
            s = libro[r["hoja"]].get(r["codigoSinapi"])
            if not x or not s: continue
            f = float(r["factor"])
            v, de = s["p"].get(uf), uf
            if not v: v, de = s["p"].get("SP"), "SP"
            if not v: continue
            if de != uf: sin_uf += 1
            unid = f'{s["u"]}' + (f", fator {f:g}" if f != 1 else "")
            nota = (f"REFERENCIA: SINAPI (Caixa/IBGE) ref. {mes}, {uf}, COM desoneração, código {r['codigoSinapi']} "
                    f"({unid}) - {s['d'][:90]}.")
            if de != uf: nota += f" Sem preço em {uf} no SINAPI {mes}: preço de SP."
            nuevo = round(v * f, 4 if f != 1 else 2)
            if x.get("precio") != nuevo or x.get("nota") != nota: cambiados += 1
            x["precio"], x["nota"] = nuevo, nota
    import datetime
    of["version"] = datetime.date.today().strftime("v%Y%m%d") + f"-br-sinapi-{mes[3:]}{mes[:2]}"
    # El manifiesto: la app baja los precios de nuevo cuando cambia esta versión.
    man = os.path.join(RAIZ, "manifest.json")
    mraw = io.open(man, encoding="utf-8", newline="").read()
    mraw2 = re.sub(r'("precios_BR"\s*:\s*\{[^}]*?"version"\s*:\s*")[^"]*(")', lambda m: m.group(1) + of["version"] + m.group(2), mraw, count=1)
    assert mraw2 != mraw, "no encontré precios_BR en el manifiesto"
    io.open(man, "w", encoding="utf-8", newline="").write(mraw2)
    t = json.dumps(of, ensure_ascii=False, indent=2) + ("\n" if fin else "")
    io.open(OFICIALES, "w", encoding="utf-8", newline="").write(t.replace("\n", "\r\n") if crlf else t)
    json.dump({"fuente": "SINAPI (Caixa/IBGE) — SINAPI_Referência nacional", "mes": mes, "regime": "COM desoneração (ICD/CCD)",
               "archivo": os.path.basename(xlsx), "sha256": sha,
               "caixa": "https://www.caixa.gov.br/Downloads/sinapi-relatorios-mensais/",
               "nota": "Desde fuera de Brasil la Caixa no responde (302 en bucle); se usa una copia del libro sin cambios y se registra su sha256."},
              io.open(FUENTE, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"mes {mes} · sha256 {sha[:12]}… · {len(mapa)} insumos mapeados · {cambiados} precios cambiados · {sin_uf} sin precio en su UF (van con SP) · versión {of['version']}")


if __name__ == "__main__":
    main()
