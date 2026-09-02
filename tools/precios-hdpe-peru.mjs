#!/usr/bin/env node
// LOS 179 HDPE DE PERÚ, POR MASA LINEAL (2-sep-2026, pedido de Oscar: «los insumos sin precio de
// Perú, corregilos o dales unos tentativos»).
//
// ── POR QUÉ ESTOS 179 SE PUEDEN CALCULAR Y OTROS NO ──────────────────────────────────────────
// La tubería de polietileno es el caso raro en que el precio NO hay que adivinarlo: un tubo HDPE
// se vende, de hecho, por KILO de resina. Su masa por metro sale de la geometría, y la geometría
// está entera en el nombre del insumo:
//
//     pared        e = D / SDR                         (SDR = diámetro / espesor, es la norma)
//     masa/m       m = π · e · (D − e) · ρ · 1e-3      (kg/m, con D y e en mm)
//     precio/m     m × precio del kilo
//
// Comprobación con catálogo: D=110, SDR 11 → e = 10 mm → 3,00 kg/m. Los fabricantes publican
// 3,00–3,14 kg/m para ese tubo. La fórmula es la buena.
//
// El precio del KILO se CALIBRA con precios reales de tubería HDPE peruana
// (precios/fuentes/hdpe_PE.json): se ajusta por mínimos cuadrados sin término independiente
// —doblar la masa dobla el precio, un tubo de masa cero cuesta cero— separando PE 80 de PE 100,
// que son resinas distintas. Sin ese archivo el script NO corre: calibrar con nada sería inventar.
//
// Cada precio queda con su nota diciendo que es TENTATIVO, con qué masa y qué kilo salió, y que
// hay que revisarlo antes de ofertar. Es la misma regla de la casa que los ESTIMADOS de los otros
// países: un número con su origen a la vista, nunca un número mudo.
//
// Uso:  node tools/precios-hdpe-peru.mjs [--dry]
import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const BASE = join(dirname(fileURLToPath(import.meta.url)), "..");
const DRY = process.argv.includes("--dry");
const F_PRE = join(BASE, "precios/v1.0/oficiales_PE.json");
const F_REF = join(BASE, "precios/fuentes/hdpe_PE.json");
const VERSION = "v20260902-hdpe-por-masa";

/** Densidad de la resina (g/cm³). El PE 100 es algo más denso que el PE 80. */
const RHO = { 100: 0.955, 80: 0.945 };

/** Espesor mínimo de pared que exige la norma, pase lo que pase con el SDR (ISO 4427: 2,0 mm).
 *  Sin esto, un D=20 SDR 21 saldría con pared de 0,95 mm — un tubo que no existe. */
const E_MIN = 2.0;

/** D, SDR y material salen del nombre: «TUBERIA HDPE D=110mm SDR 11 (PN 16) PE 100». */
function geometria(nombre) {
  const d = /D\s*=\s*([\d.]+)\s*mm/i.exec(nombre);
  const sdr = /SDR\s*([\d.]+)/i.exec(nombre);
  const pe = /PE\s*(80|100)/i.exec(nombre);
  if (!d || !sdr || !pe) return null;
  const D = +d[1], SDR = +sdr[1], material = +pe[1];
  if (!(D > 0) || !(SDR > 1)) return null;
  const e = Math.max(D / SDR, E_MIN);                  // espesor de pared, mm
  const kgPorM = Math.PI * e * (D - e) * RHO[material] * 1e-3;
  return { D, SDR, material, e, kgPorM };
}

