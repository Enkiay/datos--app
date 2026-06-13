/**
 * NORMALIZADOR CANÓNICO DE INSUMOS — fuente única de verdad.
 *
 * Saneo de la BD compartida (la consumen APK, web y PC). Estampa en CADA insumo,
 * en TODOS los archivos, dos cosas consistentes:
 *   - `categoria`: categoría canónica (las 18 de PREFIJOS_CATEGORIA).
 *   - `codigo`: esquema único `{2 letras categoría}{NNN}` (sin letra de tipo ni "U").
 *
 * Antes la BD tenía categoría ausente (oficiales.json) o degradada al cajón
 * "Ferretería" (items.json), y códigos en 3 formatos viejos mezclados
 * (M###/O###/E###) + vacíos. Eso hacía que cada app se comportara distinto.
 * Ahora la categorización vive ACÁ (no en cada app); las apps re-descargan y
 * adoptan lo mismo.
 *
 * Prioridad de categoría por insumo (idCanonico):
 *   1) Seed a mano de la APK (AppDatabase.kt → _seed_apk.json): máxima autoridad.
 *   2) items.json embebido, SI es categoría específica (no el cajón "Ferretería").
 *   3) Clasificador por palabra clave (refina "Ferretería" y cubre lo que falte).
 *   4) items.json "Ferretería" / "General".
 *
 * Determinista e idempotente: misma entrada → misma salida (numeración por
 * idCanonico ordenado dentro de cada bucket).
 */

import { readFileSync, writeFileSync } from "node:fs";

const DIR = "C:/Users/Equipo/_datos_app_work/";
const F_OFI = DIR + "precios/v1.0/oficiales.json";
const F_ITEMS = DIR + "catalogo/v1.0/items.json";
const F_ITEMS_BO = DIR + "catalogo/v1.0/items_BO.json";
const F_SEED = DIR + "tools/_seed_apk.json";
const APLICAR = process.argv.includes("--apply");

