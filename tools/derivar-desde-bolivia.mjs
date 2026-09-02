#!/usr/bin/env node
// DERIVAR LA BASE DE UN PAÍS DESDE LA DE BOLIVIA (2-sep-2026, pedido de Oscar: «nuevas y
// limpias, todas basadas en la BD de Bolivia, solo que con precio de cada país»).
//
// Produce, para el país pedido:
//   precios/v1.0/oficiales_XX.json → TODOS los insumos de Bolivia (751) bajo el espacio del
//       país (`xx_<idBoliviano>`), en TODAS las ciudades de la caja. Los que tienen precio
//       relevado lo traen (por ciudad); los demás van en 0 con nota «PENDIENTE» — el usuario
//       los ve como «sin precio» y puede cargarlos a mano. Nunca un número inventado.
//   catalogo/v1.0/items_XX.json → SÓLO los ítems bolivianos cuyos insumos tienen TODOS precio.
//       Es la regla de la casa (`estado-de-las-bases.test.ts`): un ítem con un insumo en cero
//       no da error, da un APU barato. La base CRECE SOLA: relevás precios, regenerás, entran
//       más ítems. Los códigos llevan el sufijo del país (`UA001` → `UA001PY`): el índice de
//       la APK es UNIQUE sobre el código sin país.
//
// Uso:  node tools/derivar-desde-bolivia.mjs PY
import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const BASE = join(dirname(fileURLToPath(import.meta.url)), "..");
const PAIS = (process.argv[2] || "").toUpperCase();
if (!PAIS) { console.error("uso: node tools/derivar-desde-bolivia.mjs <ISO>"); process.exit(2); }
const iso = PAIS.toLowerCase();

