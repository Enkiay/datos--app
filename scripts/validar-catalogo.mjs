#!/usr/bin/env node
// Validador del modelo de datos del catálogo. Falla (exit 1) si un cambio
// rompe los invariantes acordados:
//
//  ÍTEMS (regla espejo):
//   1. items.json e items_BO.json tienen el MISMO set de códigos.
//  INSUMOS (un catálogo, precio por ciudad):
//   2. Todo insumo embebido lleva idCanonico y precio > 0.
//   3. Mismo idCanonico → mismo precio nacional, nombre, unidad y tipo en
//      TODAS sus referencias (0 divergencias).
//   4. Todo idCanonico del catálogo existe en oficiales.json en TODAS las
//      ciudades (hoy 9) con precio > 0 — un insumo nuevo nace en todas con
//      el mismo precio inicial.
//   5. oficiales.json: sin duplicados dentro de una ciudad; todas las
//      ciudades comparten el mismo set de insumos.
//  POLÍTICA DE PARÁMETROS:
//   6. valorDefault = 1 en todos los parámetros (única excepción: UH021).
//
// Uso:  node scripts/validar-catalogo.mjs   (también corre como hook pre-push)
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const BASE = join(dirname(fileURLToPath(import.meta.url)), "..");
const items = JSON.parse(readFileSync(join(BASE, "catalogo/v1.0/items.json"), "utf8"));
const itemsBO = JSON.parse(readFileSync(join(BASE, "catalogo/v1.0/items_BO.json"), "utf8"));
const ofi = JSON.parse(readFileSync(join(BASE, "precios/v1.0/oficiales.json"), "utf8"));

const errores = [];
const err = (m) => errores.push(m);

// 1. Espejo de códigos
const cods = new Set(items.items.map((i) => i.codigo));
const codsBO = new Set(itemsBO.items.map((i) => i.codigo));
for (const c of cods) if (!codsBO.has(c)) err(`ESPEJO: ${c} está en items.json pero falta en items_BO.json`);
for (const c of codsBO) if (!cods.has(c)) err(`ESPEJO: ${c} está en items_BO.json pero falta en items.json`);

// Unidades que la APK NORMALIZA a otra forma (UnidadCanonica.MAPA): si el
// catálogo trae la variante (ej. "Lt"), la app la guarda canonizada ("L") y
// luego "Verificar insumos" la marca como diferente para siempre (loop). El
// catálogo DEBE traer ya la forma canónica. clave lowercase → forma canónica.
const NORM_UNIDAD = {
  kg: "Kg", kgs: "Kg", kilogramo: "Kg", gramo: "gr", g: "gr",
  ton: "Ton", tonelada: "Ton", tn: "Ton", t: "Ton",
  l: "L", lt: "L", lts: "L", litro: "L", cc: "cm3", "dm³": "dm3",
  "m³": "m3", "metro cubico": "m3", "m²": "m2", "metro cuadrado": "m2", "cm²": "cm2",
  metro: "m", mts: "m", pie2: "p2", "p²": "p2",
  hr: "Hr", h: "Hr", hora: "Hr", horas: "Hr", "día": "día", d: "día",
  pieza: "Pza", piezas: "Pza", und: "u", unidad: "u",
  punto: "pto", puntos: "pto", pnt: "pto",
  global: "Glb", gbl: "Glb", gl: "Glb", hojas: "Hoja", tubos: "Tubo",
  rollos: "Rollo", bolsas: "Bolsa", sacos: "Saco", barras: "Barra",
  cajas: "Caja", juegos: "Juego", jgo: "Juego", pares: "Par",
  pct: "%", porcentaje: "%",
};
const unidadCanonica = (u) => {
  const k = (u || "").trim().toLowerCase();
  return NORM_UNIDAD[k] || (u || "").trim();
};

