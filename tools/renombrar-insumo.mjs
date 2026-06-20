/**
 * RENOMBRAR INSUMO (seguro, sin huerfanos).
 *
 * Cambia SOLO el `nombre` visible de un insumo, conservando su `idCanonico` (la
 * clave inmutable que enlaza los items). Actualiza el nombre en las 3 fuentes a
 * la vez para no violar la regla 3 del validador (nombre consistente por id):
 *   - precios/v1.0/oficiales.json   (las 9 ciudades)
 *   - catalogo/v1.0/items.json      (insumo embebido en cada item que lo usa)
 *   - catalogo/v1.0/items_BO.json   (idem)
 *
 * Como NO toca el idCanonico, ningun item queda huerfano y la app, al
 * sincronizar, hace match por idCanonico y adopta el nombre nuevo.
 *
 * Uso:
 *   node tools/renombrar-insumo.mjs <idCanonico> "<Nombre nuevo>"            (dry-run)
 *   node tools/renombrar-insumo.mjs <idCanonico> "<Nombre nuevo>" --apply    (escribe)
 *
 * Despues de --apply, corre:  node scripts/validar-catalogo.mjs
 */
import { readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

const DIR = fileURLToPath(new URL("../", import.meta.url));
const F_OFI = DIR + "precios/v1.0/oficiales.json";
const F_ITEMS = DIR + "catalogo/v1.0/items.json";
const F_ITEMS_BO = DIR + "catalogo/v1.0/items_BO.json";

const args = process.argv.slice(2).filter((a) => a !== "--apply");
const APLICAR = process.argv.includes("--apply");
const [idCanonico, nombreNuevo] = args;

if (!idCanonico || !nombreNuevo) {
  console.error('Uso: node tools/renombrar-insumo.mjs <idCanonico> "<Nombre nuevo>" [--apply]');
  process.exit(2);
}

const norm = (s) => (s || "").trim();
const ID = norm(idCanonico);

const ofi = JSON.parse(readFileSync(F_OFI, "utf8"));
const items = JSON.parse(readFileSync(F_ITEMS, "utf8"));
const itemsBO = JSON.parse(readFileSync(F_ITEMS_BO, "utf8"));

let enOfi = 0, enItems = 0, enItemsBO = 0, nombreViejo = null, unidad = null;

for (const c of ofi.ciudades || []) {
  for (const p of c.precios || []) {
    if (norm(p.idCanonico) === ID) {
      nombreViejo ??= p.nombre; unidad ??= p.unidad;
      if (p.nombre !== nombreNuevo) { p.nombre = nombreNuevo; enOfi++; }
    }
  }
}
for (const [src, tag] of [[items, "items"], [itemsBO, "items_BO"]]) {
  for (const it of src.items || []) {
    for (const ins of it.insumos || []) {
      if (norm(ins.idCanonico) === ID) {
        nombreViejo ??= ins.nombre; unidad ??= ins.unidad;
        if (ins.nombre !== nombreNuevo) {
          ins.nombre = nombreNuevo;
          if (tag === "items") enItems++; else enItemsBO++;
        }
      }
    }
  }
}

if (nombreViejo === null) {
  console.error(`✗ No existe ningun insumo con idCanonico = "${ID}". Nada que renombrar.`);
  process.exit(1);
}

console.log("=== RENOMBRAR INSUMO ===");
console.log("idCanonico (intacto):", ID, "| unidad:", unidad);
console.log(`nombre:  "${nombreViejo}"  ->  "${nombreNuevo}"`);
console.log(`refs actualizadas: oficiales=${enOfi}  items.json=${enItems}  items_BO.json=${enItemsBO}`);

// Escribe con CRLF + indent 2 + trailing CRLF (= convencion del repo / normalizador).
function escribir(path, obj) {
  writeFileSync(path, JSON.stringify(obj, null, 2).replace(/\n/g, "\r\n") + "\r\n", "utf8");
}
if (APLICAR) {
  escribir(F_OFI, ofi);
  escribir(F_ITEMS, items);
  escribir(F_ITEMS_BO, itemsBO);
  console.log(">>> ARCHIVOS ESCRITOS (--apply). Ahora corre: node scripts/validar-catalogo.mjs");
} else {
  console.log(">>> DRY-RUN (sin escribir). Agrega --apply para aplicar.");
}