// ── Autochequeo de la fórmula contra catálogo de fabricante ─────────────────────────────────
// Si alguien toca la geometría (o confunde SDR con espesor), esto lo caza antes de escribir 179
// precios mal. Los pesos son de tabla ISO 4427; el cálculo da el espesor MÍNIMO, así que sale un
// 3-5 % por debajo del tubo real — y eso está bien: el kilo se calibra con esta misma fórmula, así
// que el sesgo se absorbe. Lo que no puede pasar es una diferencia grande.
{
  const catalogo = [
    { nombre: "TUBERIA HDPE D=110mm SDR 11 (PN 16) PE 100", kg: 3.14 },
    { nombre: "TUBERIA HDPE D=63mm SDR 11 (PN 16) PE 100", kg: 1.04 },
    { nombre: "TUBERIA HDPE D=160mm SDR 17 (PN 10) PE 100", kg: 4.42 },
    { nombre: "TUBERIA HDPE D=200mm SDR 11 (PN 16) PE 100", kg: 10.4 },
    { nombre: "TUBERIA HDPE D=400mm SDR 17 (PN 10) PE 100", kg: 27.5 },
    // El chico manda la pared mínima (2,0 mm), no el SDR: sin E_MIN esto se iba 10 % abajo.
    { nombre: "TUBERIA HDPE D=20mm SDR 11 (PN 16) PE 100", kg: 0.11 },
  ];
  const malos = catalogo.map((c) => ({ ...c, mio: geometria(c.nombre).kgPorM }))
    .filter((c) => Math.abs(c.mio - c.kg) / c.kg > 0.08);
  if (malos.length) {
    console.error("✗ la fórmula de masa no coincide con el catálogo del fabricante:");
    for (const m of malos) console.error(`   ${m.nombre}: calculado ${m.mio.toFixed(2)} kg/m vs catálogo ${m.kg} kg/m`);
    process.exit(1);
  }
}

// ── Calibración: precio del kilo, por material ──────────────────────────────────────────────
if (!existsSync(F_REF)) {
  console.error(`falta ${F_REF}: sin precios reales de HDPE peruano no hay con qué calibrar el kilo.`);
  console.error("El archivo es un array de { diametroMm, sdr, material, precioPorMetro, fuente, url, fecha, confianza, nota }");
  console.error("y/o entradas { precioPorKg, material, fuente, ... }.");
  process.exit(2);
}
const refs = JSON.parse(readFileSync(F_REF, "utf8"));
const IGV = 1.18;   // la cadena peruana agrega el IGV al final: los insumos van SIN IGV
const conIgv = (r) => /con igv|igv incl|incluye igv|precio mostrador/i.test(`${r.nota ?? ""} ${r.fuente ?? ""}`)
  && !/sin igv|\+ ?igv|neto/i.test(`${r.nota ?? ""}`);
const neto = (v, r) => (conIgv(r) ? v / IGV : v);

/**
 * FUENTES QUE NO FIJAN EL NIVEL, aunque sí sirven para verificar la FORMA.
 *
 * El buscador trajo dos mundos separados por 3×: el mercado peruano (El Ganadero, Aquaplast) a
 * S/ 6–10 el kilo de tubo, y el Generador de Precios de CYPE a S/ 21–26. La base peruana de ArqOn
 * es de MERCADO —«Semilla de referencia de mercado peruano», y así están sus otros 604 precios—,
 * así que calibrar con CYPE dejaría las tuberías tres veces por encima del resto de la lista: un
 * presupuesto de agua saldría al triple sin que nada lo avisara.
 *
 * Lo que CYPE sí aporta, y vale mucho: sus 61 puntos cubren de Ø20 a Ø400 y su precio por kilo es
 * PLANO (24,0 en Ø≤63 contra 23,0 en Ø≥160, relación 1,04). Eso confirma, con datos ajenos, que
 * «precio = kilo × masa» es la ley correcta en todo el rango y que no hay efecto de escala que
 * corregir. El mercado dice lo mismo en su tramo (6,0–8,2 sin tendencia con el diámetro).
 */
const SOLO_FORMA = /CYPE|generador de precios/i;