// ── LA TABLA DEL PAÍS: qué insumo boliviano ya tiene precio relevado, y con qué id ──────────
// `equivalentes`: id boliviano → id YA publicado del país (conserva el id y el precio por ciudad).
// `familias`: id boliviano → id del país cuyo precio HEREDA (misma familia de producto o mismo
// escalafón). Se declara acá, insumo por insumo, para que la decisión quede escrita.
const CONFIG = {
  PY: {
    version: "v20260902-base-bolivia",
    fuente: "Base boliviana (catálogo ArqOn) + precios de Paraguay: ANDE (arena, cemento y piedra por localidad), Resolución MTESS 670/2026 (escalafón de la construcción) y costeo.com.py ago-2026",
    equivalentes: {
      cemento_portland_kg: "py_mat_cemento", arena_comun_m3: "py_mat_arena_comun", arena_fina_m3: "py_mat_arena_fina",
      grava_comun_m3: "py_mat_grava", grava_clasificada_m3: "py_mat_grava_clasificada", piedra_bruta_m3: "py_mat_piedra_bruta",
      fierro_corrugado_kg: "py_mat_fierro", cal_kg: "py_mat_cal", clavos_kg: "py_mat_clavos", alambre_de_amarre_kg: "py_mat_alambre_amarre",
      mo_albanil: "py_mo_albanil", mo_carpintero: "py_mo_carpintero", mo_encofrador: "py_mo_encofrador",
      mo_armador: "py_mo_armador", mo_especialista: "py_mo_especialista", mo_ayudante: "py_mo_ayudante",
    },
    familias: {
      // Cemento: ANDE publica UN precio de cemento; las variantes bolivianas lo heredan.
      cemento_portland_ip30_kg: "py_mat_cemento", cemento_portland_ip40_kg: "py_mat_cemento", cemento_kg: "py_mat_cemento",
      arena_lavada_m3: "py_mat_arena_comun", grava_lavada_m3: "py_mat_grava", piedra_para_cimiento_m3: "py_mat_piedra_bruta",
      // Escalafón MTESS: todo OFICIAL cobra la hora del oficial; rige en todo el país.
      mo_especialista_calificado: "py_mo_especialista", mo_especialista_plomero: "py_mo_especialista",
      mo_especialista_cerrajero: "py_mo_especialista", mo_especialista_en_tesado_e_inyeccion: "py_mo_especialista",
      mo_tecnico_especialista: "py_mo_especialista", mo_tecnico_especialista_certificado: "py_mo_especialista",
      mo_tecnico_especialista_juntas: "py_mo_especialista", mo_electricista: "py_mo_especialista",
      mo_plomero: "py_mo_especialista", mo_plomero_certificado: "py_mo_especialista", mo_pintor: "py_mo_especialista",
      mo_cerrajero: "py_mo_especialista", mo_carpintero_en_aluminio: "py_mo_carpintero", mo_perforista: "py_mo_especialista",
    },
  },
  CL: {
    version: "v20260902-base-bolivia",
    fuente: "Base boliviana (catálogo ArqOn) + precios de Chile: índices públicos de materiales (factoIA, ObraMaestra, CalculaObra) y un APU chileno real, jun-jul 2026. Relevado en Santiago; las otras 15 ciudades COPIAN Santiago (referencial) hasta relevarse.",
    equivalentes: {
      arena_fina_m3: "cl_mat_arena_fina", arena_comun_m3: "cl_mat_arena_gruesa", cemento_portland_kg: "cl_mat_cemento",
      clavos_kg: "cl_mat_clavos", estuco_kg: "cl_mat_estuco", fierro_corrugado_kg: "cl_mat_fierro",
      madera_de_construccion_p2: "cl_mat_madera", pintura_latex_l: "cl_mat_pintura_latex", calamina_galvanizada_m2: "cl_mat_zinc",
      mo_albanil: "cl_mo_albanil", mo_carpintero: "cl_mo_carpintero", mo_especialista: "cl_mo_especialista", mo_ayudante: "cl_mo_jornalero",
    },
    familias: {
      cemento_portland_ip30_kg: "cl_mat_cemento", cemento_portland_ip40_kg: "cl_mat_cemento", cemento_kg: "cl_mat_cemento",
      arena_lavada_m3: "cl_mat_arena_gruesa",
      pintura_latex_interior_l: "cl_mat_pintura_latex", pintura_latex_exterior_l: "cl_mat_pintura_latex", pintura_latex_satinado_l: "cl_mat_pintura_latex",
      // La «plancha de zinc acanalada» chilena ES la calamina boliviana.
      calamina_ondulada_n_28_m2: "cl_mat_zinc", calamina_ondulada_n_33_m2: "cl_mat_zinc", calamina_plana_n_28_m2: "cl_mat_zinc",
      // En Chile todo MAESTRO cobra la misma hora (3.212): las oficialías bolivianas la heredan.
      mo_encofrador: "cl_mo_especialista", mo_armador: "cl_mo_especialista", mo_especialista_calificado: "cl_mo_especialista",
      mo_especialista_plomero: "cl_mo_especialista", mo_especialista_cerrajero: "cl_mo_especialista",
      mo_especialista_en_tesado_e_inyeccion: "cl_mo_especialista", mo_tecnico_especialista: "cl_mo_especialista",
      mo_tecnico_especialista_certificado: "cl_mo_especialista", mo_tecnico_especialista_juntas: "cl_mo_especialista",
      mo_electricista: "cl_mo_especialista", mo_plomero: "cl_mo_especialista", mo_plomero_certificado: "cl_mo_especialista",
      mo_pintor: "cl_mo_especialista", mo_cerrajero: "cl_mo_especialista", mo_carpintero_en_aluminio: "cl_mo_carpintero",
      mo_perforista: "cl_mo_especialista",
    },
    // LEYES SOCIALES (≈45 % de la M.O.) van DENTRO del APU como línea de porcentaje — la caja
    // chilena lleva cargasSociales = 0 por eso, y la guarda del PC exige que la línea exista.
    lineasExtra: (it) => it.insumos.some((s) => s.tipoInsumo === "MANO_DE_OBRA") ? [{
      nombre: "Leyes sociales (45 % de la M.O.)", unidad: "%", tipoInsumo: "HERRAMIENTA", categoria: "Equipo",
      rendimiento: 45, precio: 0, tipoCalculo: "PORCENTAJE", baseCalculo: "MO", idCanonico: "cl_mo_leyes_sociales", codigo: "",
    }] : [],
  },
  AR: {
    version: "v20260902-base-bolivia",
    fuente: "Base boliviana (catálogo ArqOn) + precios de Argentina: Unidad Central de Contrataciones (UCC), Provincia de Salta — planilla de insumos, julio 2026. Relevado en Salta; las otras 15 ciudades COPIAN Salta (referencial) hasta relevarse.",
    // MANO DE OBRA: la UCC cotiza «Cuadrilla tipo UOCRA» a $10.836/h y un ayudante a $10.030/h —
    // la magnitud de UNA hora-hombre promedio, no de un equipo entero—, con las cargas ADENTRO
    // (costo empresa; por eso la caja argentina lleva cargasSociales = 0 y ninguna línea de %).
    // Las líneas por trabajador de Bolivia heredan esa hora: oficialías y peón → UOCRA;
    // instaladores y técnicos → UGATS. Sin líneas de porcentaje sobre la M.O., a propósito.
    equivalentes: {
      cemento_portland_kg: "ar_li_006", arena_comun_m3: "ar_ar_001", grava_comun_m3: "ar_ar_003",
      cal_kg: "ar_li_004", clavos_kg: "ar_ac_050", fierro_corrugado_kg: "ar_ac_015", yeso_kg: "ar_li_009",
      // Un id argentino sólo puede ser EQUIVALENTE de un id boliviano (reemplaza el id); el resto
      // de las oficialías entran como FAMILIA con id propio (`ar_mo_albanil`) y heredan la hora.
      mo_ayudante: "ar_mo_006", mo_electricista: "ar_mo_007",
    },
    familias: {
      cemento_portland_ip30_kg: "ar_li_006", cemento_portland_ip40_kg: "ar_li_006", cemento_kg: "ar_li_006",
      arena_lavada_m3: "ar_ar_001", grava_lavada_m3: "ar_ar_003",
      eq_volqueta_6_m3: "ar_eq_012",
      mo_albanil: "ar_mo_006",
      mo_armador: "ar_mo_006", mo_encofrador: "ar_mo_006", mo_carpintero: "ar_mo_006", mo_carpintero_en_aluminio: "ar_mo_006",
      mo_especialista: "ar_mo_006", mo_especialista_calificado: "ar_mo_006", mo_especialista_cerrajero: "ar_mo_006",
      mo_especialista_en_tesado_e_inyeccion: "ar_mo_006", mo_pintor: "ar_mo_006", mo_cerrajero: "ar_mo_006", mo_perforista: "ar_mo_006",
      mo_especialista_plomero: "ar_mo_007", mo_plomero: "ar_mo_007", mo_plomero_certificado: "ar_mo_007",
      mo_tecnico_especialista: "ar_mo_007", mo_tecnico_especialista_certificado: "ar_mo_007", mo_tecnico_especialista_juntas: "ar_mo_007",
    },
  },
};
const cfg = CONFIG[PAIS];
if (!cfg) { console.error(`no hay tabla para ${PAIS}: agregala en CONFIG`); process.exit(2); }
// Un id del país sólo puede ser EQUIVALENTE de un id boliviano: dos bolivianos apuntando al
// mismo id lo duplicarían en oficiales. El segundo tiene que ir como FAMILIA (id propio).
{
  const vistos = new Map();
  for (const [bo, ext] of Object.entries(cfg.equivalentes)) {
    if (vistos.has(ext)) { console.error(`CONFIG.${PAIS}.equivalentes: «${ext}» ya es equivalente de «${vistos.get(ext)}»; pasá «${bo}» a familias`); process.exit(2); }
    vistos.set(ext, bo);
  }
}