// ── Utilidades ───────────────────────────────────────────────────────────────
const norm = (s) => (s || "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase().trim();

const PREFIJOS_CATEGORIA = {
  Agregados: "AG", "Cemento y Cal": "CM", "Acero y Metal": "AC", Madera: "MD",
  "Ladrillos y Cerámicos": "LC", Pinturas: "PT", "Ferretería": "FE", "Plomería": "PL",
  "Eléctrico": "EL", "Impermeabilización": "IM", Adhesivos: "AD", Cubiertas: "CB",
  Calificada: "CA", "No Calificada": "NC", "Obras Civiles": "OC", Pintura: "PI", Equipo: "EQ",
  Maquinaria: "MQ", Herramientas: "HE", General: "GN",
};
const letrasCat = (cat) => PREFIJOS_CATEGORIA[cat] || "GN";

// Reglas keyword → categoría canónica (idénticas a arqon-pc/src/core/categorias-insumo.ts).
const REGLAS_MATERIAL = [
  [/pegamento|pegaladrillo|cemento cola|adhesiv|cola fresca|masa flex|panel fix|parketek|sikaflex/, "Adhesivos"],
  [/impermeabiliz|sika ?1|sikadur|igol|membrana|asfalt|alquitran|lamina sika|neopreno/, "Impermeabilización"],
  [/pintura|barniz|sellador|latex|esmalte|anticorrosiv|superlatex|fondo preparador|aguarras|phono spray|termo spray/, "Pinturas"],
  [/calamina|policarbonato|placa ondulada|duralit|cenefa|vigueta|plastoform|costanera|cubierta de/, "Cubiertas"],
  [/cable|alambre cu|foco|luminaria|lampara|interruptor|tomacorriente|tablero|transformador|jabalina|electroducto|conduit|socket|timbre|plaqueta|tomacorr|terminal.*utp|cinta aislante|aire acondicionado|caja.*electric/, "Eléctrico"],
  [/tuberia|tubo|caneria|cañeria|pvc|codo|copla|tee |reduccion|llave de paso|valvula|sifon|camara sept|fosa sept|inodoro|lavamanos|lavaplatos|urinario|bide|ducha|griferia|mezclador|tanque|bomba|medidor de agua|supertubo|politubo|rejilla|caja sifonada|caja interceptora|calefon|hidro|acople|anillo de goma|niple|union universal|union por termofusion|chupador/, "Plomería"],
  [/ladrillo|ceramic|cerámic|azulejo|baldosa|porcelanato|mosaico|teja|adoquin|loseta|bloque|sillar|gambote|piso flotante|zocalo de ceramica|pavic|marmol|piedra pizarra|piso/, "Ladrillos y Cerámicos"],
  [/cedro|machihembre|madera|liston|tablero|entablonado|palo maria|tajibo|parket|zocalo cedro/, "Madera"],
  [/fierro|acero|perfil|plancha metalic|plancha de|tubular|angular|pletina|alambre|soldadura|electrodos|cantonera|reja metalic|estructura metalic|malla alambre|cold rolled|cable grado/, "Acero y Metal"],
  [/cemento|\bcal\b|yeso|estuco|hormigon|mortero|aditivo|masilla|revoque|ocre|nitrato/, "Cemento y Cal"],
  [/arena|grava|gravilla|piedra|tierra|ripio|turba|\blama\b|caucho granulado|estiercol|paja|kikuyo|cesped|tepe|ray.*grass/, "Agregados"],
  [/tornillo|tirafondo|bisagra|chapa|picaporte|cerradura|anclaje|tacos|quincalleria|silicona|teflon|lija|brazo hidraulico|chicotillo|marco/, "Ferretería"],
];
function keyword(nombre, tipo) {
  if (tipo !== "MATERIAL") return "";
  const n = norm(nombre);
  for (const [re, cat] of REGLAS_MATERIAL) if (re.test(n)) return cat;
  return "";
}

// ── Cargar datos ─────────────────────────────────────────────────────────────
const ofi = JSON.parse(readFileSync(F_OFI, "utf8"));
const items = JSON.parse(readFileSync(F_ITEMS, "utf8"));
const itemsBO = JSON.parse(readFileSync(F_ITEMS_BO, "utf8"));
const seed = JSON.parse(readFileSync(F_SEED, "utf8"));

// seed por nombre normalizado → categoría (autoridad máxima)
const seedPorNombre = new Map();
for (const s of seed) if (!seedPorNombre.has(norm(s.nombre))) seedPorNombre.set(norm(s.nombre), s.categoria);

// items.json embebido: idCanonico → categoría
const catItems = new Map();
const CATCH_ALL = "Ferretería";
for (const src of [items, itemsBO]) for (const it of src.items || []) for (const ins of it.insumos || []) {
  const k = norm(ins.idCanonico);
  if (k && ins.categoria && !catItems.has(k)) catItems.set(k, ins.categoria);
}

// ── Recolectar el universo de insumos (idCanonico → {nombre, tipo}) ───────────
const universo = new Map();
function registrar(idCanonico, nombre, tipo) {
  const k = norm(idCanonico);
  if (!k) return;
  if (!universo.has(k)) universo.set(k, { idCanonico: idCanonico.trim(), nombre: nombre || "", tipo: tipo || "MATERIAL" });
}
for (const c of ofi.ciudades || []) for (const p of c.precios || []) registrar(p.idCanonico, p.nombre, p.tipoInsumo || "MATERIAL");
for (const src of [items, itemsBO]) for (const it of src.items || []) for (const ins of it.insumos || []) registrar(ins.idCanonico, ins.nombre, ins.tipoInsumo || "MATERIAL");

// ── Resolver categoría por insumo ────────────────────────────────────────────
function resolverCategoria(nombre, tipo, idc) {
  const seedCat = seedPorNombre.get(norm(nombre));
  if (seedCat) return seedCat;
  const itemCat = catItems.get(norm(idc)) || "";
  if (itemCat && itemCat !== CATCH_ALL) return itemCat;
  const kw = keyword(nombre, tipo);
  if (kw) return kw;
  if (itemCat) return itemCat;          // Ferretería si lo tenía
  return "General";
}

const canon = new Map(); // idCanonico(norm) → {categoria, codigo}
for (const [k, v] of universo) canon.set(k, { categoria: resolverCategoria(v.nombre, v.tipo, v.idCanonico), tipo: v.tipo, idCanonico: v.idCanonico });

// ── Asignar código uniforme por bucket (tipo+categoría), ordenado por idCanonico ─
const buckets = new Map(); // prefijo → [idCanonico(norm)...]
for (const [k, v] of canon) {
  const pref = letrasCat(v.categoria); // esquema único: 2 letras categoría + NNN
  if (!buckets.has(pref)) buckets.set(pref, []);
  buckets.get(pref).push(k);
}
for (const [pref, ks] of buckets) {
  ks.sort((a, b) => a.localeCompare(b));
  ks.forEach((k, i) => { canon.get(k).codigo = pref + String(i + 1).padStart(3, "0"); });
}

// ── Aplicar a los archivos (mutar en sitio, preservar todo lo demás) ──────────
let tocadosOfi = 0, tocadosItems = 0;
const preciosAntes = [];
for (const c of ofi.ciudades || []) for (const p of c.precios || []) {
  preciosAntes.push(p.precio);
  const cc = canon.get(norm(p.idCanonico));
  if (cc) { p.codigo = cc.codigo; p.categoria = cc.categoria; tocadosOfi++; }
}
const preciosDespues = [];
for (const c of ofi.ciudades || []) for (const p of c.precios || []) preciosDespues.push(p.precio);

for (const src of [items, itemsBO]) for (const it of src.items || []) for (const ins of it.insumos || []) {
  const cc = canon.get(norm(ins.idCanonico));
  if (cc) { ins.categoria = cc.categoria; ins.codigo = cc.codigo; tocadosItems++; }
}

// ── Verificaciones ───────────────────────────────────────────────────────────
const erroresPrecio = preciosAntes.filter((v, i) => v !== preciosDespues[i]).length;
const sinCat = [], codInvalido = [], REGEX = /^[A-Z]{2}\d{3}$/;
const codePorId = new Map(), inconsistencias = [];
for (const c of ofi.ciudades || []) for (const p of c.precios || []) {
  if (!p.categoria || !String(p.categoria).trim()) sinCat.push(p.nombre);
  if (!REGEX.test(p.codigo)) codInvalido.push(p.codigo + " " + p.nombre);
  const k = norm(p.idCanonico), prev = codePorId.get(k);
  if (prev && prev !== p.codigo) inconsistencias.push(k);
  codePorId.set(k, p.codigo);
}
const dist = {};
for (const [, v] of canon) dist[v.categoria] = (dist[v.categoria] || 0) + 1;

console.log("=== NORMALIZACIÓN CANÓNICA ===");
console.log("insumos únicos (idCanonico):", canon.size);
console.log("precios oficiales tocados:", tocadosOfi, "| insumos embebidos en items tocados:", tocadosItems);
console.log("VERIF precios alterados:", erroresPrecio, "(debe ser 0)");
console.log("VERIF sin categoría:", sinCat.length, "(debe ser 0)", sinCat.slice(0, 5));
console.log("VERIF código inválido:", codInvalido.length, "(debe ser 0)", codInvalido.slice(0, 5));
console.log("VERIF idCanonico con código inconsistente entre ciudades:", inconsistencias.length, "(debe ser 0)");
console.log("DISTRIB categorías:", Object.entries(dist).sort((a, b) => b[1] - a[1]).map(([k, v]) => `${k}=${v}`).join("  "));
console.log("BUCKETS de código:", [...buckets.keys()].sort().map((p) => `${p}=${buckets.get(p).length}`).join("  "));

// ── Escritura (solo con --apply), preservando CRLF + indent 2 + trailing CRLF ─
function escribir(path, obj) {
  const txt = JSON.stringify(obj, null, 2).replace(/\n/g, "\r\n") + "\r\n";
  writeFileSync(path, txt, "utf8");
}
if (APLICAR) {
  escribir(F_OFI, ofi);
  escribir(F_ITEMS, items);
  escribir(F_ITEMS_BO, itemsBO);
  console.log(">>> ARCHIVOS ESCRITOS (--apply)");
} else {
  console.log(">>> DRY-RUN (sin escribir). Re-ejecutar con --apply para aplicar.");
}
