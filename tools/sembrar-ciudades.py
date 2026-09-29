#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""UNA CIUDAD POR DEPARTAMENTO, SEMBRADA CON EL PRECIO DE LA CIUDAD DE REFERENCIA (29-sep-2026).

Oscar: «completa todas las ciudades posibles con semillas» · «que se use un precio como el que
hicimos para Bolivia, ya que no teníamos datos de precios de otros departamentos».

Bolivia publica una ciudad por departamento, Perú sus 24 más el Callao y Chile una por región.
Argentina, Paraguay, Brasil, Colombia, México y Ecuador publicaban sólo las principales. Acá se
completan: la CAPITAL de cada departamento, estado o provincia que todavía no tenía ninguna ciudad.
España queda con Madrid sola (precio único, decisión de Oscar del 29-ago-2026).

QUÉ PRECIO LLEVA UNA CIUDAD NUEVA. El de la ciudad de referencia del país, fila por fila, y cada
fila lo DICE en su nota («COPIADO de Bogotá (referencial, sin relevar en Tunja)»). No se inventa
ningún número. Es lo que ya hacen las ciudades publicadas que no tienen relevamiento propio.

POR QUÉ NO SE REGENERA EL PAÍS. `derivar-desde-bolivia.mjs` sólo reproduce hoy lo publicado de
Ecuador: los demás países tienen correcciones posteriores (en Brasil, todo el trabajo con el SINAPI)
que el generador borraría. Este script trabaja SOBRE LO PUBLICADO: arma cada ciudad nueva desde la
de referencia con la misma regla de copia del generador. Antes de escribir se prueba a sí mismo: con
esa regla tiene que poder rearmar, idéntica, cada fila copiada que ya está publicada en las demás
ciudades del país. Si una sola no sale igual, no escribe.

BRASIL ES DISTINTO: el SINAPI publica cada insumo en las 27 capitales. Acá la ciudad nueva sólo se
abre; después hay que correr `precios-sinapi-br.py`, que le pone a cada una el precio de SU estado.

Las ciudades nuevas se anotan también en las FUENTES del generador (`relevados_XX.json`,
`propios_EC.json` y la tabla CONFIG de Brasil y México), para que una regeneración futura no las pierda.

Uso:
    python tools/sembrar-ciudades.py              muestra qué haría, sin escribir
    python tools/sembrar-ciudades.py --aplicar    escribe los archivos y el manifiesto
    python tools/sembrar-ciudades.py --aplicar CO MX     sólo esos países