const leer = (p) => JSON.parse(readFileSync(join(BASE, p), "utf8"));
const itemsBO = leer("catalogo/v1.0/items.json");
const ofiBO = leer("precios/v1.0/oficiales.json");
const ofiPaisViejo = existsSync(join(BASE, `precios/v1.0/oficiales_${PAIS}.json`)) ? leer(`precios/v1.0/oficiales_${PAIS}.json`) : null;
if (!ofiPaisViejo?.ciudades?.length) { console.error(`falta oficiales_${PAIS}.json con las ciudades y los precios relevados`); process.exit(2); }

// El insumo maestro: la primera ciudad boliviana trae los 751 con nombre/unidad/tipo/categoría.
const maestro = ofiBO.ciudades[0].precios;
const idPais = (idBo) => cfg.equivalentes[idBo] ?? `${iso}_${idBo}`;
const codigoPais = (idBo, codBo) => cfg.equivalentes[idBo] ? cfg.equivalentes[idBo].toUpperCase() : `${PAIS}_${codBo}`;

// Precio relevado del país para un id boliviano, en una ciudad dada (null si no hay).
function precioEn(ciudadPais, idBo) {
  const ref = cfg.equivalentes[idBo] ?? cfg.familias[idBo];
  if (!ref) return null;
  const p = ciudadPais.precios.find((x) => x.idCanonico === ref);
  return p && p.precio > 0 ? p : null;
}

