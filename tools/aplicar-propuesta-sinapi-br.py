"""
APLICA LA PROPUESTA DE CRUCE ESTIMADOS ↔ SINAPI DE BRASIL (28-sep-2026).

Uso:
  python tools/aplicar-propuesta-sinapi-br.py [--clase SEGURO] [--propuesta precios/fuentes/propuesta_sinapi_BR_20260928.csv]
                                              [--libro <SINAPI_Referencia_AAAA_MM.xlsx>] [--aplicar]

Sin --aplicar (lo normal): NO escribe nada. Muestra qué filas de la propuesta entrarían a
`precios/fuentes/mapa_sinapi_BR.csv` y cuánto cambiaría el precio de São Paulo de cada insumo.

Con --aplicar:
  1. comprueba que el libro (--libro, obligatorio) tenga el sha256 registrado en `precios/fuentes/sinapi_BR.json`
     (si es otro libro, avisa y para: primero hay que bajar el mes nuevo a propósito);
  2. agrega al final de `mapa_sinapi_BR.csv` las filas de la clase pedida (sólo accion = MAPEAR) que no estén ya;
  3. corre `tools/precios-sinapi-br.py <libro>`, que pone el precio SINAPI por estado en `oficiales_BR.json`
     y sube la versión de precios_BR del manifiesto.
No hace commit ni publica. Las acciones SUSTITUIR / QUITAR tocan recetas (`items_BR.json`) y NO las hace este script.

El libro del SINAPI nunca va al repo: guardarlo fuera (p. ej. %LOCALAPPDATA%\\Temp\\sinapi\\).
"""
import argparse, csv, hashlib, io, json, os, subprocess, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAPA = os.path.join(RAIZ, "precios", "fuentes", "mapa_sinapi_BR.csv")
FUENTE = os.path.join(RAIZ, "precios", "fuentes", "sinapi_BR.json")
PROP = os.path.join(RAIZ, "precios", "fuentes", "propuesta_sinapi_BR_20260928.csv")
CAMPOS = ["idCanonico", "codigoSinapi", "hoja", "factor", "unidadArqon", "unidadSinapi", "descripcionSinapi"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--clase", default="SEGURO", help="SEGURO (por defecto). Sólo se mapean filas con accion = MAPEAR.")
    ap.add_argument("--propuesta", default=PROP)
    ap.add_argument("--libro", help="SINAPI_Referencia_AAAA_MM.xlsx (obligatorio con --aplicar)")
    ap.add_argument("--aplicar", action="store_true", help="escribe el mapa y corre precios-sinapi-br.py")
    a = ap.parse_args()

    prop = list(csv.DictReader(open(a.propuesta, encoding="utf-8")))
    ya = {r["idCanonico"] for r in csv.DictReader(open(MAPA, encoding="utf-8"))}
    sel = [r for r in prop if r["clase"] == a.clase and r["accion"] == "MAPEAR"]
    nuevas = [r for r in sel if r["idCanonico"] not in ya]
    repetidas = len(sel) - len(nuevas)
    print(f"Propuesta: {len(prop)} filas · clase {a.clase} con accion MAPEAR: {len(sel)} · ya en el mapa: {repetidas} · nuevas: {len(nuevas)}")
    for r in nuevas:
        est, sin = r["precioEstimadoSP"], r["precioSinapiSP"]
        print(f"  + {r['idCanonico']:<60} SINAPI {r['codigoSinapi']:>6} ×{r['factor']:<9} SP {est:>9} → {sin:>10}  (ratio {r['ratio']})")
    if not a.aplicar:
        print("\n(Sin --aplicar: no se escribió nada.)")
        return

    if not a.libro or not os.path.isfile(a.libro):
        sys.exit("Falta --libro <SINAPI_Referencia_AAAA_MM.xlsx> (el mismo registrado en precios/fuentes/sinapi_BR.json).")
    sha = hashlib.sha256(open(a.libro, "rb").read()).hexdigest()
    reg = json.load(open(FUENTE, encoding="utf-8"))
    if sha != reg.get("sha256"):
        sys.exit(f"El libro no es el registrado ({reg.get('archivo')}, {reg.get('mes')}): sha256 {sha[:12]}… ≠ {reg.get('sha256', '')[:12]}…. "
                 "Si es un mes nuevo, revisar primero y correr tools/precios-sinapi-br.py a mano.")
    if nuevas:
        raw = open(MAPA, encoding="utf-8", newline="").read()
        with open(MAPA, "a", encoding="utf-8", newline="") as f:
            if raw and not raw.endswith("\n"):
                f.write("\n")
            w = csv.DictWriter(f, fieldnames=CAMPOS, lineterminator="\n", extrasaction="ignore")
            for r in nuevas:
                w.writerow({"idCanonico": r["idCanonico"], "codigoSinapi": r["codigoSinapi"], "hoja": r["hoja"] or "ICD",
                            "factor": r["factor"], "unidadArqon": r["unidadArqon"], "unidadSinapi": r["unidadSinapi"],
                            "descripcionSinapi": r["descripcionSinapi"][:120]})
        print(f"mapa_sinapi_BR.csv: +{len(nuevas)} filas")
    subprocess.run([sys.executable, os.path.join(RAIZ, "tools", "precios-sinapi-br.py"), a.libro], check=True)


if __name__ == "__main__":
    main()