"""
from __future__ import annotations

import copy
import io
import json
import os
import re
import sys

BASE = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
VERSION = "v20260929-una-ciudad-por-departamento"

# (ciudad, departamento / estado / provincia que cubre). El nombre va ESCRITO COMO SE PUBLICA: con
# sigla entre paréntesis en los países que ya la usan (Paraguay, México) y sin ella en los demás.
CIUDADES: dict[str, list[tuple[str, str]]] = {
    "AR": [
        ("San Fernando del Valle de Catamarca", "Catamarca"), ("Rawson", "Chubut"), ("Formosa", "Formosa"),
        ("San Salvador de Jujuy", "Jujuy"), ("Santa Rosa", "La Pampa"), ("La Rioja", "La Rioja"),
        ("Viedma", "Río Negro"), ("San Luis", "San Luis"), ("Río Gallegos", "Santa Cruz"),
        ("Santiago del Estero", "Santiago del Estero"), ("Ushuaia", "Tierra del Fuego"),
    ],
    "PY": [
        ("San Pedro de Ycuamandiyú (SPY)", "San Pedro"), ("Caacupé (CAA)", "Cordillera"),
        ("Caazapá (CZP)", "Caazapá"), ("San Juan Bautista (SJB)", "Misiones"), ("Paraguarí (PAR)", "Paraguarí"),
        ("Pilar (PIL)", "Ñeembucú"), ("Salto del Guairá (SDG)", "Canindeyú"), ("Villa Hayes (VHA)", "Presidente Hayes"),
        ("Filadelfia (FIL)", "Boquerón"), ("Fuerte Olimpo (FOL)", "Alto Paraguay"),
    ],
    "BR": [
        ("Rio Branco", "Acre"), ("Maceió", "Alagoas"), ("Macapá", "Amapá"), ("Vitória", "Espírito Santo"),
        ("Goiânia", "Goiás"), ("São Luís", "Maranhão"), ("Cuiabá", "Mato Grosso"),
        ("Campo Grande", "Mato Grosso do Sul"), ("Belém", "Pará"), ("João Pessoa", "Paraíba"),
        ("Teresina", "Piauí"), ("Natal", "Rio Grande do Norte"), ("Porto Velho", "Rondônia"),
        ("Boa Vista", "Roraima"), ("Florianópolis", "Santa Catarina"), ("Aracaju", "Sergipe"), ("Palmas", "Tocantins"),
    ],
    "CO": [
        ("Leticia", "Amazonas"), ("Arauca", "Arauca"), ("Tunja", "Boyacá"), ("Manizales", "Caldas"),
        ("Florencia", "Caquetá"), ("Yopal", "Casanare"), ("Popayán", "Cauca"), ("Valledupar", "Cesar"),
        ("Quibdó", "Chocó"), ("Montería", "Córdoba"), ("Inírida", "Guainía"),
        ("San José del Guaviare", "Guaviare"), ("Neiva", "Huila"), ("Riohacha", "La Guajira"),
        ("Santa Marta", "Magdalena"), ("Villavicencio", "Meta"), ("Pasto", "Nariño"), ("Mocoa", "Putumayo"),
        ("Armenia", "Quindío"), ("San Andrés", "San Andrés y Providencia"), ("Sincelejo", "Sucre"),
        ("Ibagué", "Tolima"), ("Mitú", "Vaupés"), ("Puerto Carreño", "Vichada"),
    ],
    "MX": [
        ("Aguascalientes (AGU)", "Aguascalientes"), ("La Paz (LAP)", "Baja California Sur"),
        ("Campeche (CPE)", "Campeche"), ("Chihuahua (CUU)", "Chihuahua"), ("Saltillo (SLW)", "Coahuila"),
        ("Colima (CLQ)", "Colima"), ("Durango (DGO)", "Durango"), ("Guanajuato (GTO)", "Guanajuato"),
        ("Chilpancingo (CHP)", "Guerrero"), ("Pachuca (PAC)", "Hidalgo"), ("Toluca (TLC)", "Estado de México"),
        ("Morelia (MLM)", "Michoacán"), ("Cuernavaca (CVJ)", "Morelos"), ("Tepic (TPQ)", "Nayarit"),
        ("Oaxaca (OAX)", "Oaxaca"), ("Chetumal (CTM)", "Quintana Roo"), ("San Luis Potosí (SLP)", "San Luis Potosí"),
        ("Culiacán (CUL)", "Sinaloa"), ("Hermosillo (HMO)", "Sonora"), ("Villahermosa (VSA)", "Tabasco"),
        ("Ciudad Victoria (CVM)", "Tamaulipas"), ("Tlaxcala (TLX)", "Tlaxcala"), ("Xalapa (XAL)", "Veracruz"),
        ("Zacatecas (ZCL)", "Zacatecas"),
    ],
    "EC": [
        ("Guaranda", "Bolívar"), ("Azogues", "Cañar"), ("Tulcán", "Carchi"), ("Riobamba", "Chimborazo"),
        ("Latacunga", "Cotopaxi"), ("Esmeraldas", "Esmeraldas"), ("Puerto Baquerizo Moreno", "Galápagos"),
        ("Ibarra", "Imbabura"), ("Babahoyo", "Los Ríos"), ("Macas", "Morona Santiago"), ("Tena", "Napo"),
        ("Puerto Francisco de Orellana", "Orellana"), ("Puyo", "Pastaza"), ("Santa Elena", "Santa Elena"),
        ("Santo Domingo", "Santo Domingo de los Tsáchilas"), ("Nueva Loja", "Sucumbíos"), ("Zamora", "Zamora Chinchipe"),
    ],
}


class NoSePuede(Exception):
    """El archivo no tiene la forma esperada: mejor no escribir que escribir algo que no se entiende."""


# Cada archivo se vuelve a escribir COMO ESTABA: los publicados van con sangría de 2 (y varios con
# saltos de Windows); las fuentes relevadas a mano, compactas o con sangría de 1.
ESTILOS = [
    ({"indent": 2}, "\n"),
    ({"separators": (",", ":")}, ""),
    ({"indent": 1}, ""),
]


def texto(datos, forma) -> str:
    estilo, fin, salto = forma
    return (json.dumps(datos, ensure_ascii=False, **estilo) + fin).replace("\n", salto)


def leer(ruta: str) -> tuple[dict, tuple]:
    """(datos, forma de escribirlo). Exige que el archivo se pueda volver a escribir IDÉNTICO: si
    no, el cambio de una ciudad terminaría tocando miles de líneas que nadie pidió tocar."""
    crudo = io.open(os.path.join(BASE, ruta), encoding="utf-8", newline="").read()
    salto = "\r\n" if "\r\n" in crudo else "\n"
    datos = json.loads(crudo)
    for estilo, fin in ESTILOS:
        if texto(datos, (estilo, fin, salto)) == crudo:
            return datos, (estilo, fin, salto)
    raise NoSePuede(f"{ruta}: al reescribirlo sin cambios no queda igual; no se toca")


#: Lo que hay que escribir. Se escribe TODO al final: si un país no pasa su prueba, no se toca ninguno.
PENDIENTES: dict[str, tuple] = {}


def escribir(ruta: str, datos, forma) -> None:
    PENDIENTES[ruta] = (datos, forma)


def volcar() -> None:
    for ruta, (datos, forma) in PENDIENTES.items():
        io.open(os.path.join(BASE, ruta), "w", encoding="utf-8", newline="").write(texto(datos, forma))


def sigla_de(nombre: str) -> str:
    m = re.search(r"\(([^)]+)\)\s*$", nombre)
    return m.group(1) if m else ""


#: Lo que dice el generador de la mano de obra argentina copiada (la escala UOCRA es nacional).
MOTIVO_MO_AR = "escala UOCRA zona A, la misma en todo el país salvo la Patagonia"
#: Un precio ESTIMADO o PENDIENTE no es «de» ninguna ciudad: se repite tal cual, sin decir COPIADO.
SIN_CIUDAD = re.compile(r"^(ESTIMADO|PENDIENTE)")

# LAS TRES FORMAS en que una ciudad publicada repite el precio de la de referencia:
#   GENERADOR  «COPIADO de Quito (referencial, sin relevar en Loja). <nota>» — la del generador.
#   PROPIOS    «COPIADO de Quito hasta relevarse en Loja. <nota>» — los insumos propios de Ecuador.
#   IGUAL      la misma nota, sin más: lo ESTIMADO, y lo que es nacional por definición (en Ecuador
#              el salario de la Contraloría: «mismo valor en todas las ciudades»).
GENERADOR, PROPIOS, IGUAL = "generador", "propios", "igual"


def nota_en(forma: str, fila_ref: dict, ref: str, ciudad: str, pais: str) -> str:
    nota = fila_ref.get("nota") or ""
    if forma == IGUAL:
        return nota
    if forma == PROPIOS:
        return f"COPIADO de {ref} hasta relevarse en {ciudad}. {nota}".strip()
    motivo = MOTIVO_MO_AR if pais == "AR" and fila_ref.get("tipoInsumo") == "MANO_DE_OBRA" else f"referencial, sin relevar en {ciudad}"
    return f"COPIADO de {ref} ({motivo}). {nota}".strip()


def forma_de(fila: dict, fila_ref: dict, ref: str, ciudad: str, pais: str) -> str | None:
    """En qué forma copió esta fila publicada a la de referencia. `None` = no es una copia: es un
    relevamiento propio de la ciudad (otro precio, o una nota que cuenta otra cosa)."""
    if {k: v for k, v in fila.items() if k != "nota"} != {k: v for k, v in fila_ref.items() if k != "nota"}:
        return None
    nota = fila.get("nota") or ""
    for forma in (IGUAL, GENERADOR, PROPIOS):
        if nota == nota_en(forma, fila_ref, ref, ciudad, pais):
            return forma
    return None


def forma_para(fila_ref: dict, publicadas: list[tuple[str, dict]], ref: str, pais: str) -> str:
    """La forma que le toca a este insumo en una ciudad NUEVA.

    Lo estimado va IGUAL. Lo demás va en la forma del generador, salvo que TODAS las ciudades ya
    publicadas lo repitan de otra manera: ahí se sigue a la casa. Tiene que ser unánime — en
    Paraguay hay filas de ANDE que en una ciudad coinciden con Asunción por casualidad, y eso no
    las vuelve nacionales.
    """
    if SIN_CIUDAD.match(fila_ref.get("nota") or ""):
        return IGUAL
    formas = {forma_de(f, fila_ref, ref, c, pais) for c, f in publicadas}
    if len(formas) == 1 and formas <= {IGUAL, PROPIOS}:
        return formas.pop()
    return GENERADOR


def sembrar_lista(datos: dict, pais: str, nuevas: list[str], que: str) -> tuple[list[str], int]:
    """Agrega `nuevas` a `datos["ciudades"]`. Devuelve (las que agregó, filas con las que se probó)."""
    ciudades = datos["ciudades"]
    ref_nombre = (datos.get("origenPrecios") or {}).get("ciudadReferencia") or ciudades[0]["nombre"]
    ref = next((c for c in ciudades if c["nombre"] == ref_nombre), None)
    if ref is None:
        raise NoSePuede(f"{que}: la ciudad de referencia «{ref_nombre}» no está en el archivo")
    orden = [p["idCanonico"] for p in ref["precios"]]
    if len(set(orden)) != len(orden):
        raise NoSePuede(f"{que}: {ref_nombre} tiene un insumo repetido")
    otras = [c for c in ciudades if c is not ref]
    for c in otras:
        if [p["idCanonico"] for p in c["precios"]] != orden:
            raise NoSePuede(f"{que}: «{c['nombre']}» no trae los mismos insumos que {ref_nombre}, en el mismo orden")
    formas = [forma_para(r, [(c["nombre"], c["precios"][i]) for c in otras], ref_nombre, pais)
              for i, r in enumerate(ref["precios"])]
    # LA PRUEBA: la regla tiene que rearmar, idéntica, cada fila copiada que YA está publicada.
    probadas = 0
    for c in otras:
        for i, p in enumerate(c["precios"]):
            r = ref["precios"][i]
            forma = forma_de(p, r, ref_nombre, c["nombre"], pais)
            if forma == IGUAL and formas[i] != IGUAL:
                continue    # relevamiento propio que dio lo mismo que la de referencia: no es copia
            if forma is None:
                # No es una copia reconocible. Si dice COPIADO, es una forma que este script no
                # conoce y no se puede seguir a ciegas; si no, es un relevamiento propio y se deja.
                if (p.get("nota") or "").startswith("COPIADO"):
                    raise NoSePuede(f"{que}: {p['idCanonico']} de «{c['nombre']}» está COPIADO de una forma que no se reconoce")
                continue
            if nota_en(formas[i], r, ref_nombre, c["nombre"], pais) != (p.get("nota") or ""):
                raise NoSePuede(f"{que}: la regla no rearma {p['idCanonico']} de «{c['nombre']}» como está publicada")
            probadas += 1
    if otras and not probadas:
        raise NoSePuede(f"{que}: no hay ni una fila copiada publicada contra la cual probar la regla")
    ya = {c["nombre"] for c in ciudades}
    extra = {k: v for k, v in ref.items() if k not in ("nombre", "precios", "sigla", "nombreCorto")}
    agregadas = []
    for n in nuevas:
        if n in ya:
            continue
        filas = []
        for i, r in enumerate(ref["precios"]):
            f = copy.deepcopy(r)
            if "nota" in f or formas[i] != IGUAL:
                f["nota"] = nota_en(formas[i], r, ref_nombre, n, pais)
            filas.append(f)
        ciudades.append({**copy.deepcopy(extra), "nombre": n, "precios": filas})
        agregadas.append(n)
    return agregadas, probadas


def verificar_nombres(pais: str, existentes: list[str]) -> None:
    nuevas = [n for n, _ in CIUDADES[pais]]
    todas = existentes + [n for n in nuevas if n not in existentes]
    if len(set(todas)) != len(todas):
        raise NoSePuede(f"{pais}: hay un nombre de ciudad repetido")
    con_sigla = [bool(sigla_de(n)) for n in existentes]
    if any(con_sigla) != all(con_sigla):
        raise NoSePuede(f"{pais}: las ciudades publicadas mezclan nombres con y sin sigla")
    for n in nuevas:
        if bool(sigla_de(n)) != all(con_sigla):
            raise NoSePuede(f"{pais}: «{n}» no sigue la forma de las publicadas ({'con' if all(con_sigla) else 'sin'} sigla)")
    siglas = [sigla_de(n) for n in todas if sigla_de(n)]
    repetidas = sorted({s for s in siglas if siglas.count(s) > 1})
    if repetidas:
        raise NoSePuede(f"{pais}: siglas repetidas {repetidas}")
    deptos = [d for _, d in CIUDADES[pais]]
    if len(set(deptos)) != len(deptos):
        raise NoSePuede(f"{pais}: un departamento figura dos veces")


def cuenta_en_texto(s: str, antes: int, despues: int) -> str:
    """«en las 8 ciudades de la caja» y «las otras 7 ciudades COPIAN»: que el texto diga la cuenta nueva."""
    s = re.sub(rf"en las {antes} ciudades de la caja", f"en las {despues} ciudades de la caja", s)
    return re.sub(r"[Ll]as otras (\d+) ciudades COPIAN",
                  lambda m: m.group(0).replace(m.group(1), str(int(m.group(1)) + despues - antes)), s)


def pais_uno(pais: str, aplicar: bool) -> str | None:
    ruta = f"precios/v1.0/oficiales_{pais}.json"
    datos, forma = leer(ruta)
    publicado = copy.deepcopy(datos["ciudades"])
    antes = len(datos["ciudades"])
    verificar_nombres(pais, [c["nombre"] for c in datos["ciudades"]])
    agregadas, probadas = sembrar_lista(datos, pais, [n for n, _ in CIUDADES[pais]], ruta)
    if not agregadas:
        print(f"  {pais}: ya tiene sus {antes} ciudades; no hay nada que sembrar")
        return None
    despues = len(datos["ciudades"])
    # El resumen por ciudad que deja el generador: una ciudad sembrada es toda COPIADA.
    por_ciudad = (datos.get("origenPrecios") or {}).get("porCiudad")
    # Brasil NO: sus ciudades no quedan copiadas, `precios-sinapi-br.py` les pone el precio de su estado.
    if isinstance(por_ciudad, dict) and por_ciudad and pais != "BR":
        pura = next((v for v in por_ciudad.values() if not v.get("REFERENCIA") and not v.get("ESTIMADO_DESDE_REFERENCIA")), None)
        if pura is None:
            raise NoSePuede(f"{pais}: el resumen por ciudad no trae ninguna ciudad toda copiada")
        for n in agregadas:
            por_ciudad[n] = copy.deepcopy(pura)
    for campo in ("nota", "fuente"):
        if isinstance(datos.get(campo), str):
            datos[campo] = cuenta_en_texto(datos[campo], antes, despues)
    datos["version"] = VERSION
    # Lo publicado no se mueve: las ciudades que ya estaban quedan byte a byte como estaban.
    if datos["ciudades"][:antes] != publicado:
        raise NoSePuede(f"{pais}: se movió una ciudad que ya estaba publicada")
    # Y cada ciudad nueva trae los mismos insumos que la de referencia, con el mismo precio.
    base = [(p["idCanonico"], p.get("precio")) for p in datos["ciudades"][0]["precios"]]
    ref_nombre = (datos.get("origenPrecios") or {}).get("ciudadReferencia") or datos["ciudades"][0]["nombre"]
    de_ref = [(p["idCanonico"], p.get("precio")) for c in datos["ciudades"] if c["nombre"] == ref_nombre for p in c["precios"]]
    for c in datos["ciudades"][antes:]:
        if [(p["idCanonico"], p.get("precio")) for p in c["precios"]] != de_ref:
            raise NoSePuede(f"{pais}: «{c['nombre']}» no quedó con los precios de {ref_nombre}")
    filas = len(base)
    print(f"  {pais}: {antes} → {despues} ciudades (+{len(agregadas)}), {filas} insumos cada una · regla probada contra {probadas} filas copiadas ya publicadas")
    escribir(ruta, datos, forma)
    fuentes(pais, [n for n, _ in CIUDADES[pais]])
    return VERSION


def fuentes(pais: str, nuevas: list[str]) -> None:
    """Las listas de las que parte el generador, para que regenerar no pierda las ciudades."""
    rel = f"precios/fuentes/relevados_{pais}.json"
    if os.path.exists(os.path.join(BASE, rel)):
        d, forma = leer(rel)
        ya = {c["nombre"] for c in d["ciudades"]}
        for n in nuevas:
            if n not in ya:
                d["ciudades"].append({"nombre": n, "precios": []})
        escribir(rel, d, forma)
    prop = f"precios/fuentes/propios_{pais}.json"
    if os.path.exists(os.path.join(BASE, prop)):
        d, forma = leer(prop)
        sembrar_lista(d, pais, nuevas, prop)
        escribir(prop, d, forma)


def manifiesto(versiones: dict[str, str]) -> None:
    m, forma = leer("manifest.json")
    for pais, v in versiones.items():
        m["resources"][f"precios_{pais}"]["version"] = v
    escribir("manifest.json", m, forma)


def main(argv: list[str]) -> int:
    aplicar = "--aplicar" in argv
    paises = [a.upper() for a in argv if not a.startswith("--")] or list(CIUDADES)
    print(("ESCRIBIENDO" if aplicar else "SIN ESCRIBIR (agregá --aplicar)") + f" · versión {VERSION}")
    versiones: dict[str, str] = {}
    try:
        for p in paises:
            if p not in CIUDADES:
                raise NoSePuede(f"{p}: no tiene lista de ciudades en este script")
            v = pais_uno(p, aplicar)
            if v:
                versiones[p] = v
        if versiones:
            manifiesto(versiones)
        if aplicar:
            volcar()
    except NoSePuede as e:
        print(f"✗ {e}", file=sys.stderr)
        return 1
    print(f"✓ {sum(len(CIUDADES[p]) for p in versiones)} ciudades nuevas en {len(versiones)} países")
    if "BR" in versiones:
        print("  Brasil: falta correr tools/precios-sinapi-br.py <libro del SINAPI> para el precio de cada estado")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
