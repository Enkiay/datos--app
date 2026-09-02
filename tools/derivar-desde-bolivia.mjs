#!/usr/bin/env node
// DERIVAR LA BASE DE UN PAÍS DESDE LA DE BOLIVIA (2-sep-2026, pedido de Oscar: «nuevas y
// limpias, todas basadas en la BD de Bolivia, solo que con precio de cada país»).
//
// Produce, para el país pedido:
//   precios/v1.0/oficiales_XX.json → TODOS los insumos de Bolivia (751) bajo el espacio del
//       país (`xx_<idBoliviano>`), en TODAS las ciudades de la caja. Cada precio dice en su
//       nota de dónde salió, en este orden de preferencia:
//         · RELEVADO: precio del país ya publicado (tabla `equivalentes`/`familias`).
//         · REFERENCIA: precio leído en una fuente concreta (precios/fuentes/referencias_XX.json:
//           idBo, precio en la unidad boliviana, fuente, url, fecha, conversión).
//         · ESTIMADO: precio boliviano × la relación mediana precio_XX/precio_BO medida en los
//           insumos que tienen precio en los dos lados, por tipo (material / M.O. / equipo).
//           Oscar, 2-sep-2026: «para aquellos que no encuentres, completar por relación».
//           La nota lo dice con el factor y pide revisar. `--sin-estimar` lo apaga.
//         · PENDIENTE (0): sólo si no hay ni un par para medir la relación.
//       Al regenerar, sólo los RELEVADOS cuentan como precio del país (COPIADO/ESTIMADO se
//       recalculan): el generador es idempotente y las referencias viven en su propio archivo.
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
const ESTIMAR = !process.argv.includes("--sin-estimar");
// Unidades comparables: «Hr» = «h», «m²» = «m2», sin espacios ni puntos.
const u = (s) => String(s ?? "").toLowerCase().replace(/[\s.]/g, "").replace("²", "2").replace("³", "3").replace(/^(hr|hora)$/, "h");
// Un precio estimado se redondea a la precisión que se cotiza: entero si pasa de 100.
const redondear = (v) => (v >= 100 ? Math.round(v) : Math.round(v * 100) / 100);
const mediana = (a) => { const s = [...a].sort((x, y) => x - y); return s.length ? (s.length % 2 ? s[(s.length - 1) / 2] : (s[s.length / 2 - 1] + s[s.length / 2]) / 2) : null; };