// ── oficiales_XX: las ciudades del país, con los 751 insumos cada una ──────────────────────
// TODAS las ciudades de la caja salen SERVIDAS (Oscar, 2-sep-2026: «habilita todas las
// ciudades, con precios copiados»): una ciudad sin relevamiento propio copia los precios de la
// ciudad de REFERENCIA (la primera que tenga precios), y cada precio copiado lo dice en su nota.
// Es lo que ya hacía Paraguay con los materiales fuera de la lista de ANDE.
const servida = (c) => c.precios.some((p) => p.precio > 0);
const ciudadRef = ofiPaisViejo.ciudades.find(servida);
if (!ciudadRef) { console.error("ninguna ciudad tiene un solo precio relevado: no hay de dónde copiar"); process.exit(2); }
const ciudades = ofiPaisViejo.ciudades.map((c) => ({
  nombre: c.nombre,
  precios: maestro.map((m) => {
    const propio = precioEn(c, m.idCanonico);
    const rel = propio ?? precioEn(ciudadRef, m.idCanonico);
    const copiado = !propio && !!rel;
    const viejo = (copiado ? ciudadRef : c).precios.find((x) => x.idCanonico === cfg.equivalentes[m.idCanonico]);
    const notaBase = viejo ? (viejo.nota ?? "") : (rel ? `Precio heredado de «${rel.nombre}» (misma familia / mismo escalafón)` : "");
    return {
      idCanonico: idPais(m.idCanonico),
      nombre: viejo?.nombre ?? m.nombre,
      categoria: m.categoria,
      unidad: viejo?.unidad ?? m.unidad,
      tipoInsumo: m.tipoInsumo,
      codigo: codigoPais(m.idCanonico, m.codigo),
      precio: rel ? rel.precio : 0,
      nota: rel
        ? (copiado ? `COPIADO de ${ciudadRef.nombre} (referencial, sin relevar en ${c.nombre}). ${notaBase}`.trim() : notaBase)
        : `PENDIENTE: sin precio relevado en ${PAIS}. Insumo heredado de la base boliviana (${m.idCanonico}); cargalo a mano o esperá la próxima publicación.`,
    };
  }),
}));

// ── items_XX: sólo los que cierran con precio completo en TODAS las ciudades SERVIDAS ──────
// Las líneas de PORCENTAJE (leyes sociales chilenas) no llevan precio: no cuentan como faltante.
const servidas = ciudades.filter((c) => c.precios.length);
const conPrecio = new Set();
for (const m of maestro) {
  if (servidas.every((c) => (c.precios.find((p) => p.idCanonico === idPais(m.idCanonico))?.precio ?? 0) > 0)) conPrecio.add(m.idCanonico);
}
const primeraServida = ofiPaisViejo.ciudades.find(servida);
const items = [];
const bloqueo = new Map();
for (const it of itemsBO.items) {
  const conPrecioReq = it.insumos.filter((s) => s.tipoCalculo !== "PORCENTAJE");
  const faltan = [...new Set(conPrecioReq.filter((s) => !conPrecio.has(s.idCanonico)).map((s) => s.idCanonico))];
  for (const id of faltan) bloqueo.set(id, (bloqueo.get(id) ?? 0) + 1);
  if (faltan.length) continue;
  const insumos = it.insumos.map((s) => {
    const viejo = primeraServida.precios.find((x) => x.idCanonico === cfg.equivalentes[s.idCanonico]);
    return { ...s, idCanonico: idPais(s.idCanonico), codigo: codigoPais(s.idCanonico, s.codigo), nombre: viejo?.nombre ?? s.nombre, unidad: viejo?.unidad ?? s.unidad, precio: 0 };
  });
  // Líneas que el país agrega a cada APU (Chile: leyes sociales como % de la M.O.).
  for (const extra of cfg.lineasExtra?.(it) ?? []) insumos.push(extra);
  items.push({ ...it, codigo: `${it.codigo}${PAIS}`, insumos });
}