// 2-3. Insumos embebidos coherentes (sobre ambos archivos)
const porId = new Map(); // id → { precio, nombre, unidad, tipo, ref }
for (const [tag, cat] of [["items", items], ["items_BO", itemsBO]]) {
  for (const it of cat.items) {
    for (const ins of it.insumos || []) {
      const ref = `${tag}/${it.codigo}`;
      const id = (ins.idCanonico || "").trim();
      if (!id) { err(`INSUMO sin idCanonico: "${ins.nombre}" en ${ref}`); continue; }
      if (!(ins.precio > 0)) err(`INSUMO sin precio (>0): "${ins.nombre}" [${id}] en ${ref}`);
      // Unidad debe estar ya canonizada (sino la APK la "corregiría" en loop).
      const canon = unidadCanonica(ins.unidad);
      if (ins.unidad && ins.unidad.trim() !== canon) {
        err(`UNIDAD no canónica [${id}]: "${ins.unidad}" debería ser "${canon}" (${ref})`);
      }
      const prev = porId.get(id);
      if (!prev) { porId.set(id, { precio: ins.precio, nombre: ins.nombre, unidad: ins.unidad, tipo: ins.tipoInsumo, ref }); continue; }
      if (ins.precio !== prev.precio) err(`PRECIO divergente [${id}]: ${prev.precio} (${prev.ref}) vs ${ins.precio} (${ref})`);
      if (ins.nombre !== prev.nombre) err(`NOMBRE divergente [${id}]: "${prev.nombre}" vs "${ins.nombre}" (${ref})`);
      if (ins.unidad !== prev.unidad) err(`UNIDAD divergente [${id}]: "${prev.unidad}" vs "${ins.unidad}" (${ref})`);
      if (ins.tipoInsumo !== prev.tipo) err(`TIPO divergente [${id}]: ${prev.tipo} vs ${ins.tipoInsumo} (${ref})`);
    }
  }
}

// 4-5. oficiales.json: cobertura total y sets idénticos entre ciudades
const ciudades = ofi.ciudades || [];
if (ciudades.length < 9) err(`OFICIALES: ${ciudades.length} ciudades (se esperan 9)`);
const setsPorCiudad = ciudades.map((c) => {
  const vistos = new Map();
  for (const p of c.precios || []) {
    const id = (p.idCanonico || "").trim();
    if (!id) { err(`OFICIALES ${c.nombre}: entrada sin idCanonico ("${p.nombre}")`); continue; }
    if (vistos.has(id)) err(`OFICIALES ${c.nombre}: idCanonico duplicado [${id}]`);
    if (!(p.precio > 0)) err(`OFICIALES ${c.nombre}: precio no positivo [${id}] = ${p.precio}`);
    vistos.set(id, p);
  }
  return { nombre: c.nombre, ids: new Set(vistos.keys()) };
});
const base = setsPorCiudad[0];
for (const s of setsPorCiudad.slice(1)) {
  for (const id of base.ids) if (!s.ids.has(id)) err(`OFICIALES: [${id}] está en ${base.nombre} pero falta en ${s.nombre}`);
  for (const id of s.ids) if (!base.ids.has(id)) err(`OFICIALES: [${id}] está en ${s.nombre} pero falta en ${base.nombre}`);
}
for (const id of porId.keys()) {
  if (base && !base.ids.has(id)) err(`COBERTURA: [${id}] usado en el catálogo pero ausente de oficiales.json`);
}

// 6. Política: defaults = 1 (excepción UH021, paramétrico real)
for (const [tag, cat] of [["items", items], ["items_BO", itemsBO]]) {
  for (const it of cat.items) {
    if (it.codigo === "UH021") continue;
    for (const p of it.parametros || []) {
      if (p.valorDefault !== undefined && p.valorDefault !== 1) {
        err(`DEFAULT≠1: ${tag}/${it.codigo} param "${p.nombre}" = ${p.valorDefault}`);
      }
    }
  }
}

if (errores.length) {
  console.error(`✗ Validación FALLÓ — ${errores.length} problema(s):`);
  for (const e of errores.slice(0, 50)) console.error("  · " + e);
  if (errores.length > 50) console.error(`  … y ${errores.length - 50} más`);
  process.exit(1);
}
console.log(`✓ Catálogo válido: ${cods.size} ítems espejo · ${porId.size} insumos canónicos · ${ciudades.length} ciudades × ${base ? base.ids.size : 0} precios`);