// ── LA TABLA DEL PAÍS: qué insumo boliviano ya tiene precio relevado, y con qué id ──────────
// `equivalentes`: id boliviano → id YA publicado del país (conserva el id y el precio por ciudad).
// `familias`: id boliviano → id del país cuyo precio HEREDA (misma familia de producto o mismo
// escalafón). Se declara acá, insumo por insumo, para que la decisión quede escrita.
const CONFIG = {
  PY: {
    version: "v20260902-referencias-capaco-neto",
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
    version: "v20260902-referencias-sodimac",
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
    version: "v20260902-referencias-ucc-neto",
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
  EC: {
    version: "v20260902-base-bolivia",
    fuente: "Base boliviana (catálogo ArqOn) + precios de Ecuador: Contraloría General del Estado (salarios mínimos por ley 2026, hora real con cargas: la caja lleva cargasSociales = 0) y precios de referencia de mercado de Quito 2026. Relevado en Quito; las otras 6 ciudades COPIAN Quito (referencial) hasta relevarse. La cadena ecuatoriana agrega el IVA (15 %) al final: los insumos van sin IVA.",
    // El cemento ecuatoriano se vende por SACO de 50 kg y el boliviano por kg: no es equivalente,
    // entra como REFERENCIA convertida (referencias_EC.json). Lo mismo con galones y tubos.
    equivalentes: {
      fierro_corrugado_kg: "ec_mat_acero", alambre_de_amarre_kg: "ec_mat_alambre", arena_comun_m3: "ec_mat_arena", arena_fina_m3: "ec_mat_arena_fina",
      grava_comun_m3: "ec_mat_ripio", piedra_bruta_m3: "ec_mat_piedra", clavos_kg: "ec_mat_clavos", bloque_de_hormigon_3h_e_15_cm_pza: "ec_mat_bloque15",
      ladrillo_gambote_pza: "ec_mat_ladrillo", ceramica_esmaltada_30_30_m2: "ec_mat_ceramica", porcelanato_m2: "ec_mat_porcelanato",
      inodoro_blanco_tanq_bajo_con_acc_pza: "ec_mat_inodoro", lavamanos_blanco_con_acc_pza: "ec_mat_lavamanos", teflon_pza: "ec_mat_teflon",
      electrodos_kg: "ec_mat_electrodo", cable_thw_12_awg_m: "ec_mat_cable12", interruptor_simple_pza: "ec_mat_interruptor",
      tomacorriente_doble_pza: "ec_mat_tomacorriente", lija_hoja: "ec_mat_lija", bisagra_3_doble_pza: "ec_mat_bisagra",
      interruptor_termico_2x30_amp_pza: "ec_mat_breaker", foco_led_14_w_pza: "ec_mat_foco", tablero_de_distribucion_6_circuitos_pza: "ec_mat_tablero",
      eq_mezcladora: "ec_eq_concretera", eq_vibradora: "ec_eq_vibrador", eq_retroexcavadora: "ec_eq_retro", eq_volqueta_6_m3: "ec_eq_volqueta",
      eq_compactadora_manual_de_impacto: "ec_eq_compactadora",
      // Contraloría: categorías por estructura ocupacional. D2 (albañil, carpintero, fierrero,
      // electricista, plomero, pintor) = 4,39; C1 (maestro mayor, operador) = 4,87; E2 (peón) = 4,34.
      mo_albanil: "ec_mo_albanil", mo_carpintero: "ec_mo_carpintero", mo_electricista: "ec_mo_electricista", mo_armador: "ec_mo_fierrero",
      mo_ayudante: "ec_mo_peon", mo_pintor: "ec_mo_pintor", mo_plomero: "ec_mo_plomero", mo_operador_de_retroexcavadora: "ec_mo_operador",
      mo_especialista: "ec_mo_maestro",
    },
    familias: {
      arena_lavada_m3: "ec_mat_arena", grava_lavada_m3: "ec_mat_ripio", grava_clasificada_m3: "ec_mat_ripio", piedra_para_cimiento_m3: "ec_mat_piedra",
      ladrillo_adobito_de_1ra_pza: "ec_mat_ladrillo", ladrillo_gambote_18h_25x12x6_5_cm_pza: "ec_mat_ladrillo",
      ceramica_esmaltada_brasil_m2: "ec_mat_ceramica", ceramica_esmaltada_nal_20x30cm_m2: "ec_mat_ceramica", baldosa_ceramica_esmaltada_m2: "ec_mat_ceramica",
      baldosa_ceramica_esmalt_11x23_cm_m2: "ec_mat_ceramica", revestimiento_ceramico_nacional_m2: "ec_mat_ceramica",
      ceramica_nacional_22_34_cm_m2: "ec_mat_ceramica", ceramica_nacional_25_25_cm_m2: "ec_mat_ceramica", ceramica_nacional_34_34_cm_m2: "ec_mat_ceramica", ceramica_nacional_40_40_cm_m2: "ec_mat_ceramica",
      lija_para_cubierta_hoja: "ec_mat_lija", lija_para_madera_hoja: "ec_mat_lija", lija_para_pared_hoja: "ec_mat_lija",
      interruptor_termico_2x40_amp_pza: "ec_mat_breaker",
      mezcladora_de_hormigon_320_litros_hr: "ec_eq_concretera", vibradora_de_2_hp_hr: "ec_eq_vibrador", retroexcavadora_110_hp_hr: "ec_eq_retro",
      mo_encofrador: "ec_mo_carpintero", mo_carpintero_en_aluminio: "ec_mo_carpintero",
      mo_especialista_calificado: "ec_mo_albanil", mo_especialista_plomero: "ec_mo_plomero", mo_especialista_cerrajero: "ec_mo_albanil",
      mo_especialista_en_tesado_e_inyeccion: "ec_mo_albanil", mo_tecnico_especialista: "ec_mo_albanil", mo_tecnico_especialista_certificado: "ec_mo_albanil",
      mo_tecnico_especialista_juntas: "ec_mo_albanil", mo_plomero_certificado: "ec_mo_plomero", mo_cerrajero: "ec_mo_albanil", mo_perforista: "ec_mo_albanil",
      mo_operador_de_compactadora: "ec_mo_operador", mo_operador_de_mezcladora: "ec_mo_operador", mo_operador_de_volqueta: "ec_mo_operador",
    },
  },
  CO: {
    version: "v20260902-base-bolivia",
    fuente: "Base boliviana (catálogo ArqOn) + precios de Colombia: precios de referencia de mercado de Bogotá 2026 y jornales con factor prestacional incluido (la caja lleva cargasSociales = 0). Relevado en Bogotá; las otras 7 ciudades COPIAN Bogotá (referencial) hasta relevarse. La cadena colombiana agrega el IVA (19 %) al final: los insumos van sin IVA.",
    // Cemento por BULTO de 50 kg, pintura por galón, tubería por tubo: entran como REFERENCIA
    // convertida (referencias_CO.json), no como equivalentes.
    equivalentes: {
      fierro_corrugado_kg: "co_mat_acero", alambre_de_amarre_kg: "co_mat_alambre", arena_comun_m3: "co_mat_arena", arena_fina_m3: "co_mat_arena_pena",
      grava_comun_m3: "co_mat_triturado", clavos_kg: "co_mat_puntilla", ladrillo_gambote_pza: "co_mat_tolete", ceramica_esmaltada_30_30_m2: "co_mat_ceramica",
      inodoro_blanco_tanq_bajo_con_acc_pza: "co_mat_sanitario", lavamanos_blanco_con_acc_pza: "co_mat_lavamanos", teflon_pza: "co_mat_teflon",
      cable_thw_12_awg_m: "co_mat_cable12", interruptor_simple_pza: "co_mat_interruptor", tomacorriente_doble_pza: "co_mat_toma", lija_hoja: "co_mat_lija",
      interruptor_termico_2x30_amp_pza: "co_mat_breaker", foco_led_14_w_pza: "co_mat_bombillo", tablero_de_distribucion_6_circuitos_pza: "co_mat_tablero",
      eq_mezcladora: "co_eq_mezcladora", eq_vibradora: "co_eq_vibrador", eq_retroexcavadora: "co_eq_retro", eq_compactadora_manual_salt: "co_eq_compactador",
      // Jornales con prestaciones adentro: ayudante 9.500, oficial 11.900, oficiales especializados
      // 13.000, operador 14.500, maestro 16.650.
      mo_ayudante: "co_mo_ayudante", mo_albanil: "co_mo_oficial", mo_electricista: "co_mo_electricista", mo_plomero: "co_mo_plomero",
      mo_pintor: "co_mo_pintor", mo_especialista: "co_mo_maestro", mo_operador_de_retroexcavadora: "co_mo_operador",
    },
    familias: {
      arena_lavada_m3: "co_mat_arena", grava_lavada_m3: "co_mat_triturado", grava_clasificada_m3: "co_mat_triturado",
      ladrillo_adobito_de_1ra_pza: "co_mat_tolete", ladrillo_gambote_18h_25x12x6_5_cm_pza: "co_mat_tolete",
      ceramica_esmaltada_brasil_m2: "co_mat_ceramica", ceramica_esmaltada_nal_20x30cm_m2: "co_mat_ceramica", baldosa_ceramica_esmaltada_m2: "co_mat_ceramica",
      baldosa_ceramica_esmalt_11x23_cm_m2: "co_mat_ceramica", revestimiento_ceramico_nacional_m2: "co_mat_ceramica",
      ceramica_nacional_22_34_cm_m2: "co_mat_ceramica", ceramica_nacional_25_25_cm_m2: "co_mat_ceramica", ceramica_nacional_34_34_cm_m2: "co_mat_ceramica", ceramica_nacional_40_40_cm_m2: "co_mat_ceramica",
      lija_para_cubierta_hoja: "co_mat_lija", lija_para_madera_hoja: "co_mat_lija", lija_para_pared_hoja: "co_mat_lija",
      interruptor_termico_2x40_amp_pza: "co_mat_breaker",
      mezcladora_de_hormigon_320_litros_hr: "co_eq_mezcladora", vibradora_de_2_hp_hr: "co_eq_vibrador", retroexcavadora_110_hp_hr: "co_eq_retro",
      mo_carpintero: "co_mo_oficial", mo_encofrador: "co_mo_oficial", mo_armador: "co_mo_oficial", mo_carpintero_en_aluminio: "co_mo_oficial",
      mo_especialista_calificado: "co_mo_oficial", mo_especialista_cerrajero: "co_mo_oficial", mo_especialista_en_tesado_e_inyeccion: "co_mo_oficial",
      mo_cerrajero: "co_mo_oficial", mo_perforista: "co_mo_oficial",
      mo_especialista_plomero: "co_mo_plomero", mo_plomero_certificado: "co_mo_plomero",
      mo_tecnico_especialista: "co_mo_electricista", mo_tecnico_especialista_certificado: "co_mo_electricista", mo_tecnico_especialista_juntas: "co_mo_electricista",
      mo_operador_de_compactadora: "co_mo_operador", mo_operador_de_mezcladora: "co_mo_operador", mo_operador_de_volqueta: "co_mo_operador",
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
// LOS RELEVADOS viven en precios/fuentes/relevados_XX.json (la lista del país tal como se
// relevó, con sus ciudades): es la fuente de verdad y no se sobreescribe. Si no existe todavía,
// la primera corrida toma el oficiales_XX.json vigente — y conviene guardarlo ahí antes, porque
// después de derivar sólo sobreviven los ids declarados como equivalentes.
const relevadosPath = `precios/fuentes/relevados_${PAIS}.json`;
const ofiPaisViejo = existsSync(join(BASE, relevadosPath)) ? leer(relevadosPath)
  : existsSync(join(BASE, `precios/v1.0/oficiales_${PAIS}.json`)) ? leer(`precios/v1.0/oficiales_${PAIS}.json`) : null;
if (!ofiPaisViejo?.ciudades?.length) { console.error(`falta ${relevadosPath} (o oficiales_${PAIS}.json) con las ciudades y los precios relevados`); process.exit(2); }
if (!existsSync(join(BASE, relevadosPath))) console.warn(`  aviso: no existe ${relevadosPath}; guardá ahí la lista relevada antes de regenerar`);

// El insumo maestro: la primera ciudad boliviana trae los 751 con nombre/unidad/tipo/categoría.
const maestro = ofiBO.ciudades[0].precios;
const idPais = (idBo) => cfg.equivalentes[idBo] ?? `${iso}_${idBo}`;
const codigoPais = (idBo, codBo) => cfg.equivalentes[idBo] ? cfg.equivalentes[idBo].toUpperCase() : `${PAIS}_${codBo}`;

// Un precio del archivo del país cuenta como RELEVADO sólo si es real: lo copiado de otra
// ciudad, lo estimado y lo pendiente se recalculan en cada corrida (idempotencia).
const relevado = (p) => !!p && p.precio > 0 && !/^(COPIADO|ESTIMADO|PENDIENTE)/.test(p.nota ?? "");
// Precio relevado del país para un id boliviano, en una ciudad dada (null si no hay).
function precioEn(ciudadPais, idBo) {
  const ref = cfg.equivalentes[idBo] ?? cfg.familias[idBo];
  if (!ref) return null;
  const p = ciudadPais.precios.find((x) => x.idCanonico === ref);
  return relevado(p) ? p : null;
}

// ── REFERENCIAS: precios leídos en una fuente concreta (precios/fuentes/referencias_XX.json) ─
// Valen para la ciudad de referencia, en la unidad boliviana; el resto de las ciudades los copia.
// La primera entrada de cada idBo manda (el archivo viene ordenado por confianza).
const refPath = `precios/fuentes/referencias_${PAIS}.json`;
const referencias = new Map();
if (existsSync(join(BASE, refPath))) {
  for (const r of leer(refPath)) {
    const m = maestro.find((x) => x.idCanonico === r.idBo);
    if (!m) { console.warn(`  referencia ignorada: «${r.idBo}» no es un insumo boliviano`); continue; }
    if (!(r.precio > 0)) continue;
    if (u(m.unidad) !== u(r.unidad)) { console.warn(`  referencia ignorada: ${r.idBo} viene en «${r.unidad}» y el insumo es «${m.unidad}»`); continue; }
    if (!referencias.has(r.idBo)) referencias.set(r.idBo, r);
  }
}

// ── oficiales_XX: las ciudades del país, con los 751 insumos cada una ──────────────────────
// TODAS las ciudades de la caja salen SERVIDAS (Oscar, 2-sep-2026: «habilita todas las
// ciudades, con precios copiados»): una ciudad sin relevamiento propio copia los precios de la
// ciudad de REFERENCIA (la primera que tenga precios relevados), y cada precio copiado lo dice
// en su nota. Es lo que ya hacía Paraguay con los materiales fuera de la lista de ANDE.
const servida = (c) => c.precios.some(relevado);
const ciudadRef = ofiPaisViejo.ciudades.find(servida);
if (!ciudadRef) { console.error("ninguna ciudad tiene un solo precio relevado: no hay de dónde copiar"); process.exit(2); }

// ── La RELACIÓN con Bolivia, medida: precio_XX / precio_BO en los insumos con precio en los dos
// lados (relevados + referencias), misma unidad, mediana por tipo. Un tipo sin pares (equipo,
// casi siempre) toma la relación de los materiales y la nota lo dice.
const pares = { MATERIAL: [], MANO_DE_OBRA: [], HERRAMIENTA: [] };
for (const m of maestro) {
  const rel = precioEn(ciudadRef, m.idCanonico);
  const precio = rel ? rel.precio : referencias.get(m.idCanonico)?.precio;
  if (!(precio > 0) || !(m.precio > 0)) continue;
  if (rel && u(rel.unidad) !== u(m.unidad)) continue;
  pares[m.tipoInsumo]?.push(precio / m.precio);
}
// Con menos de MIN_PARES un tipo no tiene relación propia (una sola volqueta no hace mediana).
const MIN_PARES = 3;
const k = {};
for (const t of Object.keys(pares)) k[t] = pares[t].length >= MIN_PARES ? mediana(pares[t]) : null;
if (k.MATERIAL == null) k.MATERIAL = mediana(pares.MATERIAL);
for (const t of Object.keys(k)) if (k[t] == null) k[t] = k.MATERIAL;
const kNota = (t) => pares[t].length >= MIN_PARES
  ? `mediana de ${pares[t].length} pares de ${t.toLowerCase().replace(/_/g, " ")}`
  : `${pares[t].length} pares de ${t.toLowerCase().replace(/_/g, " ")}, insuficientes: usa la relación de los materiales`;

const origen = { RELEVADO: 0, REFERENCIA: 0, ESTIMADO: 0, PENDIENTE: 0 };
const ciudades = ofiPaisViejo.ciudades.map((c) => ({
  nombre: c.nombre,
  precios: maestro.map((m) => {
    const esRef = c === ciudadRef;
    const cuenta = (o) => { if (esRef) origen[o]++; };
    const copia = (nota) => (esRef ? nota : `COPIADO de ${ciudadRef.nombre} (referencial, sin relevar en ${c.nombre}). ${nota}`.trim());
    const propio = precioEn(c, m.idCanonico);
    const rel = propio ?? precioEn(ciudadRef, m.idCanonico);
    const viejo = (propio ? c : ciudadRef).precios.find((x) => x.idCanonico === cfg.equivalentes[m.idCanonico]);
    const base = {
      idCanonico: idPais(m.idCanonico), nombre: viejo?.nombre ?? m.nombre, categoria: m.categoria,
      unidad: viejo?.unidad ?? m.unidad, tipoInsumo: m.tipoInsumo, codigo: codigoPais(m.idCanonico, m.codigo),
    };
    if (rel) {
      cuenta("RELEVADO");
      const notaBase = viejo ? (viejo.nota ?? "") : `Precio heredado de «${rel.nombre}» (misma familia / mismo escalafón)`;
      return { ...base, precio: rel.precio, nota: propio ? notaBase : copia(notaBase) };
    }
    const r = referencias.get(m.idCanonico);
    if (r) {
      cuenta("REFERENCIA");
      const nota = `REFERENCIA: ${r.fuente}${r.fecha ? ` (${r.fecha})` : ""}${r.conversion ? `; ${r.conversion}` : ""}${r.nota ? `; ${r.nota}` : ""}${r.url ? ` · ${r.url}` : ""}`;
      return { ...base, precio: r.precio, nota: copia(nota) };
    }
    if (ESTIMAR && k[m.tipoInsumo] != null && m.precio > 0) {
      cuenta("ESTIMADO");
      const f = k[m.tipoInsumo];
      return {
        ...base, precio: redondear(m.precio * f),
        nota: `ESTIMADO por relación con Bolivia: ${m.precio} Bs × ${f.toFixed(2)} (${kNota(m.tipoInsumo)}). Sin referencia relevada en ${PAIS}; revisar antes de usarlo en una oferta.`,
      };
    }
    cuenta("PENDIENTE");
    return { ...base, precio: 0, nota: `PENDIENTE: sin precio relevado en ${PAIS}. Insumo heredado de la base boliviana (${m.idCanonico}); cargalo a mano o esperá la próxima publicación.` };
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
  nota: `Base de ${PAIS} DERIVADA de la boliviana (2-sep-2026): los ${maestro.length} insumos de Bolivia bajo el espacio ${iso}_, en las ${ciudades.length} ciudades de la caja. Cada precio dice en su nota de dónde salió — en ${ciudadRef.nombre}: ${origen.RELEVADO} RELEVADOS, ${origen.REFERENCIA} por REFERENCIA (fuente citada), ${origen.ESTIMADO} ESTIMADOS por relación con Bolivia (material ×${k.MATERIAL?.toFixed(2)}, M.O. ×${k.MANO_DE_OBRA?.toFixed(2)}, equipo ×${k.HERRAMIENTA?.toFixed(2)}; revisar antes de ofertar), ${origen.PENDIENTE} PENDIENTES en 0. Las otras ciudades copian ${ciudadRef.nombre} hasta relevarse. Ítems publicados: los que cierran con precio completo (${items.length} de ${itemsBO.items.length}). Regenerar con tools/derivar-desde-bolivia.mjs al entrar precios nuevos (precios/fuentes/referencias_${PAIS}.json).`,
  origenPrecios: { ciudadReferencia: ciudadRef.nombre, ...origen, relacionConBolivia: k, paresMedidos: Object.fromEntries(Object.entries(pares).map(([t, a]) => [t, a.length])) },
  precios: [],
  ciudades,
};
writeFileSync(join(BASE, `catalogo/v1.0/items_${PAIS}.json`), JSON.stringify(salidaItems, null, 2) + "\n");
writeFileSync(join(BASE, `precios/v1.0/oficiales_${PAIS}.json`), JSON.stringify(salidaPrecios, null, 2) + "\n");

const top = [...bloqueo.entries()].sort((a, b) => b[1] - a[1]).slice(0, 15);
console.log(`✓ ${PAIS}: ${items.length}/${itemsBO.items.length} ítems con precio completo · ${maestro.length} insumos × ${ciudades.length} ciudades · pendientes por ciudad: ${zerosPorCiudad} (poner ese TOPE en estado-de-las-bases.test.ts)`);
console.log(`  origen en ${ciudadRef.nombre}: ${origen.RELEVADO} relevados · ${origen.REFERENCIA} referencias · ${origen.ESTIMADO} estimados · ${origen.PENDIENTE} pendientes`);
console.log(`  relación con Bolivia: material ×${k.MATERIAL?.toFixed(2)} (${pares.MATERIAL.length} pares) · M.O. ×${k.MANO_DE_OBRA?.toFixed(2)} (${pares.MANO_DE_OBRA.length}) · equipo ×${k.HERRAMIENTA?.toFixed(2)} (${pares.HERRAMIENTA.length})`);
if (top.length) { console.log("  los que más destraban al relevarlos:"); for (const [id, n] of top) console.log(`    ${String(n).padStart(3)}  ${id}`); }