// ── Chequeos: lo que las guardas del PC van a exigir, comprobado ACÁ antes de escribir ─────
const err = [];
const setBase = new Set(ciudades[0].precios.map((p) => p.idCanonico));
for (const c of ciudades) {
  const ids = c.precios.map((p) => p.idCanonico);
  if (new Set(ids).size !== ids.length) err.push(`${c.nombre}: idCanonico repetido`);
  if (ids.length !== setBase.size || ids.some((i) => !setBase.has(i))) err.push(`${c.nombre}: set de insumos distinto al de la primera ciudad`);
}
const cods = items.map((i) => i.codigo);
if (new Set(cods).size !== cods.length) err.push("códigos de ítem repetidos");
if (!servidas.length) err.push("ninguna ciudad servida: no hay un solo precio relevado");
for (const i of items) for (const s of i.insumos.filter((x) => x.tipoCalculo !== "PORCENTAJE")) {
  for (const c of servidas) if (!((c.precios.find((p) => p.idCanonico === s.idCanonico)?.precio ?? 0) > 0)) err.push(`${i.codigo}: ${s.idCanonico} sin precio en ${c.nombre}`);
}
if (err.length) { console.error("✗ derivación inválida:"); for (const e of err.slice(0, 20)) console.error("  · " + e); process.exit(1); }

const zerosPorCiudad = Math.max(...servidas.map((c) => c.precios.filter((p) => !p.precio).length));
const salidaItems = { version: cfg.version, schemaVersion: itemsBO.schemaVersion ?? 1, items };
const salidaPrecios = {
  version: cfg.version, fuente: cfg.fuente, pais: PAIS,
  nota: `Base de ${PAIS} DERIVADA de la boliviana (2-sep-2026): los ${maestro.length} insumos de Bolivia bajo el espacio ${iso}_, en las ${ciudades.length} ciudades de la caja. Los relevados traen precio por ciudad; los PENDIENTES van en 0 con nota y se ven como «sin precio». Los ítems publicados son SÓLO los que cierran con precio completo (${items.length} de ${itemsBO.items.length}); regenerar con tools/derivar-desde-bolivia.mjs cuando entren precios nuevos. ${ofiPaisViejo.nota ? "Nota de la base anterior: " + ofiPaisViejo.nota : ""}`,
  precios: [],
  ciudades,
};
writeFileSync(join(BASE, `catalogo/v1.0/items_${PAIS}.json`), JSON.stringify(salidaItems, null, 2) + "\n");
writeFileSync(join(BASE, `precios/v1.0/oficiales_${PAIS}.json`), JSON.stringify(salidaPrecios, null, 2) + "\n");

const top = [...bloqueo.entries()].sort((a, b) => b[1] - a[1]).slice(0, 15);
console.log(`✓ ${PAIS}: ${items.length}/${itemsBO.items.length} ítems con precio completo · ${maestro.length} insumos × ${ciudades.length} ciudades · pendientes por ciudad: ${zerosPorCiudad} (poner ese TOPE en estado-de-las-bases.test.ts)`);
console.log("  los que más destraban al relevarlos:");
for (const [id, n] of top) console.log(`    ${String(n).padStart(3)}  ${id}`);
