import { readFileSync, writeFileSync } from "node:fs";

const KT = "C:/Users/Equipo/AndroidStudioProjects/ArqOn-app/composeApp/src/main/java/com/example/myapplicationpresuspuestosobras/data/db/AppDatabase.kt";
const txt = readFileSync(KT, "utf8");

// Insumo(nombre = "...", codigo = "...", unidad = "...", tipoInsumo = TipoInsumo.X, categoria = "...")
const re = /Insumo\(\s*nombre\s*=\s*"((?:[^"\\]|\\.)*)"\s*,\s*codigo\s*=\s*"([^"]*)"\s*,\s*unidad\s*=\s*"([^"]*)"\s*,\s*tipoInsumo\s*=\s*TipoInsumo\.(\w+)\s*,\s*categoria\s*=\s*"([^"]*)"/g;

let m;
const seed = [];
while ((m = re.exec(txt))) {
  seed.push({ nombre: m[1].replace(/\\"/g, '"'), codigo: m[2], unidad: m[3], tipoInsumo: m[4], categoria: m[5] });
}
console.log("seed extraído:", seed.length);
const tipos = {};
seed.forEach((s) => (tipos[s.tipoInsumo] = (tipos[s.tipoInsumo] || 0) + 1));
console.log("por tipo:", tipos);
writeFileSync("C:/Users/Equipo/_datos_app_work/tools/_seed_apk.json", JSON.stringify(seed, null, 2));
console.log("MO/EQ del seed:");
seed.filter((s) => s.tipoInsumo !== "MATERIAL").forEach((s) => console.log("  " + s.codigo + " " + s.nombre + " [" + s.categoria + "]"));
