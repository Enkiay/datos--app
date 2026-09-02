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
};
const cfg = CONFIG[PAIS];
if (!cfg) { console.error(`no hay tabla para ${PAIS}: agregala en CONFIG`); process.exit(2); }

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
const ciudades = ofiPaisViejo.ciudades.map((c) => ({
  nombre: c.nombre,
  precios: maestro.map((m) => {
    const rel = precioEn(c, m.idCanonico);
    const viejo = c.precios.find((x) => x.idCanonico === cfg.equivalentes[m.idCanonico]);
    return {
      idCanonico: idPais(m.idCanonico),
      nombre: viejo?.nombre ?? m.nombre,
      categoria: m.categoria,
      unidad: viejo?.unidad ?? m.unidad,
      tipoInsumo: m.tipoInsumo,
      codigo: codigoPais(m.idCanonico, m.codigo),
      precio: rel ? rel.precio : 0,
      nota: rel
        ? (viejo ? (viejo.nota ?? "") : `Precio heredado de «${rel.nombre}» (misma familia / mismo escalafón)`)
        : `PENDIENTE: sin precio relevado en ${PAIS}. Insumo heredado de la base boliviana (${m.idCanonico}); cargalo a mano o esperá la próxima publicación.`,
    };
  }),
}));

// ── items_XX: sólo los que cierran con precio completo en TODAS las ciudades ───────────────
const conPrecio = new Set();
for (const m of maestro) {
  if (ciudades.every((c) => (c.precios.find((p) => p.idCanonico === idPais(m.idCanonico))?.precio ?? 0) > 0)) conPrecio.add(m.idCanonico);
}
const items = [];
const bloqueo = new Map();
for (const it of itemsBO.items) {
  const faltan = [...new Set(it.insumos.filter((s) => !conPrecio.has(s.idCanonico)).map((s) => s.idCanonico))];
  for (const id of faltan) bloqueo.set(id, (bloqueo.get(id) ?? 0) + 1);
  if (faltan.length) continue;
  items.push({
    ...it,
    codigo: `${it.codigo}${PAIS}`,
    insumos: it.insumos.map((s) => {
      const viejo = ofiPaisViejo.ciudades[0].precios.find((x) => x.idCanonico === cfg.equivalentes[s.idCanonico]);
      return { ...s, idCanonico: idPais(s.idCanonico), codigo: codigoPais(s.idCanonico, s.codigo), nombre: viejo?.nombre ?? s.nombre, unidad: viejo?.unidad ?? s.unidad, precio: 0 };
    }),
  });
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
for (const i of items) for (const s of i.insumos) {
  for (const c of ciudades) if (!((c.precios.find((p) => p.idCanonico === s.idCanonico)?.precio ?? 0) > 0)) err.push(`${i.codigo}: ${s.idCanonico} sin precio en ${c.nombre}`);
}
if (err.length) { console.error("✗ derivación inválida:"); for (const e of err.slice(0, 20)) console.error("  · " + e); process.exit(1); }

const zerosPorCiudad = Math.max(...ciudades.map((c) => c.precios.filter((p) => !p.precio).length));
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