const puntos = { 80: [], 100: [] };
const verificacion = [];
const sueltos = { 80: [], 100: [] };   // precios por kilo declarados directamente
for (const r of refs) {
  const mat = /80/.test(String(r.material ?? "")) ? 80 : /100/.test(String(r.material ?? "")) ? 100 : null;
  if (r.precioPorKg > 0) { if (mat) sueltos[mat].push(neto(r.precioPorKg, r)); else { sueltos[80].push(neto(r.precioPorKg, r)); sueltos[100].push(neto(r.precioPorKg, r)); } continue; }
  if (!(r.precioPorMetro > 0) || !(r.diametroMm > 0) || !(r.sdr > 1) || !mat) continue;
  const e = Math.max(r.diametroMm / r.sdr, E_MIN);
  const kg = Math.PI * e * (r.diametroMm - e) * RHO[mat] * 1e-3;
  const punto = { kg, precio: neto(r.precioPorMetro, r), r, D: r.diametroMm };
  if (SOLO_FORMA.test(String(r.fuente ?? ""))) verificacion.push(punto);
  else puntos[mat].push(punto);
}
// La FORMA, comprobada con las fuentes que no fijan nivel: ¿el kilo es plano de punta a punta?
if (verificacion.length >= 8) {
  const sk = verificacion.map((p) => ({ D: p.D, k: p.precio / p.kg }));
  const med = (a) => { const s = [...a].sort((x, y) => x - y); return s[Math.floor(s.length / 2)]; };
  const chico = med(sk.filter((x) => x.D <= 63).map((x) => x.k)), grande = med(sk.filter((x) => x.D >= 160).map((x) => x.k));
  if (chico && grande) {
    const rel = chico / grande;
    console.log(`  forma verificada con ${verificacion.length} puntos ajenos (${verificacion[0].r.fuente.split(/[-(–]/)[0].trim()}): kilo Ø≤63 / Ø≥160 = ${rel.toFixed(2)} → ${Math.abs(rel - 1) < 0.15 ? "PLANO, la ley precio = kilo × masa se sostiene en todo el rango" : "¡NO es plano! hay efecto de escala que este modelo no captura"}`);
    if (Math.abs(rel - 1) >= 0.3) { console.error("  ✗ el precio por kilo NO es plano: el modelo proporcional no sirve acá"); process.exit(1); }
  }
}
/** Mínimos cuadrados SIN término independiente: precio = k · masa. */
const ajustar = (ps) => (ps.length ? ps.reduce((a, p) => a + p.kg * p.precio, 0) / ps.reduce((a, p) => a + p.kg * p.kg, 0) : null);
const mediana = (a) => { const s = [...a].sort((x, y) => x - y); return s.length ? (s.length % 2 ? s[(s.length - 1) / 2] : (s[s.length / 2 - 1] + s[s.length / 2]) / 2) : null; };

