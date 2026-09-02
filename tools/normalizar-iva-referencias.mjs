#!/usr/bin/env node
// REFERENCIAS A NETO (2-sep-2026). Las cadenas de PY, CL y AR agregan el IVA al FINAL (10 / 19 /
// 21 % sobre el neto: `impuestoPct` de la caja), así que los precios de los insumos tienen que
// ir SIN IVA. Una referencia de mostrador «con IVA» (CAPACO «IVA incluido», Sodimac, Easy,
// Ferretería Gay…) hay que dividirla por (1 + IVA) antes de usarla; si no, el IVA se cobra dos
// veces. Las que dicen «neto» o «sin IVA» se dejan; las que no dicen nada tampoco se tocan (no se
// inventa). Idempotente: marca `ivaNormalizado` y no vuelve a dividir.
//
// Uso:  node tools/normalizar-iva-referencias.mjs <ISO>
import { readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const BASE = join(dirname(fileURLToPath(import.meta.url)), "..");
const PAIS = (process.argv[2] || "").toUpperCase();
const IVA = { PY: 10, CL: 19, AR: 21 }[PAIS];
if (!IVA) { console.error("uso: node tools/normalizar-iva-referencias.mjs PY|CL|AR"); process.exit(2); }

const ruta = join(BASE, `precios/fuentes/referencias_${PAIS}.json`);
const refs = JSON.parse(readFileSync(ruta, "utf8"));
const texto = (r) => `${r.nota ?? ""} ${r.fuente ?? ""} ${r.conversion ?? ""}`.toLowerCase();
const conIva = (t) => /con iva|iva incl|incluye iva|incluido el iva|iva \d\d ?%|precio mostrador/.test(t);
const neto = (t) => /sin iva|neto|\+ ?iva|más iva|mas iva/.test(t);
// La mano de obra no lleva IVA (sueldos): nunca se divide.
const f = 1 + IVA / 100;
let n = 0, ya = 0, dudosos = 0;
for (const r of refs) {
  if (r.ivaNormalizado) { ya++; continue; }
  const t = texto(r);
  if (/^mo_/.test(r.idBo)) continue;
  if (conIva(t) && !neto(t)) {
    const antes = r.precio;
    r.precio = Math.round((antes / f) * 100) / 100;
    r.conversion = `${r.conversion ? r.conversion + "; " : ""}${antes} con IVA ÷ ${f.toFixed(2)} = ${r.precio} NETO (la cadena ${PAIS} agrega el IVA ${IVA} % al final)`;
    r.ivaNormalizado = true;
    n++;
  } else if (conIva(t) && neto(t)) {
    dudosos++;
  }
}
writeFileSync(ruta, JSON.stringify(refs, null, 1) + "\n");
console.log(`✓ ${PAIS}: ${n} referencias pasadas a neto (÷${f.toFixed(2)}) · ${ya} ya estaban · ${dudosos} mencionan las dos cosas (se dejaron) · ${refs.length} total`);