const nombreFuente = (s) => String(s ?? "").split(/[-(–]/)[0].trim();
const kilo = {}, detalle = {};
for (const mat of [80, 100]) {
  const porRegresion = ajustar(puntos[mat]);
  const porDeclarado = mediana(sueltos[mat]);
  kilo[mat] = porRegresion ?? porDeclarado;
  const de = [...new Set(puntos[mat].map((p) => nombreFuente(p.r.fuente)))].join(", ");
  detalle[mat] = porRegresion
    ? `${puntos[mat].length} tubo${puntos[mat].length === 1 ? "" : "s"} de PE ${mat} con precio por metro${de ? ` (${de})` : ""}`
    : porDeclarado ? `${sueltos[mat].length} precios por kilo` : null;
}
// Un material sin puntos propios toma el del otro (el PE 100 es la resina de referencia).
if (kilo[100] == null && kilo[80] != null) { kilo[100] = kilo[80]; detalle[100] = `${detalle[80]} de PE 80`; }
if (kilo[80] == null && kilo[100] != null) { kilo[80] = kilo[100]; detalle[80] = `${detalle[100]} de PE 100`; }
if (kilo[100] == null) { console.error("las referencias no traen ni un tubo con precio por metro ni un precio por kilo"); process.exit(2); }

// Dispersión del ajuste: si es enorme, el kilo no representa a la familia y hay que mirarlo.
for (const mat of [80, 100]) {
  const ps = puntos[mat];
  if (ps.length < 2) continue;
  const err = ps.map((p) => Math.abs(p.precio - kilo[mat] * p.kg) / p.precio);
  console.log(`  PE ${mat}: kilo S/ ${kilo[mat].toFixed(2)} · ${ps.length} puntos · error mediano ${(mediana(err) * 100).toFixed(0)} % · máx ${(Math.max(...err) * 100).toFixed(0)} %`);
}
const fuentes = [...new Set(refs.filter((r) => r.fuente).map((r) => String(r.fuente).split(" (")[0].split(" -")[0].trim()))].slice(0, 4).join(", ");

// ── Aplicar a los 179 ───────────────────────────────────────────────────────────────────────
const ofi = JSON.parse(readFileSync(F_PRE, "utf8"));
const conPrecio = new Map(ofi.ciudades[0].precios.map((p) => [p.idCanonico, p.precio]));
const objetivo = ofi.ciudades[0].precios.filter((p) => !(p.precio > 0) && geometria(p.nombre));
const sinGeo = ofi.ciudades[0].precios.filter((p) => !(p.precio > 0) && !geometria(p.nombre));
console.log(`\nsin precio: ${objetivo.length + sinGeo.length} · con geometría legible: ${objetivo.length} · sin geometría: ${sinGeo.length}`);
if (sinGeo.length) for (const p of sinGeo.slice(0, 10)) console.log(`   queda en 0: ${p.idCanonico} «${p.nombre}»`);

const nuevo = new Map();
for (const p of objetivo) {
  const g = geometria(p.nombre);
  const precio = Math.round(g.kgPorM * kilo[g.material] * 100) / 100;
  nuevo.set(p.idCanonico, {
    precio,
    nota: `TENTATIVO (calculado, no relevado): D=${g.D} mm con SDR ${g.SDR} → pared ${g.e.toFixed(1)} mm → ${g.kgPorM.toFixed(3)} kg/m × S/ ${kilo[g.material].toFixed(2)} el kilo de tubo PE ${g.material}, calibrado con ${detalle[g.material]} del mercado peruano. Las fuentes no declaran IGV: el precio va como lo publican, igual que el resto de la lista. Revisar antes de usarlo en una oferta.`,
  });
}
let tocados = 0;
for (const c of ofi.ciudades) {
  for (const p of c.precios) {
    const n = nuevo.get(p.idCanonico);
    if (!n || p.precio > 0) continue;
    p.precio = n.precio; p.nota = n.nota; tocados++;
  }
}
ofi.version = VERSION;
ofi.fuente = `${ofi.fuente ?? ""} + tubería HDPE calculada por masa lineal (2-sep-2026): pared = D/SDR, masa = π·e·(D−e)·ρ, precio = masa × kilo de tubo calibrado con precios reales del mercado peruano (${fuentes}). Los HDPE llevan nota TENTATIVO.`.trim();

const muestra = ["20", "63", "110", "160", "250", "400", "630"];
console.log(`\nmuestra (PE 100, SDR 11):`);
for (const d of muestra) {
  const p = objetivo.find((x) => new RegExp(`D=${d}mm SDR 11 `).test(x.nombre) && /PE 100/.test(x.nombre));
  if (p) { const g = geometria(p.nombre); console.log(`   D=${String(g.D).padStart(3)} mm · pared ${g.e.toFixed(1)} mm · ${g.kgPorM.toFixed(2)} kg/m → S/ ${nuevo.get(p.idCanonico).precio.toFixed(2)}/m`); }
}
if (DRY) { console.log("\n(--dry: no se escribió nada)"); process.exit(0); }
writeFileSync(F_PRE, JSON.stringify(ofi, null, 2) + "\n");
console.log(`\n✓ oficiales_PE.json: ${nuevo.size} insumos con precio tentativo × ${ofi.ciudades.length} ciudades (${tocados} celdas) · versión ${VERSION}`);
